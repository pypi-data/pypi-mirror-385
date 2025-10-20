"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2024-01-15

Purpose: Provide string utilities with lazy loading of heavy helpers.

The module exposes cryptographic helpers on demand to avoid unnecessary import
costs for lightweight string tooling workflows.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .crypto import SimpleCrypto as SimpleCrypto

__all__ = [
    "SimpleCrypto",
]

_EXPORT_MAP = {
    "SimpleCrypto": ("crypto", "SimpleCrypto"),
}


def __getattr__(name: str) -> Any:
    """Resolve configured stringtool exports on demand.

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
