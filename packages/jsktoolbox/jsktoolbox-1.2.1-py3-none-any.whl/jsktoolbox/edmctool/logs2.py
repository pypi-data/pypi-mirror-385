# -*- coding: utf-8 -*-
"""
logs2.py
Author : Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 16.10.2025, 20:55:52

Purpose: Logging server and component mixin for EDMC toolbox.
Description:
  This module provides a logging server that manages logging destinations
  and a mixin for components to easily attach to the logging server.
"""

from __future__ import annotations
from inspect import currentframe

from re import DEBUG, L
import threading
import time
from pathlib import Path
from typing import TYPE_CHECKING, Iterable, List, Optional, cast, Union
from venv import logger

from ..attribtool import ReadOnlyClass
from ..basetool.data import BData
from ..logstool import (
    LoggerClient,
    LoggerEngine,
    LoggerEngineFile,
    LoggerEngineStdout,
    LogFormatterDateTime,
    LogsLevelKeys,
    ThLoggerProcessor,
)
from ..basetool import BLoggerQueue
from ..raisetool import Raise


if TYPE_CHECKING:
    from ..logstool import LoggerQueue


class _Keys(object, metaclass=ReadOnlyClass):
    """Predefined keys for logging configuration."""

    APP_NAME: str = "__app_name__"
    LEC: str = "__logger_engine_config__"
    LOGGER_CLIENT: str = "__logger_client__"
    LOG_PATH: str = "__log_path__"


