import logging
import functools
import inspect
import time
import threading
import traceback
import asyncio
import sys
from typing import Any, Callable, Dict, Optional, TypeVar, Union, cast, Awaitable, Type, TypeVar, overload
from functools import wraps
from typing_extensions import ParamSpec, Concatenate

# Type variables for generic function typing
P = ParamSpec('P')
R = TypeVar('R')
T = TypeVar('T')
F = TypeVar('F', bound=Callable[..., Any])

# Thread-local storage for tracking recursive calls
_thread_local = threading.local()

# Get the logger for this module
logger = logging.getLogger('decorator')
logger.propagate = False  # Prevent duplicate logs

# Ensure the logger has at least one handler
if not logger.handlers:
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)  # Default to INFO level
    
# Custom exception for decorator-specific errors
class DecoratorError(Exception):
    """Base exception for decorator-related errors."""
    pass



class ErrorManager:

    def __init__(
        self, error_type: str, message: str, context: dict[str, Any], status_code: int
    ):
        self.error_type = error_type
        self.message = message
        self.context = self._safe_context_str(context)
        self.status_code = status_code
        self.log_error()

    def _safe_context_str(self, context: Dict[str, Any]) -> str:
        """Safely convert context to string without triggering DB queries"""
        try:
            # Only include basic info that won't trigger DB queries
            safe_context = {
                "args": str(context.get("args", "")),
                "kwargs": str(context.get("kwargs", "")),
            }
            return str(safe_context)
        except Exception as e:
            return f"Error converting context to string: {str(e)}"

    def log_error(self):
        logger.error(
            f"Error Type: {self.error_type}, Message: {self.message}, Status Code: {self.status_code}"
        )
        logger.error(f"Context: {self.context}")


def log_decor(
    func_or_mode: Optional[Union[Callable[P, R], int]] = None,
    *,
    mode: int = 0,
    log_level: int = logging.INFO,
    log_exceptions: bool = True,
    max_arg_length: int = 1000,
    max_result_length: int = 5000
) -> Union[Callable[[Callable[P, R]], Callable[P, R]], Callable[P, R]]:
    """
    A decorator for logging function entry, exit, and exceptions.

    Args:
        func_or_mode: The function to decorate or the mode value (for backward compatibility)
        mode: Logging mode:
              0: Log function entry/exit with timing
              1: Log entry (with args/kwargs) and exit with timing
              2: Log entry (with args/kwargs), exit with timing, and result
              3: Log entry (with args/kwargs), exit with timing, result, and full traceback
        log_level: Logging level (from logging module)
        log_exceptions: Whether to log exceptions
        max_arg_length: Maximum length of logged arguments (truncated if longer)
        max_result_length: Maximum length of logged results (truncated if longer)

    Returns:
        Decorated function with logging
    """
    # Handle the case where mode is passed as the first argument (backward compatibility)
    if isinstance(func_or_mode, int):
        mode = func_or_mode
        func_or_mode = None

    # Validate mode
    if mode not in (0, 1, 2, 3):
        logger.warning(f"Invalid mode {mode}, defaulting to mode 2")
        mode = 2

    def _truncate(value: Any, max_length: int) -> str:
        """Safely truncate string representation of a value."""
        try:
            s = str(value)
            return s[:max_length] + '... [truncated]' if len(s) > max_length else s
        except Exception:
            return '[unserializable]'

    def _log_entry(func: Callable[..., Any], args: tuple, kwargs: Dict[str, Any]) -> None:
        """Log function entry with arguments if mode >= 1."""
        if mode >= 1:
            args_repr = [_truncate(arg, max_arg_length) for arg in args]
            kwargs_repr = {k: _truncate(v, max_arg_length) for k, v in kwargs.items()}
            logger.log(log_level, f"→ {func.__qualname__} args={args_repr}, kwargs={kwargs_repr}")
        else:
            logger.log(log_level, f"→ {func.__qualname__}()")

    def _log_exit(func: Callable[..., Any], result: Any, duration: float) -> None:
        """Log function exit with result if mode >= 2."""
        duration_str = f" in {duration:.3f}s"
        if mode >= 2:
            result_str = _truncate(result, max_result_length)
            logger.log(log_level, f"← {func.__qualname__} returned: {result_str}{duration_str}")
        else:
            logger.log(log_level, f"← {func.__qualname__}{duration_str}")

    def _log_exception(func: Callable[..., Any], e: Exception) -> None:
        """Log exception with appropriate detail level."""
        if not log_exceptions:
            return

        exc_type = type(e).__name__
        if mode >= 3:  # Full traceback for mode 3
            tb = traceback.extract_tb(e.__traceback__)[-1]
            logger.error(
                f"✗ {func.__qualname__} failed at {tb.filename}:{tb.lineno}: {str(e)}\n"
                f"Type: {exc_type}\nTraceback:\n{traceback.format_exc()}",
                exc_info=False
            )
        else:  # Just the error message for modes 0-2
            logger.error(f"✗ {func.__qualname__} failed: {exc_type}: {str(e)}")

    def _decorator(func: Callable[P, R]) -> Callable[P, R]:
        """The actual decorator that wraps the function."""
        if asyncio.iscoroutinefunction(func):
            @wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                _log_entry(func, args, kwargs)
                try:
                    start_time = time.time()
                    result = await func(*args, **kwargs)
                    _log_exit(func, result, time.time() - start_time)
                    return result
                except Exception as e:
                    _log_exception(func, e)
                    raise
            return cast(Callable[P, R], async_wrapper)
        else:
            @wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                _log_entry(func, args, kwargs)
                try:
                    start_time = time.time()
                    result = func(*args, **kwargs)
                    _log_exit(func, result, time.time() - start_time)
                    return result
                except Exception as e:
                    _log_exception(func, e)
                    raise
            return cast(Callable[P, R], sync_wrapper)

    # Handle both @log_decor and @log_decor(mode=1) cases
    if func_or_mode is None:
        return _decorator
    if callable(func_or_mode):
        return _decorator(func_or_mode)
    raise ValueError("Invalid arguments passed to log_decor")


# Decorator using print instead of logger
def print_decor(_func=None, mode=-1):
    """
    Decorator to print function entry, exit, and exceptions.
    Prints at INFO level for entry and exit, ERROR for exceptions.
    mode: 0=print inputs, 1=print outputs, 2=print both (default)
    """
    def decorator(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            print(f"Entering: {func.__name__}")
            if mode in (0, 2):
                print(f"Inputs: args={args}, kwargs={kwargs}")
            try:
                result = await func(*args, **kwargs)
                if mode in (1, 2):
                    print(f"Output: {result}")
                print(f"Exiting: {func.__name__}")
                return result
            except Exception as e:
                print(f"Exception in {func.__name__}: {e}")
                traceback.print_exc()
                raise

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            print(f"Entering: {func.__name__}")
            if mode in (0, 2):
                print(f"Inputs: args={args}, kwargs={kwargs}")
            try:
                result = func(*args, **kwargs)
                if mode in (1, 2):
                    print(f"Output: {result}")
                print(f"Exiting: {func.__name__}")
                return result
            except Exception as e:
                print(f"Exception in {func.__name__}: {e}")
                traceback.print_exc()
                raise

        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    if _func is None:
        return decorator
    else:
        return decorator(_func)




