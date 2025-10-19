# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-09-06

Purpose: Define read-only key containers for the logging subsystem.

The module centralises symbolic names for log levels, facilities, and queue
attributes to keep engines, formatters, and clients aligned.
"""

import syslog

from types import MappingProxyType
from typing import Mapping
from ..attribtool import ReadOnlyClass


class LogKeys(object, metaclass=ReadOnlyClass):
    """Expose symbolic names shared across log engines, queues, and clients."""

    BUFFERED: str = "__buffered__"
    CONF: str = "__conf__"
    DIR: str = "__dir__"
    FACILITY: str = "__facility__"
    FILE: str = "__file__"
    FORMATTER: str = "__formatter__"
    LEVEL: str = "__level__"
    NAME: str = "__name__"
    NO_CONF: str = "__no_conf__"
    QUEUE: str = "__queue__"
    SYSLOG: str = "__syslog__"
    ROTATE_SIZE: str = "__rotate_size__"
    ROTATE_COUNT: str = "__rotate_count__"


class SysLogKeys(object, metaclass=ReadOnlyClass):
    """Provide syslog level and facility constants as read-only namespaces."""

    class __Levels(object, metaclass=ReadOnlyClass):
        ALERT = syslog.LOG_ALERT
        CRITICAL = syslog.LOG_CRIT
        DEBUG = syslog.LOG_DEBUG
        EMERGENCY = syslog.LOG_EMERG
        ERROR = syslog.LOG_ERR
        INFO = syslog.LOG_INFO
        NOTICE = syslog.LOG_NOTICE
        WARNING = syslog.LOG_WARNING

    class __Facilities(object, metaclass=ReadOnlyClass):
        DAEMON = syslog.LOG_DAEMON
        LOCAL0 = syslog.LOG_LOCAL0
        LOCAL1 = syslog.LOG_LOCAL1
        LOCAL2 = syslog.LOG_LOCAL2
        LOCAL3 = syslog.LOG_LOCAL3
        LOCAL4 = syslog.LOG_LOCAL4
        LOCAL5 = syslog.LOG_LOCAL5
        LOCAL6 = syslog.LOG_LOCAL6
        LOCAL7 = syslog.LOG_LOCAL7
        MAIL = syslog.LOG_MAIL
        SYSLOG = syslog.LOG_SYSLOG
        USER = syslog.LOG_USER

    #: Exposes syslog level constants as read-only namespace.
    level: type[__Levels] = __Levels
    #: Exposes syslog facility constants as read-only namespace.
    facility: type[__Facilities] = __Facilities
    #: Maps human-readable level names to syslog values.
    level_keys: Mapping[str, int] = MappingProxyType(
        {
            "ALERT": __Levels.ALERT,
            "CRITICAL": __Levels.CRITICAL,
            "DEBUG": __Levels.DEBUG,
            "EMERGENCY": __Levels.EMERGENCY,
            "ERROR": __Levels.ERROR,
            "INFO": __Levels.INFO,
            "NOTICE": __Levels.NOTICE,
            "WARNING": __Levels.WARNING,
        }
    )
    #: Maps human-readable facility names to syslog values.
    facility_keys: Mapping[str, int] = MappingProxyType(
        {
            "DAEMON": __Facilities.DAEMON,
            "LOCAL0": __Facilities.LOCAL0,
            "LOCAL1": __Facilities.LOCAL1,
            "LOCAL2": __Facilities.LOCAL2,
            "LOCAL3": __Facilities.LOCAL3,
            "LOCAL4": __Facilities.LOCAL4,
            "LOCAL5": __Facilities.LOCAL5,
            "LOCAL6": __Facilities.LOCAL6,
            "LOCAL7": __Facilities.LOCAL7,
            "MAIL": __Facilities.MAIL,
            "SYSLOG": __Facilities.SYSLOG,
            "USER": __Facilities.USER,
        }
    )


class LogsLevelKeys(object, metaclass=ReadOnlyClass):
    """Provide symbolic identifiers for supported log severities."""

    ALERT: str = "ALERT"
    CRITICAL: str = "CRITICAL"
    DEBUG: str = "DEBUG"
    EMERGENCY: str = "EMERGENCY"
    ERROR: str = "ERROR"
    INFO: str = "INFO"
    NOTICE: str = "NOTICE"
    WARNING: str = "WARNING"

    #: Contains all supported log level identifiers.
    keys: tuple[str, ...] = (
        ALERT,
        CRITICAL,
        DEBUG,
        EMERGENCY,
        ERROR,
        INFO,
        NOTICE,
        WARNING,
    )


# #[EOF]#######################################################################
