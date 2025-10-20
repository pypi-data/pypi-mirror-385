# -*- coding: UTF-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2023-10-10

Purpose: Provide reusable log formatter implementations.

Each formatter composes a list of format segments consumed by `BLogFormatter`
to render message payloads consistently across engines.
"""

from datetime import datetime

from ..basetool.logs import BLogFormatter
from ..datetool import Timestamp


class LogFormatterNull(BLogFormatter):
    """Provide bare message formatting with optional logger name prefix."""

    def __init__(self) -> None:
        """Initialise null formatter templates.

        ### Returns:
        None - Populates the formatter template list.
        """
        self._forms_.append("{message}")
        self._forms_.append("[{name}]: {message}")


class LogFormatterDateTime(BLogFormatter):
    """Prefix log messages with the current local date and time."""

    def __init__(self) -> None:
        """Initialise date-time formatter templates.

        ### Returns:
        None - Populates the formatter template list.
        """
        self._forms_.append(self.__get_formatted_date__)
        self._forms_.append("{message}")
        self._forms_.append("[{name}]: {message}")

    def __get_formatted_date__(self) -> str:
        """Return the current local datetime string.

        ### Returns:
        str - Timestamp in `%Y-%m-%d %H:%M:%S` format.
        """
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


class LogFormatterTime(BLogFormatter):
    """Prefix log messages with the current local time."""

    def __init__(self) -> None:
        """Initialise time-only formatter templates.

        ### Returns:
        None - Populates the formatter template list.
        """
        self._forms_.append(self.__get_formatted_time__)
        self._forms_.append("{message}")
        self._forms_.append("[{name}]: {message}")

    def __get_formatted_time__(self) -> str:
        """Return the current local time string.

        ### Returns:
        str - Timestamp in `%H:%M:%S` format.
        """
        return datetime.now().strftime("%H:%M:%S")


class LogFormatterTimestamp(BLogFormatter):
    """Prefix log messages with a high-resolution numeric timestamp."""

    def __init__(self) -> None:
        """Initialise timestamp formatter templates.

        ### Returns:
        None - Populates the formatter template list.
        """
        self._forms_.append(Timestamp.now())
        self._forms_.append("{message}")
        self._forms_.append("[{name}]: {message}")


# #[EOF]#######################################################################
