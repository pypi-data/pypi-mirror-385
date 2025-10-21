# Copyright (c) 2025, qBraid Development Team
# All rights reserved.

# pylint: disable=duplicate-code

"""
Module serving qBraid system information.

.. currentmodule:: qbraid_core.system


"""
__all__ = []  # type: ignore[var-annotated]

_lazy_mods = [
    "magic",
    "exceptions",
    "executables",
    "generic",
    "packages",
    "filemanager",
    "versions",
]


def __getattr__(name):
    if name in _lazy_mods:
        import importlib  # pylint: disable=import-outside-toplevel

        module = importlib.import_module(f".{name}", __name__)
        globals()[name] = module
        return module
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__():
    return sorted(__all__ + _lazy_mods)
