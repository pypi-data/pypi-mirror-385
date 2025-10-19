"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2023-10-29

Purpose: Provide configuration processing helpers.

Exports are loaded lazily to keep import costs low while maintaining IDE hints.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from .libs.data import DataProcessor as DataProcessor
    from .libs.data import SectionModel as SectionModel
    from .libs.data import VariableModel as VariableModel
    from .libs.file import FileProcessor as FileProcessor
    from .main import Config as Config

__all__ = [
    "Config",
    "DataProcessor",
    "FileProcessor",
    "SectionModel",
    "VariableModel",
]

_EXPORT_MAP = {
    "Config": ("main", "Config"),
    "DataProcessor": ("libs.data", "DataProcessor"),
    "FileProcessor": ("libs.file", "FileProcessor"),
    "SectionModel": ("libs.data", "SectionModel"),
    "VariableModel": ("libs.data", "VariableModel"),
}


def __getattr__(name: str) -> Any:
    """Lazily resolve configured exports."""
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
