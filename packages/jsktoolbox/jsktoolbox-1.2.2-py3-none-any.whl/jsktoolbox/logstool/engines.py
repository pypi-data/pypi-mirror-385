# -*- coding: UTF-8 -*-
"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2023-10-10

Purpose: Implement logging engines targeting stdout, stderr, files, and syslog.

Each engine adheres to `ILoggerEngine`, providing consistent `send` semantics
while supporting optional formatters and buffering behaviour.
"""

import os
import ssl
import sys
import syslog

from inspect import currentframe
from typing import Optional, Union, cast
from types import ModuleType

from .keys import LogKeys, SysLogKeys

from ..attribtool import NoDynamicAttributes
from ..raisetool import Raise
from ..basetool.data import BData
from ..systemtool import PathChecker
from ..basetool.logs import (
    BLoggerEngine,
)
from ..libs.interfaces.logger_engine import ILoggerEngine
from .formatters import BLogFormatter

# https://www.geeksforgeeks.org/python-testing-output-to-stdout/


class LoggerEngineStdout(ILoggerEngine, BLoggerEngine, BData, NoDynamicAttributes):
    """Emit formatted log records to standard output."""

    def __init__(
        self,
        name: Optional[str] = None,
        formatter: Optional[BLogFormatter] = None,
        buffered: bool = False,
    ) -> None:
        """Initialise stdout engine state.

        ### Arguments:
        * name: Optional[str] - Logger name injected into formatted messages.
        * formatter: Optional[BLogFormatter] - Formatter applied prior to emission.
        * buffered: bool - When False, flush the stream after each message.

        ### Returns:
        None - Constructor.
        """
        if name is not None:
            self.name = name
        self._set_data(key=LogKeys.BUFFERED, value=buffered, set_default_type=bool)
        self._set_data(
            key=LogKeys.FORMATTER,
            value=formatter,
            set_default_type=Optional[BLogFormatter],
        )

    def send(self, message: str) -> None:
        """Write the message to stdout honoring buffering/formatting rules.

        ### Arguments:
        * message: str - Raw log payload.

        ### Returns:
        None - Output is written to stdout.
        """
        formatter: BLogFormatter = self._get_data(key=LogKeys.FORMATTER)  # type: ignore
        if formatter:
            message = formatter.format(message, self.name)
        sys.stdout.write(f"{message}")
        if not f"{message}".endswith("\n"):
            sys.stdout.write("\n")
        if not self._get_data(key=LogKeys.BUFFERED):
            sys.stdout.flush()


class LoggerEngineStderr(ILoggerEngine, BLoggerEngine, BData, NoDynamicAttributes):
    """Emit formatted log records to standard error."""

    def __init__(
        self,
        name: Optional[str] = None,
        formatter: Optional[BLogFormatter] = None,
        buffered: bool = False,
    ) -> None:
        """Initialise stderr engine state.

        ### Arguments:
        * name: Optional[str] - Logger name injected into formatted messages.
        * formatter: Optional[BLogFormatter] - Formatter applied prior to emission.
        * buffered: bool - When False, flush the stream after each message.
        """
        if name is not None:
            self.name = name
        self._set_data(key=LogKeys.BUFFERED, value=buffered, set_default_type=bool)
        self._set_data(
            key=LogKeys.FORMATTER,
            value=formatter,
            set_default_type=Optional[BLogFormatter],
        )

    def send(self, message: str) -> None:
        """Write the message to stderr honoring buffering/formatting rules.

        ### Arguments:
        * message: str - Raw log payload.

        ### Returns:
        None - Output is written to stderr.
        """
        formatter: BLogFormatter = self._get_data(key=LogKeys.FORMATTER)  # type: ignore
        if formatter:
            message = formatter.format(message, self.name)
        sys.stderr.write(f"{message}")
        if not f"{message}".endswith("\n"):
            sys.stderr.write("\n")
        if not self._get_data(key=LogKeys.BUFFERED):
            sys.stderr.flush()


class LoggerEngineFile(ILoggerEngine, BLoggerEngine, BData, NoDynamicAttributes):
    """Append formatted log records to files stored on disk.

    Supports optional size-based rotation with numbered suffixes when configured.
    """

    def __init__(
        self,
        name: Optional[str] = None,
        formatter: Optional[BLogFormatter] = None,
        buffered: bool = False,
    ) -> None:
        """Initialise file engine configuration.

        ### Arguments:
        * name: Optional[str] - Logger name injected into formatted messages.
        * formatter: Optional[BLogFormatter] - Formatter applied prior to emission.
        * buffered: bool - When False, flush the stream after each message.
        """
        if name is not None:
            self.name = name
        self._set_data(key=LogKeys.BUFFERED, value=buffered, set_default_type=bool)
        self._set_data(
            key=LogKeys.FORMATTER,
            value=formatter,
            set_default_type=Optional[BLogFormatter],
        )

    def send(self, message: str) -> None:
        """Append the formatted message to the configured log file.

        ### Arguments:
        * message: str - Raw log payload.

        ### Returns:
        None - The file on disk is updated.

        ### Raises:
        * ValueError: Raised when `logfile` is not configured.
        """
        formatter: BLogFormatter = self._get_data(key=LogKeys.FORMATTER)  # type: ignore
        if formatter:
            message = formatter.format(message, self.name)
            if self.logfile is None:
                raise Raise.error(
                    f"The {self._c_name} is not configured correctly.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
            log_dir: str = self.logdir if self.logdir else ""
            file_path = os.path.join(log_dir, self.logfile)
            self._rotate_if_needed(file_path, len(f"{message}\n"))
            with open(file_path, "a") as file:
                if file.writable:
                    file.write(message)
                    file.write("\n")

    @property
    def logdir(self) -> Optional[str]:
        """Return configured log directory.

        ### Returns:
        Optional[str] - Directory path or None when unset.
        """
        return self._get_data(key=LogKeys.DIR, default_value=None)

    @logdir.setter
    def logdir(self, dirname: str) -> None:
        """Set or create the log directory as required.

        ### Arguments:
        * dirname: str - Directory path used for log files.

        ### Returns:
        None - Internal state updated.
        """
        if dirname[-1] != os.sep:
            dirname = f"{dirname}/"
        pc_ld = PathChecker(dirname)
        if not pc_ld.exists:
            pc_ld.create()
        if pc_ld.exists and pc_ld.is_dir:
            self._set_data(key=LogKeys.DIR, value=pc_ld.path)

    @property
    def logfile(self) -> Optional[str]:
        """Return configured log file name.

        ### Returns:
        Optional[str] - File name or None when unset.
        """
        return self._get_data(key=LogKeys.FILE, default_value=None)

    @logfile.setter
    def logfile(self, filename: str) -> None:
        """Set log file name and ensure the path exists.

        ### Arguments:
        * filename: str - Desired log file name.

        ### Returns:
        None - File path created if necessary.

        ### Raises:
        * FileExistsError: When the path exists and is a directory.
        * PermissionError: When the file cannot be created.
        """
        fn = None
        if self.logdir is None:
            fn = filename
        else:
            fn = os.path.join(self.logdir, filename)
        pc_ld = PathChecker(fn)
        if pc_ld.exists:
            if not pc_ld.is_file:
                raise Raise.error(
                    f"The 'filename' passed: '{filename}', is a directory.",
                    FileExistsError,
                    self._c_name,
                    currentframe(),
                )
        else:
            if not pc_ld.create():
                raise Raise.error(
                    f"I cannot create a file: {pc_ld.path}",
                    PermissionError,
                    self._c_name,
                    currentframe(),
                )
        self.logdir = pc_ld.dirname if pc_ld.dirname else ""
        self._set_data(key=LogKeys.FILE, value=pc_ld.filename)

    @property
    def rotation_max_bytes(self) -> Optional[int]:
        """Return the maximum file size before rotation triggers.

        ### Returns:
        Optional[int] - Size threshold in bytes; None disables rotation.
        """
        value = self._get_data(key=LogKeys.ROTATE_SIZE, default_value=None)
        return cast(Optional[int], value)

    @rotation_max_bytes.setter
    def rotation_max_bytes(self, size: Optional[int]) -> None:
        """Configure the maximum file size before rotation triggers.

        ### Arguments:
        * size: Optional[int] - Positive size in bytes; None disables rotation.

        ### Returns:
        None - Internal configuration updated.

        ### Raises:
        * ValueError: When `size` is not positive.
        """
        if size is None:
            self._delete_data(key=LogKeys.ROTATE_SIZE)
            return
        if size <= 0:
            raise Raise.error(
                f"Expected positive rotation size, received: '{size}'.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        self._set_data(key=LogKeys.ROTATE_SIZE, value=size, set_default_type=int)

    @property
    def rotation_backup_count(self) -> int:
        """Return the number of rotated log archives retained.

        ### Returns:
        int - Number of archives; zero disables rotation.
        """
        value = self._get_data(key=LogKeys.ROTATE_COUNT, default_value=0)
        return cast(int, value) if value is not None else 0

    @rotation_backup_count.setter
    def rotation_backup_count(self, count: int) -> None:
        """Configure how many rotated log archives should be retained.

        ### Arguments:
        * count: int - Non-negative number of archives; zero disables rotation.

        ### Returns:
        None - Internal configuration updated.

        ### Raises:
        * ValueError: When `count` is negative.
        """
        if count < 0:
            raise Raise.error(
                f"Expected non-negative rotation count, received: '{count}'.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        if count == 0:
            self._delete_data(key=LogKeys.ROTATE_COUNT)
            return
        self._set_data(key=LogKeys.ROTATE_COUNT, value=count, set_default_type=int)

    def _rotate_if_needed(self, file_path: str, incoming_length: int) -> None:
        """Rotate the log file when size and backup thresholds are met."""
        max_bytes = self.rotation_max_bytes
        backup_count = self.rotation_backup_count
        if max_bytes is None or backup_count == 0:
            return
        try:
            current_size = os.path.getsize(file_path)
        except FileNotFoundError:
            return
        if (current_size + incoming_length) <= max_bytes:
            return
        self._perform_rotation(file_path, backup_count)

    def _perform_rotation(self, file_path: str, backup_count: int) -> None:
        """Perform numbered rotation using suffixes `.0`, `.1`, etc."""
        if backup_count <= 0:
            return
        highest_path = f"{file_path}.{backup_count - 1}"
        if os.path.exists(highest_path):
            os.remove(highest_path)
        for index in range(backup_count - 1, 0, -1):
            src = f"{file_path}.{index - 1}"
            dst = f"{file_path}.{index}"
            if os.path.exists(src):
                os.replace(src, dst)
        if os.path.exists(file_path):
            os.replace(file_path, f"{file_path}.0")


class LoggerEngineSyslog(ILoggerEngine, BLoggerEngine, BData, NoDynamicAttributes):
    """Send formatted log records to the system syslog daemon."""

    def __init__(
        self,
        name: Optional[str] = None,
        formatter: Optional[BLogFormatter] = None,
        buffered: bool = False,
    ) -> None:
        """Initialise syslog engine configuration.

        ### Arguments:
        * name: Optional[str] - Logger name injected into formatted messages.
        * formatter: Optional[BLogFormatter] - Formatter applied prior to emission.
        * buffered: bool - When False, flush the stream after each message.
        """
        if name is not None:
            self.name = name
        self._set_data(key=LogKeys.BUFFERED, value=buffered, set_default_type=bool)
        self._set_data(
            key=LogKeys.FORMATTER,
            value=formatter,
            set_default_type=Optional[BLogFormatter],
        )
        self._set_data(
            key=LogKeys.LEVEL, value=SysLogKeys.level.INFO, set_default_type=int
        )
        self._set_data(
            key=LogKeys.FACILITY, value=SysLogKeys.facility.USER, set_default_type=int
        )
        self._set_data(
            key=LogKeys.SYSLOG, value=None, set_default_type=Optional[ModuleType]
        )

    def __del__(self) -> None:
        try:
            s_slog: syslog = self._get_data(key=LogKeys.SYSLOG)  # type: ignore
            s_slog.closelog()
        except:
            pass
        self._set_data(key=LogKeys.SYSLOG, value=None)

    @property
    def facility(self) -> int:
        """Return active syslog facility.

        ### Returns:
        int - Syslog facility value.
        """
        return self._get_data(key=LogKeys.FACILITY)  # type: ignore

    @facility.setter
    def facility(self, value: Union[int, str]) -> None:
        """Configure syslog facility.

        ### Arguments:
        * value: Union[int, str] - Facility constant or symbolic name.

        ### Returns:
        None - Resets the syslog handle to apply the new facility.

        ### Raises:
        * ValueError: When integer facility is not recognised.
        * KeyError: When facility name is unknown.
        """
        if isinstance(value, int):
            if value in tuple(SysLogKeys.facility_keys.values()):
                self._set_data(key=LogKeys.FACILITY, value=value)
            else:
                raise Raise.error(
                    f"Syslog facility: '{value}' not found.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        if isinstance(value, str):
            if value in SysLogKeys.facility_keys:
                self._set_data(
                    key=LogKeys.FACILITY, value=SysLogKeys.facility_keys[value]
                )
            else:
                raise Raise.error(
                    f"Syslog facility name not found: '{value}'",
                    KeyError,
                    self._c_name,
                    currentframe(),
                )
        try:
            s_slog: syslog = self._get_data(key=LogKeys.SYSLOG)  # type: ignore
            s_slog.closelog()
        except:
            pass
        self._set_data(key=LogKeys.SYSLOG, value=None)

    @property
    def level(self) -> int:
        """Return active syslog level.

        ### Returns:
        int - Syslog level value.
        """
        return self._get_data(key=LogKeys.LEVEL)  # type: ignore

    @level.setter
    def level(self, value: Union[int, str]) -> None:
        """Configure syslog level.

        ### Arguments:
        * value: Union[int, str] - Level constant or symbolic name.

        ### Returns:
        None - Resets the syslog handle to apply the new level.

        ### Raises:
        * ValueError: When integer level is not recognised.
        * KeyError: When level name is unknown.
        """
        if isinstance(value, int):
            if value in tuple(SysLogKeys.level_keys.values()):
                self._set_data(key=LogKeys.LEVEL, value=value)
            else:
                raise Raise.error(
                    f"Syslog level: '{value}' not found.",
                    ValueError,
                    self._c_name,
                    currentframe(),
                )
        if isinstance(value, str):
            if value in SysLogKeys.level_keys:
                self._set_data(key=LogKeys.LEVEL, value=SysLogKeys.level_keys[value])
            else:
                raise Raise.error(
                    f"Syslog level name not found: '{value}'",
                    KeyError,
                    self._c_name,
                    currentframe(),
                )
        try:
            s_slog: syslog = self._get_data(key=LogKeys.SYSLOG)  # type: ignore
            s_slog.closelog()
        except:
            pass
        self._set_data(key=LogKeys.SYSLOG, value=None)

    def send(self, message: str) -> None:
        """Emit the message to syslog.

        ### Arguments:
        * message: str - Raw log payload.

        ### Returns:
        None - Message is forwarded to syslog with configured facility/level.
        """
        formatter: BLogFormatter = self._get_data(key=LogKeys.FORMATTER)  # type: ignore
        if formatter:
            message = formatter.format(message, self.name)
        if self._get_data(key=LogKeys.SYSLOG) is None:
            self._set_data(key=LogKeys.SYSLOG, value=syslog)
            self._get_data(key=LogKeys.SYSLOG).openlog(facility=self._get_data(key=LogKeys.FACILITY))  # type: ignore
        self._get_data(key=LogKeys.SYSLOG).syslog(  # type: ignore
            priority=self._get_data(LogKeys.LEVEL), message=message
        )


# #[EOF]#######################################################################
