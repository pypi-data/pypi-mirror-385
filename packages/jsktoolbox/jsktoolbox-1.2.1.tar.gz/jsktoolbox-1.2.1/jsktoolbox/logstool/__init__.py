"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2023-09-04

Purpose: Aggregate logging toolkit components (engines, formatters, queues).

Exports are loaded lazily to avoid circular import with `jsktoolbox.basetool`.
Type hints are provided for IDE support while maintaining lazy loading behavior.
"""

from importlib import import_module
from typing import TYPE_CHECKING, Any

# Type stubs for IDE support - these imports are only evaluated by type checkers
if TYPE_CHECKING:
    from .keys import LogKeys as LogKeys
    from .keys import LogsLevelKeys as LogsLevelKeys
    from .keys import SysLogKeys as SysLogKeys
    from .queue import LoggerQueue as LoggerQueue
    from .formatters import LogFormatterNull as LogFormatterNull
    from .formatters import LogFormatterDateTime as LogFormatterDateTime
    from .formatters import LogFormatterTime as LogFormatterTime
    from .formatters import LogFormatterTimestamp as LogFormatterTimestamp
    from .engines import LoggerEngineStdout as LoggerEngineStdout
    from .engines import LoggerEngineStderr as LoggerEngineStderr
    from .engines import LoggerEngineFile as LoggerEngineFile
    from .engines import LoggerEngineSyslog as LoggerEngineSyslog
    from .logs import LoggerClient as LoggerClient
    from .logs import LoggerEngine as LoggerEngine
    from .logs import ThLoggerProcessor as ThLoggerProcessor

__all__ = [
    "LogKeys",
    "LogsLevelKeys",
    "SysLogKeys",
    "LoggerQueue",
    "LogFormatterNull",
    "LogFormatterDateTime",
    "LogFormatterTime",
    "LogFormatterTimestamp",
    "LoggerEngineStdout",
    "LoggerEngineStderr",
    "LoggerEngineFile",
    "LoggerEngineSyslog",
    "LoggerClient",
    "LoggerEngine",
    "ThLoggerProcessor",
]

_EXPORT_MAP = {
    "LogKeys": ("keys", "LogKeys"),
    "LogsLevelKeys": ("keys", "LogsLevelKeys"),
    "SysLogKeys": ("keys", "SysLogKeys"),
    "LoggerQueue": ("queue", "LoggerQueue"),
    "LogFormatterNull": ("formatters", "LogFormatterNull"),
    "LogFormatterDateTime": ("formatters", "LogFormatterDateTime"),
    "LogFormatterTime": ("formatters", "LogFormatterTime"),
    "LogFormatterTimestamp": ("formatters", "LogFormatterTimestamp"),
    "LoggerEngineStdout": ("engines", "LoggerEngineStdout"),
    "LoggerEngineStderr": ("engines", "LoggerEngineStderr"),
    "LoggerEngineFile": ("engines", "LoggerEngineFile"),
    "LoggerEngineSyslog": ("engines", "LoggerEngineSyslog"),
    "LoggerClient": ("logs", "LoggerClient"),
    "LoggerEngine": ("logs", "LoggerEngine"),
    "ThLoggerProcessor": ("logs", "ThLoggerProcessor"),
}


def __getattr__(name: str) -> Any:
    if name not in _EXPORT_MAP:
        raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
    module_name, attr_name = _EXPORT_MAP[name]
    module = import_module(f"{__name__}.{module_name}")
    value = getattr(module, attr_name)
    globals()[name] = value
    return value
