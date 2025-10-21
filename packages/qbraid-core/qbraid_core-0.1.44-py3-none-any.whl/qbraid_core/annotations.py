# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module defining function annotations (e.g. decorators) used in qbraid-core.

"""
import functools
import warnings
from typing import Callable, Union


def deprecated(func_or_message: Union[Callable, str]):
    """
    Decorator to mark functions as deprecated with an optional custom message.

    This decorator emits a warning when the decorated function is called. The warning
    can include a custom deprecation message if one is provided.

    Args:
        func_or_message: Either the function to be decorated or a string message.
                         If a string is provided, it will be used as the custom
                         deprecation message.

    Returns:
        A decorator that wraps the given function and shows a DeprecationWarning
        when the function is called. If a custom message is provided, it will
        be included in the warning.

    Raises:
        DeprecationWarning: When the decorated function is invoked.

    Example Usage:
        @deprecated
        def old_function():
            pass

        @deprecated("Use 'new_function' instead.")
        def old_function_with_message():
            pass
    """
    if isinstance(func_or_message, str):
        message = func_or_message
        func = None
    else:
        message = None
        func = func_or_message

    def decorator(inner_func):
        @functools.wraps(inner_func)
        def wrapped_func(*args, **kwargs):
            warning_message = f"Call to deprecated function {inner_func.__name__}."
            if message:
                warning_message += f" {message}"
            warnings.simplefilter("always", DeprecationWarning)
            warnings.warn(warning_message, category=DeprecationWarning, stacklevel=2)
            warnings.simplefilter("default", DeprecationWarning)
            return inner_func(*args, **kwargs)

        return wrapped_func

    return decorator if func is None else decorator(func)  # type: ignore
