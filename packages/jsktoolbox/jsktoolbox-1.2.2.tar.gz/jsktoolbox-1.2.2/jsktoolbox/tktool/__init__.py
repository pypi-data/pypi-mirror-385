# -*- coding: UTF-8 -*-
"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2024-01-15

Purpose: Provide Tkinter toolkit exports with lazy loading.

The module exposes base mixins, geometry helpers, and composite widgets on demand so that projects
can import the package without immediately initialising Tkinter or loading heavy helpers.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .base import TkBase as TkBase
    from .layout import Grid as Grid
    from .layout import Pack as Pack
    from .layout import Place as Place
    from .tools import ClipBoard as ClipBoard
    from .widgets import CreateToolTip as CreateToolTip
    from .widgets import StatusBarTkFrame as StatusBarTkFrame
    from .widgets import StatusBarTtkFrame as StatusBarTtkFrame
    from .widgets import VerticalScrolledTkFrame as VerticalScrolledTkFrame
    from .widgets import VerticalScrolledTtkFrame as VerticalScrolledTtkFrame

__all__ = [
    "TkBase",
    "Pack",
    "Grid",
    "Place",
    "ClipBoard",
    "StatusBarTkFrame",
    "StatusBarTtkFrame",
    "CreateToolTip",
    "VerticalScrolledTkFrame",
    "VerticalScrolledTtkFrame",
]

_EXPORT_MAP = {
    "TkBase": ("base", "TkBase"),
    "Pack": ("layout", "Pack"),
    "Grid": ("layout", "Grid"),
    "Place": ("layout", "Place"),
    "ClipBoard": ("tools", "ClipBoard"),
    "StatusBarTkFrame": ("widgets", "StatusBarTkFrame"),
    "StatusBarTtkFrame": ("widgets", "StatusBarTtkFrame"),
    "CreateToolTip": ("widgets", "CreateToolTip"),
    "VerticalScrolledTkFrame": ("widgets", "VerticalScrolledTkFrame"),
    "VerticalScrolledTtkFrame": ("widgets", "VerticalScrolledTtkFrame"),
}


def __getattr__(name: str) -> Any:
    """Resolve configured Tk toolkit exports on demand.

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