class LoggerEngineConfig(BData):
    """Configuration data for logger engine destinations."""

    class _LECKeys(object, metaclass=ReadOnlyClass):
        """Predefined keys for logger engine configuration."""

        BACKUP_COUNT: str = "backup_count"
        CONSOLE_LEVELS: str = "console_levels"
        CONSOLE_OBJ: str = "__console_obj__"
        FILE_LEVELS: str = "file_levels"
        FILE_OBJ: str = "__file_obj__"
        MAX_FILE_SIZE: str = "max_file_size"
        DEBUG: str = "debug_mode"

    class Console(BData):
        """Console logging configuration."""

        def __init__(self) -> None:
            """Constructor."""
            self._set_data(
                key=LoggerEngineConfig._LECKeys.CONSOLE_LEVELS,
                set_default_type=str,
                value=LogsLevelKeys.INFO,
            )

        @property
        def levels(self) -> str:
            """Return the configured console log levels.

            ### Returns:
            str - log levels as str.
            """
            level = self._get_data(
                key=LoggerEngineConfig._LECKeys.CONSOLE_LEVELS,
            )
            return level or LogsLevelKeys.INFO

        @levels.setter
        def levels(self, obj: str) -> None:
            """Assign the console log levels.

            ### Arguments:
            * obj: str - List of log levels or None.
            """
            self._set_data(
                key=LoggerEngineConfig._LECKeys.CONSOLE_LEVELS,
                value=obj,
                set_default_type=str,
            )

    class File(BData):
        """File logging configuration."""

        def __init__(self) -> None:
            """Constructor."""
            self._set_data(
                key=LoggerEngineConfig._LECKeys.FILE_LEVELS,
                set_default_type=str,
                value=LogsLevelKeys.INFO,
            )
            self._set_data(
                key=LoggerEngineConfig._LECKeys.MAX_FILE_SIZE,
                set_default_type=Optional[int],
                value=None,
            )
            self._set_data(
                key=LoggerEngineConfig._LECKeys.BACKUP_COUNT,
                set_default_type=int,
                value=0,
            )

        @property
        def levels(self) -> str:
            """Return the configured file log levels.

            ### Returns:
            str - Log levels as str.
            """
            level = self._get_data(
                key=LoggerEngineConfig._LECKeys.FILE_LEVELS,
            )
            return level or LogsLevelKeys.INFO

        @levels.setter
        def levels(self, obj: str) -> None:
            """Assign the file log levels.

            ### Arguments:
            * obj: str - log levels as str.
            """
            self._set_data(
                key=LoggerEngineConfig._LECKeys.FILE_LEVELS,
                value=obj,
                set_default_type=str,
            )

        @property
        def max_file_size(self) -> Optional[int]:
            """Return the maximum file size in bytes.

            ### Returns:
            Optional[int] - Maximum file size in bytes or None.
            """
            return self._get_data(
                key=LoggerEngineConfig._LECKeys.MAX_FILE_SIZE,
            )

        @max_file_size.setter
        def max_file_size(self, obj: Optional[int]) -> None:
            """Assign the maximum file size in bytes.

            ### Arguments:
            * obj: Optional[int] - Maximum file size in bytes or None.
            """
            self._set_data(
                key=LoggerEngineConfig._LECKeys.MAX_FILE_SIZE,
                value=obj,
            )

        @property
        def backup_count(self) -> int:
            """Return the number of backup files to keep.

            ### Returns:
            int - Number of backup files.
            """
            count = self._get_data(
                key=LoggerEngineConfig._LECKeys.BACKUP_COUNT,
            )
            return count or 0

        @backup_count.setter
        def backup_count(self, obj: int) -> None:
            """Assign the number of backup files to keep.

            ### Arguments:
            * obj: int - Number of backup files.
            """
            self._set_data(key=LoggerEngineConfig._LECKeys.BACKUP_COUNT, value=obj)

    def __init__(self) -> None:
        """Constructor."""
        self._set_data(
            key=LoggerEngineConfig._LECKeys.CONSOLE_OBJ,
            value=LoggerEngineConfig.Console(),
            set_default_type=LoggerEngineConfig.Console,
        )
        self._set_data(
            key=LoggerEngineConfig._LECKeys.FILE_OBJ,
            value=LoggerEngineConfig.File(),
            set_default_type=LoggerEngineConfig.File,
        )

    @property
    def debug(self) -> bool:
        """Return the debug mode.

        ### Returns:
        bool - Debug mode.
        """
        debug = self._get_data(
            key=LoggerEngineConfig._LECKeys.DEBUG,
        )
        if debug is None:
            return False
        return cast(bool, debug)

    @debug.setter
    def debug(self, obj: bool) -> None:
        """Assign the debug mode.

        ### Arguments:
        * obj: bool - Debug mode.
        """
        self._set_data(
            key=LoggerEngineConfig._LECKeys.DEBUG,
            value=obj,
            set_default_type=bool,
        )

    @property
    def console(self) -> LoggerEngineConfig.Console:
        """Return the console logging configuration.

        ### Returns:
        LoggerEngineConfig.Console - Console configuration instance.
        """
        console = self._get_data(
            key=LoggerEngineConfig._LECKeys.CONSOLE_OBJ,
        )
        if console is None:
            raise Raise.error(
                "LoggerEngineConfig console not initialized.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )
        return cast(LoggerEngineConfig.Console, console)

    @property
    def file(self) -> LoggerEngineConfig.File:
        """Return the file logging configuration.

        ### Returns:
        LoggerEngineConfig.File - File configuration instance.
        """
        file = self._get_data(
            key=LoggerEngineConfig._LECKeys.FILE_OBJ,
        )
        if file is None:
            raise Raise.error(
                "LoggerEngineConfig file not initialized.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )
        return cast(LoggerEngineConfig.File, file)


class LoggingServer(ThLoggerProcessor):
    """Run the logging processor thread with predefined engine destinations.

    The server configures a `LoggerEngine`, registers file/stdout sinks, and exposes
    helpers to create additional `LoggerClient` instances that reuse the shared queue.
    """

    def __init__(
        self,
        application_name: str,
        log_path: Path,
        engine_config: Optional[LoggerEngineConfig] = None,
        debug: bool = False,
    ) -> None:
        """Initialise the logging server with configured destinations.

        ### Arguments:
        * application_name: str - Friendly application name used in log prefixes.
        * log_path: Path - Target file for persistent log storage.
        * engine_config: Optional[LoggerEngineConfig] - Optional configuration for the logger engine.
        * debug: bool - Enables verbose lifecycle logging when True.

        ### Returns:
        None - Constructor.
        """
        super().__init__(debug=debug)
        # self._debug = debug
        self._set_data(key=_Keys.APP_NAME, value=application_name, set_default_type=str)
        self._set_data(key=_Keys.LOG_PATH, value=log_path, set_default_type=Path)
        if engine_config is None:
            engine_config = LoggerEngineConfig()
        self._set_data(
            key=_Keys.LEC,
            value=engine_config,
            set_default_type=LoggerEngineConfig,
        )
        engine = LoggerEngine()
        self.logger_engine = engine
        self._configure_engine()
        self.logger_client = LoggerClient(engine.logs_queue, name=self._c_name)

    def _configure_engine(self) -> None:
        """Configure file and console engines attached to the logger engine."""
        engine: Optional[LoggerEngine] = self.logger_engine
        log_path: Optional[Path] = self._get_data(_Keys.LOG_PATH)
        if engine is None or log_path is None:
            raise Raise.error(
                "LoggingServer initialisation incomplete.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )
        config: Optional[LoggerEngineConfig] = self._get_data(_Keys.LEC)
        if config is None:
            raise Raise.error(
                "LoggingServer engine configuration missing.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )

        app: Optional[str] = self._get_data(_Keys.APP_NAME)
        if app is None:
            app = ""

        formatter = LogFormatterDateTime()
        file_engine = LoggerEngineFile(name=app, formatter=formatter, buffered=False)
        file_engine.logdir = str(log_path.parent)
        file_engine.logfile = log_path.name
        file_engine.rotation_max_bytes = config.file.max_file_size
        file_engine.rotation_backup_count = config.file.backup_count

        console_engine = LoggerEngineStdout(
            name=app, formatter=formatter, buffered=False
        )

        lvl_con = False
        lvl_file = False
        for level in (
            LogsLevelKeys.DEBUG,
            LogsLevelKeys.INFO,
            LogsLevelKeys.NOTICE,
            LogsLevelKeys.WARNING,
            LogsLevelKeys.ERROR,
            LogsLevelKeys.CRITICAL,
        ):
            if config.debug or level == config.console.levels:
                lvl_con = True
            if config.debug or level == config.file.levels:
                lvl_file = True
            if lvl_con:
                engine.add_engine(level, console_engine)
            if lvl_file:
                engine.add_engine(level, file_engine)

    @property
    def logs_queue(self) -> Optional[LoggerQueue]:
        """Expose the server queue for external clients.

        ### Returns:
        Optional[LoggerQueue] - Shared logging queue instance or None.
        """
        engine: Optional[LoggerEngine] = self.logger_engine
        if engine is None:
            return None
        return engine.logs_queue

    def create_client(self, name: Optional[str] = None) -> LoggerClient:
        """Create a logger client attached to the server queue.

        ### Arguments:
        * name: Optional[str] - Friendly component name used in log prefixes.

        ### Returns:
        LoggerClient - Configured client instance.

        ### Raises:
        * RuntimeError: When the server queue is not available.
        """
        queue: Optional[LoggerQueue] = self.logs_queue
        if queue is None:
            raise Raise.error(
                "LoggingServer not initialised.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )

        return LoggerClient(queue, name=name)

    def shutdown(self, timeout: float = 5.0) -> None:
        """Stop the processor thread and wait for graceful completion.

        ### Arguments:
        * timeout: float - Maximum seconds to wait for termination.

        ### Returns:
        None - The thread is joined.
        """
        self.stop()
        self.join(timeout=timeout)


class LoggingComponentMixin(BLoggerQueue):
    """Reusable mixin that binds components to the logging server."""

    def attach_logger(self, server: LoggingServer, name: Optional[str] = None) -> None:
        """Bind the component to the server queue and create a dedicated client.

        ### Arguments:
        * server: LoggingServer - Active logging server instance.
        * name: Optional[str] - Optional override for the client name.

        ### Returns:
        None - Internal logger client configured.
        """
        queue: Optional[LoggerQueue] = server.logs_queue
        if queue is None:
            raise Raise.error(
                "Logging server queue not available.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )

        self.logs_queue = queue
        resolved_name: str = name or self._c_name

        self._set_data(
            key=_Keys.LOGGER_CLIENT,
            value=LoggerClient(queue, name=resolved_name),
            set_default_type=LoggerClient,
        )

    @property
    def logger(self) -> LoggerClient:
        """Return the attached logger client.

        ### Returns:
        LoggerClient - Component-specific logger client.

        ### Raises:
        * RuntimeError: When the logger has not been attached.
        """
        logger: Optional[LoggerClient] = self._get_data(_Keys.LOGGER_CLIENT)
        if logger is None:
            raise Raise.error(
                "Logger client not attached.",
                RuntimeError,
                self._c_name,
                currentframe(),
            )

        return cast(LoggerClient, logger)


# #[EOF]#######################################################################
