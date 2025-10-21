# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

"""
Module for registering qBraid service clients.

"""
import importlib
import inspect
import os
import pkgutil
from typing import Callable, Iterator, Optional, Type

client_registry: dict[str, Type] = {}


def register_client(service_name: Optional[str] = None) -> Callable:
    """
    Decorator to register a client class under a given service name.

    If the service name is not explicitly provided, the decorator attempts to infer the service name
    based on the directory name of the module where the decorated class is defined. This is useful
    for automating the registration of service clients based on their directory structure.

    Args:
        service_name (Optional[str]): The name of the service to register the client under. If None,
                                      the name is inferred from the module's directory name.

    Returns:
        Callable: A decorator that registers the decorated class in the global `client_registry`
                  under the determined service name.

    Raises:
        ValueError: If the service name could not be determined automatically.

    Example:
        @register_client()
        class Service1Client:
        # Implementation of the client
    """

    def decorator(cls: Type) -> Type:
        nonlocal service_name
        if service_name is None:
            # Inspect the stack to find the module of the caller
            frame = inspect.stack()[1]
            module = inspect.getmodule(frame[0])
            if module is not None and hasattr(module, "__file__") and module.__file__ is not None:
                # Extract the service name from the module's file path
                service_dir = os.path.basename(os.path.dirname(module.__file__))
                service_name = service_dir
            else:
                raise ValueError("Could not determine the service name automatically.")

        # Register the class with the determined service name
        client_registry[service_name] = cls

        return cls

    return decorator


def discover_services(directory: str) -> Iterator[str]:
    """
    Discover and import service client modules to trigger registration.

    Args:
        directory (str): Directory path to search for service modules.

    Returns:
        Iterator over the names of the discovered services.
    """
    for _, name, ispkg in pkgutil.iter_modules([directory]):
        if ispkg:
            package = f"qbraid_core.services.{name}"
            yield name
            importlib.import_module(package)
