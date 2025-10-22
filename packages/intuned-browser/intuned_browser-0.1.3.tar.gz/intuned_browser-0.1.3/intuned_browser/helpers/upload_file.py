import logging
import os
import re
import uuid
from typing import Any
from typing import Optional
from typing import TYPE_CHECKING
from typing import Union

import aiofiles
import httpx
from botocore.exceptions import NoCredentialsError
from playwright.async_api import Download
from pydantic import BaseModel
from pydantic import Field

from intuned_browser.helpers.types import AttachmentType

if TYPE_CHECKING:
    pass

try:
    from runtime.backend_functions._call_backend_function import call_backend_function
except ImportError:
    call_backend_function = None
    import logging

    logging.warning(
        "Runtime dependencies are not available. Uploading file without S3 credentials will not be available. Install 'intuned-runtime' to enable this feature."
    )

from intuned_browser.helpers.types import Attachment
from intuned_browser.helpers.types import S3Configs
from intuned_browser.helpers.types import SignedUrlAttachment
from intuned_browser.helpers.utils.get_mode import is_generate_code_mode
from intuned_browser.helpers.utils.get_s3_client import get_async_s3_session

logger = logging.getLogger(__name__)


def _normalize_s3_config(configs: Union[S3Configs, dict[str, Any], None]) -> Optional[S3Configs]:
    """
    Convert dict to S3Configs or return None if configs is None.
    Raises TypeError if configs is neither None, dict, nor S3Configs.
    """
    if configs is None:
        return None

    if isinstance(configs, S3Configs):
        return configs

    if isinstance(configs, dict):
        try:
            return S3Configs(**configs)
        except Exception as e:
            raise ValueError("Invalid S3 configuration dict") from e

    raise TypeError(f"configs must be S3Configs, dict, or None. Got: {type(configs)}")


def sanitize_key(key):
    """
    Sanitize a key string by replacing non-alphanumeric characters with underscores
    and consolidating multiple underscores into single underscores.
    Args:
        key (str): The input string to sanitize
    Returns:
        str: Sanitized string
    """
    # Replace any non-alphanumeric chars (except .-_/) with underscore
    result = re.sub(r"[^a-zA-Z0-9.\-_/]", "_", key)
    # Replace multiple underscores with single underscore
    result = re.sub(r"_{2,}", "_", result)
    return result


FileType = Union[Download, bytes]


async def upload_file_to_s3(
    file: FileType,
    *,
    configs: Optional[S3Configs] = None,
    file_name_override: Optional[str] = None,
    content_type: Optional[str] = None,
) -> Attachment:
    """Upload a downloaded file to S3 storage"""
    if not isinstance(file, (Download, bytes)):
        raise ValueError("Invalid file type, Supported types are Download and bytes")
    if configs is None:
        configs = S3Configs()
    configs = _normalize_s3_config(configs)
    bucket_name = (
        configs.bucket_name
        if (configs and configs.bucket_name)
        else (os.environ.get("AWS_BUCKET") or os.environ.get("INTUNED_S3_BUCKET"))
    )
    region = (
        configs.region
        if (configs and configs.region)
        else (os.environ.get("AWS_REGION") or os.environ.get("INTUNED_S3_REGION"))
    )
    endpoint = (
        configs.endpoint
        if (configs and configs.endpoint)
        else (os.environ.get("AWS_ENDPOINT_URL") or os.environ.get("INTUNED_S3_ENDPOINT_URL"))
    )

    is_downloaded_file = isinstance(file, Download)
    if is_generate_code_mode():
        logger.info("Uploaded file successfully")
        if is_downloaded_file:
            return Attachment(
                file_name=f"{str(uuid.uuid4())}/{file.suggested_filename}",
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=file.suggested_filename,
                file_type=AttachmentType.DOCUMENT,
                key=f"{str(uuid.uuid4())}/{file.suggested_filename}",
            )
        else:
            suggested_file_name = str(uuid.uuid4())
            return Attachment(
                file_name=suggested_file_name,
                bucket="testing_bucket",
                region="testing_region",
                endpoint=endpoint,
                suggested_file_name=suggested_file_name,
                file_type=AttachmentType.DOCUMENT,
                key=suggested_file_name,
            )

    suggested_file_name = file.suggested_filename if is_downloaded_file else None
    logger.info(f"suggested_file_name {suggested_file_name}")
    file_name = file_name_override if file_name_override is not None else suggested_file_name or str(uuid.uuid4())

    file_body = await get_file_body(file)

    if region is None or bucket_name is None:
        return await upload_to_intuned(
            name=file_name,
            suggested_name=suggested_file_name,
            body=file_body,
        )

    if is_downloaded_file and not await file.path():
        raise ValueError("File path not found")

    session, endpoint_url = get_async_s3_session(endpoint, configs)

    cleaned_file_name = sanitize_key(file_name)
    key = f"{uuid.uuid4()}/{cleaned_file_name}"
    try:
        async with session.client("s3", endpoint_url=endpoint_url) as s3_client:
            if content_type:
                response = await s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_body,
                    ContentType=content_type,
                )
            else:
                response = await s3_client.put_object(
                    Bucket=bucket_name,
                    Key=key,
                    Body=file_body,
                )

    except NoCredentialsError:
        raise Exception("Credentials not available")  # noqa: B904
    finally:
        if isinstance(file, Download):
            await file.delete()

    if response["ResponseMetadata"]["HTTPStatusCode"] == 200:
        return Attachment(
            file_name=key,
            key=key,
            bucket=bucket_name,
            region=region,
            endpoint=endpoint,
            suggested_file_name=suggested_file_name or "",
            file_type=AttachmentType.DOCUMENT,
        )
    else:
        raise Exception("Error uploading file")


async def get_file_body(file: FileType):
    if isinstance(file, Download):
        file_path = await file.path()
        if not file_path:
            raise ValueError("Downloaded file path not found")
        async with aiofiles.open(file_path, "rb") as f:
            return await f.read()
    elif isinstance(file, bytes):
        return file
    else:
        raise ValueError("Invalid file type")


class GetUploadSignedUrlResponse(BaseModel):
    id: str
    write_signed_url: str = Field(alias="writeSignedUrl")
    read_signed_url: str = Field(alias="readSignedUrl")


async def upload_to_intuned(
    *,
    name: str,
    suggested_name: Optional[str],
    body: bytes,
):
    if call_backend_function is None:
        raise Exception(
            "Runtime dependencies are not available. Uploading file without S3 credentials will not be available."
        )
    response = await call_backend_function(
        name="files/uploadSignedUrls",
        validation_model=GetUploadSignedUrlResponse,
        method="GET",
    )
    async with httpx.AsyncClient() as client:
        put_response = await client.put(
            response.write_signed_url,
            data=body,  # type: ignore
        )
        if not (200 <= put_response.status_code < 300):
            raise Exception(f"Error uploading file: {put_response.status_code} {put_response.text}")
    return SignedUrlAttachment(
        file_name=name,
        download_signed_url=response.read_signed_url,
        suggested_file_name=suggested_name or name,
    )
