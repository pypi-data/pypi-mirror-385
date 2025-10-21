# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
This top level module contains the main qBraid public functionality.

.. currentmodule:: qbraid_core

Classes
----------

.. autosummary::
   :toctree: ../stubs/

   Session
   QbraidClient
   QbraidSession

Functions
----------

.. autosummary::
   :toctree: ../stubs/

   client
   setup_default_session

Exceptions
------------

.. autosummary::
   :toctree: ../stubs/

   QbraidException
   QbraidChainedException
   AuthError
   ConfigError
   RequestsApiError
   ResourceNotFoundError
   UserNotFoundError

"""
from ._compat import __version__
from ._import import LazyLoader
from .annotations import deprecated
from .client import QbraidClient
from .exceptions import (
    AuthError,
    ConfigError,
    QbraidChainedException,
    QbraidException,
    RequestsApiError,
    ResourceNotFoundError,
    UserNotFoundError,
)
from .retry import PostForcelistRetry
from .sessions import QbraidSession, Session

# Hold the default session in a global variable, but don't initialize it yet.
_DEFAULT_SESSION = None  # pylint: disable=invalid-name


def setup_default_session(**kwargs):
    """
    Set up a default session, passing through any parameters to the session
    constructor. There is no need to call this unless you wish to pass custom
    parameters, because a default session will be created for you.
    """
    global _DEFAULT_SESSION  # pylint: disable=global-statement
    _DEFAULT_SESSION = QbraidSession(**kwargs)


def _get_default_session():
    """
    Get or create a default session. If the session does not exist, it is created
    with the provided keyword arguments. If it already exists, the existing session
    is returned, ignoring any provided arguments.

    This function ensures that a session is created only once and reused, offering
    a balance between laziness and reusability.

    Args:
        **kwargs: Keyword arguments to pass to the Session constructor if creating
                  a new session.

    Returns:
        The default session instance.
    """
    if _DEFAULT_SESSION is None:
        setup_default_session()

    return _DEFAULT_SESSION


def client(*args, **kwargs):
    """
    Create a client for a specified service using the default session. If specific
    session parameters are needed, a new default session can be initialized before
    calling this function.

    Args:
        service_name (str): The name of the service for which to create the client.
        **kwargs: Keyword arguments for session customization, used only if creating
                  a new default session.

    Returns:
        A service client instance.
    """
    return _get_default_session().client(*args, **kwargs)


__all__ = [
    "Session",
    "QbraidClient",
    "QbraidSession",
    "PostForcelistRetry",
    "client",
    "setup_default_session",
    "QbraidException",
    "QbraidChainedException",
    "AuthError",
    "ConfigError",
    "RequestsApiError",
    "ResourceNotFoundError",
    "UserNotFoundError",
    "LazyLoader",
    "deprecated",
    "__version__",
]

_lazy_mods = ["services", "system"]


def __getattr__(name):
    if name in _lazy_mods:
        return LazyLoader(name, globals(), f"qbraid_core.{name}")
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__ + _lazy_mods)
