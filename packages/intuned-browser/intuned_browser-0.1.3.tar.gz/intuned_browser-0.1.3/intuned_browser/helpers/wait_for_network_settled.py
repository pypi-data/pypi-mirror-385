import asyncio
import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import Optional
from typing import overload

from playwright.async_api import Page
from playwright.async_api import Request

logger = logging.getLogger(__name__)


# Overload 1: Direct call with page only (callable pattern)
@overload
async def wait_for_network_settled(
    page: Page,
    *,
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> None: ...


# Overload 2: Wrapper pattern with page and func
@overload
async def wait_for_network_settled(
    *,
    page: Page,
    func: Callable[[], Awaitable[Any]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Any: ...


# Overload 3: Decorator without arguments
@overload
def wait_for_network_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]: ...


# Overload 4: Decorator factory with arguments
@overload
def wait_for_network_settled(
    *,
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...


def wait_for_network_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Wait for network to settle after performing an action or by itself.

    Usage patterns:
    1. Callable: await wait_for_network_settled(page, timeout_s=30)
    2. Wrapper: await wait_for_network_settled(page=page, func=my_func, timeout_s=30)
    3. Decorator: @wait_for_network_settled or @wait_for_network_settled()
    4. Decorator with options: @wait_for_network_settled(timeout_s=30, max_inflight_requests=0)

    Args:
        page: Playwright Page object
        func: Optional callable to execute before waiting for network to settle
        timeout_s: Maximum time to wait for network to settle (default: 30)
        max_inflight_requests: Maximum number of in-flight requests to consider as settled (default: 0)
    """

    # Case 1a: Direct call with page only (callable pattern - positional)
    # await wait_for_network_settled(page, timeout_s=30, max_inflight_requests=0)
    if len(args) == 1 and isinstance(args[0], Page):
        page = args[0]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)
        return _wait_for_network_settled_core(
            page=page,
            func=None,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 1b: Direct call with page only (callable pattern - keyword)
    # await wait_for_network_settled(page=page, timeout_s=30, max_inflight_requests=0)
    if "page" in kwargs and "func" not in kwargs and len(args) == 0:
        page = kwargs["page"]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)

        if not isinstance(page, Page):
            raise ValueError(
                "No Page object found in function arguments. 'page' parameter must be a Playwright Page object."
            )

        return _wait_for_network_settled_core(
            page=page,
            func=None,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 2: Wrapper pattern with page and func as keyword arguments
    # await wait_for_network_settled(page=page, func=func, timeout_s=30)
    if "page" in kwargs and "func" in kwargs:
        page = kwargs["page"]
        func = kwargs["func"]
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)

        if not isinstance(page, Page):
            raise ValueError(
                "No Page object found in function arguments. 'page' parameter must be a Playwright Page object."
            )

        return _wait_for_network_settled_core(
            page=page,
            func=func,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    # Case 3: Decorator without arguments
    # @wait_for_network_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], Page):
        func = args[0]
        return _create_decorated_function(func, timeout_s=30, max_inflight_requests=0)  # type: ignore

    # Case 4: Decorator factory with arguments (including empty parentheses)
    # @wait_for_network_settled() or @wait_for_network_settled(timeout_s=60, max_inflight_requests=0)
    if len(args) == 0 and "page" not in kwargs and "func" not in kwargs:
        timeout_s = kwargs.get("timeout_s", 30)
        max_inflight_requests = kwargs.get("max_inflight_requests", 0)

        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            return _create_decorated_function(func, timeout_s=timeout_s, max_inflight_requests=max_inflight_requests)

        return decorator

    raise ValueError(
        "Invalid usage. Valid patterns:\n"
        "1. await wait_for_network_settled(page, timeout_s=30) or await wait_for_network_settled(page=page, timeout_s=30)\n"
        "2. await wait_for_network_settled(page=page, func=func, timeout_s=30)\n"
        "3. @wait_for_network_settled or @wait_for_network_settled()\n"
        "4. @wait_for_network_settled(timeout_s=30)"
    )


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    timeout_s: int,
    max_inflight_requests: int,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with network waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the page object in function arguments
        page = next((arg for arg in args if isinstance(arg, Page)), None)
        if page is None:
            page = kwargs.get("page")

        if not page or not isinstance(page, Page):
            logging.error(
                "No Page object found in function arguments. The decorated function must have a 'page' parameter or receive a Page object as an argument."
            )
            raise ValueError(
                "No Page object found in function arguments. The decorated function must have a 'page' parameter or receive a Page object as an argument."
            )

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_network_settled_core(
            page=page,
            func=func_with_args,
            timeout_s=timeout_s,
            max_inflight_requests=max_inflight_requests,
        )

    return wrapper


async def _wait_for_network_settled_core(
    *,
    page: Page,
    func: Optional[Callable[..., Awaitable[Any]]],
    timeout_s: int = 30,
    max_inflight_requests: int = 0,
):
    """Core implementation of network settling logic."""
    if not isinstance(page, Page):
        raise ValueError("No Page object found in function arguments. Page parameter must be a Playwright Page object.")

    logging.debug(f"Page object: {page}")
    network_settled_event = asyncio.Event()
    is_timeout = False
    request_counter = 0
    action_done = False
    pending_requests: set[Request] = set()

    async def maybe_settle():
        if action_done and request_counter <= max_inflight_requests:
            network_settled_event.set()

    def on_request(request: Request):
        nonlocal request_counter
        request_counter += 1
        pending_requests.add(request)
        logging.debug(f"+[{request_counter}]: {request.url}")

    async def on_request_done(request: Request):
        nonlocal request_counter
        # Simulate asynchronous handling
        await asyncio.sleep(0)
        if request in pending_requests:
            request_counter -= 1
            pending_requests.discard(request)
            logging.debug(f"-[{request_counter}]: {request.url}")
            await maybe_settle()

    # Define listener functions to allow proper removal later
    async def handle_request_finished(req: Request):
        await on_request_done(req)

    async def handle_request_failed(req: Request):
        await on_request_done(req)

    # Add listeners
    page.on("request", on_request)
    page.on("requestfinished", handle_request_finished)
    page.on("requestfailed", handle_request_failed)

    async def timeout_task():
        nonlocal is_timeout
        await asyncio.sleep(timeout_s)
        is_timeout = True
        network_settled_event.set()

    try:
        # Execute function if provided, otherwise just wait for network to settle
        result = None
        if func is not None:
            result = await func()
        action_done = True
        await asyncio.sleep(0.5)
        await maybe_settle()
        timeout_task_handle = asyncio.create_task(timeout_task())
        while True:
            await network_settled_event.wait()
            await asyncio.sleep(0.5)
            if (action_done and request_counter <= max_inflight_requests) or is_timeout:
                if is_timeout:
                    logger.debug("Network did not settle within timeout.")
                else:
                    logger.debug("Network settled.")
                break
            else:
                network_settled_event = asyncio.Event()
        return result
    finally:
        # Remove listeners using the same function references
        page.remove_listener("request", on_request)
        page.remove_listener("requestfinished", handle_request_finished)
        page.remove_listener("requestfailed", handle_request_failed)
        try:
            timeout_task_handle.cancel()
        except Exception:
            pass
