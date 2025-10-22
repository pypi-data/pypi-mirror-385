import functools
import logging
from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import overload
from typing import Union

from playwright.async_api import Locator
from playwright.async_api import Page

logger = logging.getLogger(__name__)


# Overload 1: Direct call with source only (callable pattern)
# await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30)
@overload
async def wait_for_dom_settled(
    source: Union[Page, Locator],
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool: ...


# Overload 2: Wrapper pattern with source and func
# await wait_for_dom_settled(source=source, func=func, settle_duration=0.5, timeout_s=30)
@overload
async def wait_for_dom_settled(
    *,
    source: Union[Page, Locator],
    func: Callable[[], Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Any: ...


# Overload 3: Decorator without arguments
# @wait_for_dom_settled
@overload
def wait_for_dom_settled(
    func: Callable[..., Awaitable[Any]],
) -> Callable[..., Awaitable[Any]]: ...


# Overload 4: Decorator factory with arguments
# @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)
@overload
def wait_for_dom_settled(
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> Callable[[Callable[..., Awaitable[Any]]], Callable[..., Awaitable[Any]]]: ...


def wait_for_dom_settled(
    *args: Any,
    **kwargs: Any,
) -> Any:
    """
    Wait for DOM to settle after performing an action or by itself.

    Usage patterns:
    1. Callable: await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30)
    2. Wrapper: await wait_for_dom_settled(source=source, func=my_func, settle_duration=0.5, timeout_s=30)
    3. Decorator: @wait_for_dom_settled or @wait_for_dom_settled()
    4. Decorator with options: @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)

    Args:
        source: Playwright Page or Locator object
        func: Optional callable to execute before waiting for DOM to settle
        settle_duration: Duration in seconds to wait for DOM to stabilize (default: 0.5)
        timeout_s: Maximum time to wait for DOM to settle (default: 30.0)
    """

    # Case 1a: Direct call with source only (callable pattern - positional)
    # await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30)
    if len(args) == 1 and isinstance(args[0], Union[Page, Locator]):
        source = args[0]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)
        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 1b: Direct call with source only (callable pattern - keyword)
    # await wait_for_dom_settled(source=page, settle_duration=0.5, timeout_s=30)
    if "source" in kwargs and "func" not in kwargs and len(args) == 0:
        source = kwargs["source"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        if not isinstance(source, Union[Page, Locator]):
            raise ValueError(
                "No Page or Locator object found in function arguments. 'source' parameter must be a Playwright Page or Locator object."
            )

        return _wait_for_dom_settled_original(
            source=source,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 2: Wrapper pattern with source and func as keyword arguments
    # await wait_for_dom_settled(source=source, func=func, settle_duration=0.5, timeout_s=30)
    if "source" in kwargs and "func" in kwargs:
        source = kwargs["source"]
        func = kwargs["func"]
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        if not isinstance(source, Union[Page, Locator]):
            raise ValueError(
                "No Page or Locator object found in function arguments. 'source' parameter must be a Playwright Page or Locator object."
            )

        return _wait_for_dom_settled_core(
            source=source,
            func=func,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    # Case 3: Decorator without arguments
    # @wait_for_dom_settled
    if len(args) == 1 and callable(args[0]) and not isinstance(args[0], Union[Page, Locator]):
        func = args[0]
        return _create_decorated_function(func, settle_duration=0.5, timeout_s=30.0)  # type: ignore

    # Case 4: Decorator factory with arguments (including empty parentheses)
    # @wait_for_dom_settled() or @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)
    if len(args) == 0 and "source" not in kwargs and "func" not in kwargs:
        settle_duration = kwargs.get("settle_duration", 0.5)
        timeout_s = kwargs.get("timeout_s", 30.0)

        def decorator(func: Callable[..., Awaitable[Any]]) -> Callable[..., Awaitable[Any]]:
            return _create_decorated_function(func, settle_duration=settle_duration, timeout_s=timeout_s)

        return decorator

    raise ValueError(
        "Invalid usage. Valid patterns:\n"
        "1. await wait_for_dom_settled(source, settle_duration=0.5, timeout_s=30) or await wait_for_dom_settled(source=source, settle_duration=0.5, timeout_s=30)\n"
        "2. await wait_for_dom_settled(source=source, func=func, settle_duration=0.5, timeout_s=30)\n"
        "3. @wait_for_dom_settled or @wait_for_dom_settled()\n"
        "4. @wait_for_dom_settled(settle_duration=1.0, timeout_s=30)"
    )


def _create_decorated_function(
    func: Callable[..., Awaitable[Any]],
    settle_duration: float,
    timeout_s: float,
) -> Callable[..., Awaitable[Any]]:
    """Helper to create a decorated function with DOM waiting."""

    @functools.wraps(func)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        # Find the Page or Locator object in function arguments
        source_obj = None
        for arg in args:
            if isinstance(arg, Union[Page, Locator]):
                source_obj = arg
                break
        if source_obj is None:
            source_obj = kwargs.get("page") or kwargs.get("source")

        if not source_obj or not isinstance(source_obj, Union[Page, Locator]):
            logger.error(
                "No Page or Locator object found in function arguments. The decorated function must have a 'page' or 'source' parameter or receive a Page/Locator object as an argument."
            )
            raise ValueError(
                "No Page or Locator object found in function arguments. The decorated function must have a 'page' or 'source' parameter or receive a Page/Locator object as an argument."
            )

        async def func_with_args():
            return await func(*args, **kwargs)

        return await _wait_for_dom_settled_core(
            source=source_obj,
            func=func_with_args,
            settle_duration=settle_duration,
            timeout_s=timeout_s,
        )

    return wrapper


async def _wait_for_dom_settled_core(
    *,
    source: Union[Page, Locator],
    func: Callable[..., Awaitable[Any]],
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
):
    """Core function that executes the provided function and then waits for DOM to settle."""
    if not isinstance(source, Union[Page, Locator]):
        raise ValueError(
            "No Page or Locator object found in function arguments. Source parameter must be a Playwright Page or Locator object."
        )

    logger.debug(f"Source object: {source}")

    # Execute the function first
    result = await func()

    # Then wait for DOM to settle
    await _wait_for_dom_settled_original(
        source=source,
        settle_duration=settle_duration,
        timeout_s=timeout_s,
    )

    return result


async def _wait_for_dom_settled_original(
    source: Union[Page, Locator],
    *,
    settle_duration: float = 0.5,
    timeout_s: float = 30.0,
) -> bool:
    """Original DOM settlement detection logic."""
    if not isinstance(source, Union[Page, Locator]):
        raise ValueError(
            "No Page or Locator object found in function arguments. Source parameter must be a Playwright Page or Locator object."
        )

    settle_duration_ms = int(settle_duration * 1000)
    timeout_ms = int(timeout_s * 1000)

    # Get the page object
    if isinstance(source, Locator):
        page_obj = source.page
        element_handle = await source.element_handle()
    else:
        page_obj = source
        element_handle = await page_obj.evaluate_handle("document.documentElement")

    js_code = f"""
    (target) => {{
        return new Promise((resolve, reject) => {{
            if (!target) {{
                reject(new Error('Target element not found'));
                return;
            }}

            let mutationTimer;
            let timeoutTimer;
            let settled = false;

            const observer = new MutationObserver(() => {{
                if (settled) return;

                clearTimeout(mutationTimer);
                mutationTimer = setTimeout(() => {{
                    settled = true;
                    observer.disconnect();
                    clearTimeout(timeoutTimer);
                    resolve(true);
                }}, {settle_duration_ms});
            }});

            timeoutTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(mutationTimer);
                reject(new Error('DOM timed out settling after {timeout_ms} ms'));
            }}, {timeout_ms});

            observer.observe(target, {{
                childList: true,
                subtree: true,
                attributes: true,
                characterData: true
            }});

            // Initial timer for already-stable DOM
            mutationTimer = setTimeout(() => {{
                settled = true;
                observer.disconnect();
                clearTimeout(timeoutTimer);
                resolve(true);
            }}, {settle_duration_ms});
        }});
    }}
    """

    try:
        result = await page_obj.evaluate(js_code, element_handle)
        return result
    except Exception as e:
        logger.warning(f"DOM settlement detection failed: {e}")
        return False
