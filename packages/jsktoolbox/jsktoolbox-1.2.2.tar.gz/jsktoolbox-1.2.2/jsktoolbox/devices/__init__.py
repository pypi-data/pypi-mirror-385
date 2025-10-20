"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-05-12

Purpose: Expose device-related subpackages (connectors, libraries, vendors)
under a unified namespace.

This module keeps the import surface minimal to avoid side effects while still
providing a single integration point for device tooling. Exports are resolved
lazily to defer heavyweight dependencies until they are explicitly requested.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .libs.base import BDebug as BDebug
    from .libs.base import BDev as BDev
    from .libs.converters import B64Converter as B64Converter
    from .network.connectors import API as API
    from .network.connectors import IConnector as IConnector
    from .network.connectors import SSH as SSH
    from .mikrotik.base import BRouterOS as BRouterOS
    from .mikrotik.base import Element as Element
    from .mikrotik.routerboard import RouterBoard as RouterBoard

__all__ = [
    "API",
    "BDebug",
    "BDev",
    "BRouterOS",
    "B64Converter",
    "Element",
    "IConnector",
    "RouterBoard",
    # "SSH", # Not Implemented Yet
]

_EXPORT_MAP = {
    "BDebug": ("libs.base", "BDebug"),
    "BDev": ("libs.base", "BDev"),
    "B64Converter": ("libs.converters", "B64Converter"),
    "IConnector": ("network.connectors", "IConnector"),
    "API": ("network.connectors", "API"),
    # "SSH": ("network.connectors", "SSH"),
    "BRouterOS": ("mikrotik.base", "BRouterOS"),
    "Element": ("mikrotik.base", "Element"),
    "RouterBoard": ("mikrotik.routerboard", "RouterBoard"),
}


def __getattr__(name: str) -> Any:
    """Resolve configured device exports on demand.

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


# #[EOF]#######################################################################
