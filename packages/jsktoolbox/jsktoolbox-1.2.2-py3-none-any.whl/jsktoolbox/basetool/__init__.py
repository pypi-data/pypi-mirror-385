# -*- coding: UTF-8 -*-
"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2024-01-15

Purpose: Provide common base classes shared across JskToolBox modules.

These helpers cover class metadata, typed data containers, logging scaffolding,
and threading utilities that higher-level packages build upon.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .classes import BClasses as BClasses
    from .data import BData as BData
    from .logs import BLogFormatter as BLogFormatter
    from .logs import BLoggerEngine as BLoggerEngine
    from .logs import BLoggerQueue as BLoggerQueue
    from .threads import ThBaseObject as ThBaseObject

__all__ = [
    "BClasses",
    "BData",
    "BLogFormatter",
    "BLoggerEngine",
    "BLoggerQueue",
    "ThBaseObject",
]

_EXPORT_MAP = {
    "BClasses": ("classes", "BClasses"),
    "BData": ("data", "BData"),
    "BLogFormatter": ("logs", "BLogFormatter"),
    "BLoggerEngine": ("logs", "BLoggerEngine"),
    "BLoggerQueue": ("logs", "BLoggerQueue"),
    "ThBaseObject": ("threads", "ThBaseObject"),
}


def __getattr__(name: str) -> Any:
    """Resolve configured basetool exports on demand.

    ### Arguments:
    * name: str - Requested attribute name.

    ### Returns:
    [Any] - Resolved attribute from the target submodule.

    ### Raises:
    * AttributeError: Raised when the attribute is not registered.
    """
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, attr_name)
    globals()[name] = value
    return value


def __dir__() -> list[str]:
    """Expose lazy exports to dir()."""
    return sorted(__all__)
