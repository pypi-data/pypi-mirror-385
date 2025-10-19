# -*- coding: UTF-8 -*-
"""
Author:  Jacek Kotlarski --<szumak@virthost.pl>
Created: 2023-09-04

Purpose: Implement logging client, engine, and processing thread utilities.

These classes orchestrate message queuing, engine dispatch, and background
processing for the logging subsystem.
"""

import time
import threading
from inspect import currentframe

from typing import Optional

from .queue import LoggerQueue

from .keys import LogKeys, LogsLevelKeys

from ..attribtool import NoDynamicAttributes, ReadOnlyClass
from ..raisetool import Raise
from ..basetool.logs import (
    BLoggerQueue,
)
from ..basetool.threads import ThBaseObject
from .engines import *


class _Keys(object, metaclass=ReadOnlyClass):
    """Keys definition class.

    For internal purpose only.
    """

    LCO: str = "__LCO__"
    LEO: str = "__LEO__"


class LoggerClient(BLoggerQueue, NoDynamicAttributes):
    """Provide a user-facing client for enqueuing log messages."""

    def __init__(
        self, queue: Optional[LoggerQueue] = None, name: Optional[str] = None
    ) -> None:
        """Initialise a logging client instance.

        ### Arguments:
        * queue: Optional[LoggerQueue] - Shared queue supplied by a `LoggerEngine`.
        * name: Optional[str] - Optional client prefix added to messages.

        ### Returns:
        None - Constructor.
        """
        # store name
        self.name = name
        # logger queue
        if queue:
            self.logs_queue = queue

    @property
    def name(self) -> Optional[str]:
        """Return the configured client name.

        ### Returns:
        Optional[str] - Client identifier or None.
        """
        return self._get_data(key=LogKeys.NAME, set_default_type=Optional[str])

    @name.setter
    def name(self, name: Optional[str]) -> None:
        """Set the client name.

        ### Arguments:
        * name: Optional[str] - Desired identifier, trimmed when provided.

        ### Returns:
        None - Internal state updated.
        """
        if name is None:
            self._set_data(key=LogKeys.NAME, value=None, set_default_type=Optional[str])
        else:
            self._set_data(
                key=LogKeys.NAME, value=name.strip(), set_default_type=Optional[str]
            )

    def message(self, message: str, log_level: str = LogsLevelKeys.INFO) -> None:
        """Emit a log message at the requested level.

        ### Arguments:
        * message: str - Payload to log.
        * log_level: str - Severity key from `LogsLevelKeys`; defaults to INFO.

        ### Returns:
        None - Message enqueued when a queue is available.

        ### Raises:
        * TypeError: When `log_level` is not a string.
        * KeyError: When `log_level` is not recognised.
        """
        if not isinstance(log_level, str):
            raise Raise.error(
                f"Expected 'log_level' as string type, received: '{type(log_level)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if log_level not in LogsLevelKeys.keys:
            raise Raise.error(
                f"Expected 'log_level' as key from .base_logs.LogsLevelKeys.keys, received: '{log_level}'.",
                KeyError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(message, str):
            message = f"{message}"
        if self.name is not None:
            message = f"[{self.name}] {message}"
        if self.logs_queue:
            self.logs_queue.put(message, log_level)

    @property
    def message_alert(self) -> None:
        """Return None for the ALERT proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_alert.setter
    def message_alert(self, message: str) -> None:
        """Send an ALERT-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with ALERT severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.ALERT)

    @property
    def message_critical(self) -> None:
        """Return None for the CRITICAL proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_critical.setter
    def message_critical(self, message: str) -> None:
        """Send a CRITICAL-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with CRITICAL severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.CRITICAL)

    @property
    def message_debug(self) -> None:
        """Return None for the DEBUG proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_debug.setter
    def message_debug(self, message: str) -> None:
        """Send a DEBUG-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with DEBUG severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.DEBUG)

    @property
    def message_emergency(self) -> None:
        """Return None for the EMERGENCY proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_emergency.setter
    def message_emergency(self, message: str) -> None:
        """Send an EMERGENCY-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with EMERGENCY severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.EMERGENCY)

    @property
    def message_error(self) -> None:
        """Return None for the ERROR proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_error.setter
    def message_error(self, message: str) -> None:
        """Send an ERROR-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with ERROR severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.ERROR)

    @property
    def message_info(self) -> None:
        """Return None for the INFO proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_info.setter
    def message_info(self, message: str) -> None:
        """Send an INFO-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with INFO severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.INFO)

    @property
    def message_notice(self) -> None:
        """Return None for the NOTICE proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_notice.setter
    def message_notice(self, message: str) -> None:
        """Send a NOTICE-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with NOTICE severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.NOTICE)

    @property
    def message_warning(self) -> None:
        """Return None for the WARNING proxy property.

        ### Returns:
        None - Property exposed for write-only usage.
        """

    @message_warning.setter
    def message_warning(self, message: str) -> None:
        """Send a WARNING-level message via the client property interface.

        ### Arguments:
        * message: str - Log payload forwarded with WARNING severity.

        ### Returns:
        None - Delegates to `message`.
        """
        self.message(message, LogsLevelKeys.WARNING)


class LoggerEngine(BLoggerQueue, NoDynamicAttributes):
    """Coordinate engines and dispatch queued log messages."""

    def __init__(self) -> None:
        """Initialise the logging engine with default outputs.

        ### Returns:
        None - Constructor.
        """
        # make logs queue object
        self.logs_queue = LoggerQueue()
        # default logs level configuration
        self._data[LogKeys.NO_CONF] = {}
        self._data[LogKeys.NO_CONF][LogsLevelKeys.INFO] = [LoggerEngineStdout()]
        self._data[LogKeys.NO_CONF][LogsLevelKeys.WARNING] = [LoggerEngineStdout()]
        self._data[LogKeys.NO_CONF][LogsLevelKeys.NOTICE] = [LoggerEngineStdout()]
        self._data[LogKeys.NO_CONF][LogsLevelKeys.DEBUG] = [LoggerEngineStderr()]
        self._data[LogKeys.NO_CONF][LogsLevelKeys.ERROR] = [
            LoggerEngineStdout(),
            LoggerEngineStderr(),
        ]
        self._data[LogKeys.NO_CONF][LogsLevelKeys.CRITICAL] = [
            LoggerEngineStdout(),
            LoggerEngineStderr(),
        ]

    def add_engine(self, log_level: str, engine: ILoggerEngine) -> None:
        """Attach an engine to a specific log level.

        ### Arguments:
        * log_level: str - Severity identifier from `LogsLevelKeys`.
        * engine: ILoggerEngine - Engine instance handling the level.

        ### Returns:
        None - Internal configuration updated.

        ### Raises:
        * TypeError: When `log_level` is not a string or `engine` is not an `ILoggerEngine`.
        """
        if not isinstance(log_level, str):
            raise Raise.error(
                f"Expected 'log_level' as string type, received: '{type(log_level)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if not isinstance(engine, ILoggerEngine):
            raise Raise.error(
                f"Expected ILoggerEngine type, received: '{type(engine)}'.",
                TypeError,
                self._c_name,
                currentframe(),
            )
        if LogKeys.CONF not in self._data:
            self._data[LogKeys.CONF] = {}
            self._data[LogKeys.CONF][log_level] = [engine]
        else:
            if log_level not in self._data[LogKeys.CONF].keys():
                self._data[LogKeys.CONF][log_level] = [engine]
            else:
                test = False
                for i in range(0, len(self._data[LogKeys.CONF][log_level])):
                    if (
                        self._data[LogKeys.CONF][log_level][i].__class__
                        == engine.__class__
                    ):
                        self._data[LogKeys.CONF][log_level][i] = engine
                        test = True
                if not test:
                    self._data[LogKeys.CONF][log_level].append(engine)

    def send(self) -> None:
        """Dequeue pending messages and dispatch them to engines.

        ### Returns:
        None - The queue is drained until empty.
        """
        while True:
            if self.logs_queue is not None:
                item: Optional[tuple[str, ...]] = self.logs_queue.get()
                if item is not None:
                    # get tuple(log_level, message)
                    log_level, message = item
                    # check if has have configured logging subsystem
                    if LogKeys.CONF in self._data and len(self._data[LogKeys.CONF]) > 0:
                        if log_level in self._data[LogKeys.CONF]:
                            for l_eng in self._data[LogKeys.CONF][log_level]:
                                engine: ILoggerEngine = l_eng
                                engine.send(message)
                    else:
                        if log_level in self._data[LogKeys.NO_CONF]:
                            for l_eng in self._data[LogKeys.NO_CONF][log_level]:
                                engine: ILoggerEngine = l_eng
                                engine.send(message)
                else:
                    return None
            else:
                return None


class ThLoggerProcessor(threading.Thread, ThBaseObject, NoDynamicAttributes):
    """Run a background thread that continually drains the log queue."""

    def __init__(self, debug: bool = False) -> None:
        """Initialise processing thread state.

        ### Arguments:
        * debug: bool - When True, emit diagnostic messages via the client.

        ### Returns:
        None - Constructor.
        """
        threading.Thread.__init__(self, name=self._c_name)
        self._stop_event = threading.Event()
        self._debug = debug
        self.daemon = True
        self.sleep_period = 0.2

    @property
    def logger_engine(self) -> Optional[LoggerEngine]:
        """Return the associated logger engine instance.

        ### Returns:
        Optional[LoggerEngine] - Engine reference or None.
        """
        return self._get_data(key=_Keys.LEO, set_default_type=Optional[LoggerEngine])

    @logger_engine.setter
    def logger_engine(self, engine: LoggerEngine) -> None:
        """Assign the logger engine and propagate its queue to the client.

        ### Arguments:
        * engine: LoggerEngine - Engine instance powering the processor.

        ### Returns:
        None - Internal references updated.
        """
        self._set_data(
            key=_Keys.LEO, set_default_type=Optional[LoggerEngine], value=engine
        )
        if self.logger_client and self.logger_engine and self.logger_engine.logs_queue:
            self.logger_client.logs_queue = self.logger_engine.logs_queue

    @property
    def logger_client(self) -> Optional[LoggerClient]:
        """Return the associated logger client instance.

        ### Returns:
        Optional[LoggerClient] - Client reference or None.
        """
        return self._get_data(key=_Keys.LCO, set_default_type=Optional[LoggerClient])

    @logger_client.setter
    def logger_client(self, client: LoggerClient) -> None:
        """Assign the logger client, syncing queues if necessary.

        ### Arguments:
        * client: LoggerClient - Client instance providing message publishing.

        ### Returns:
        None - Internal references updated.
        """
        self._set_data(
            key=_Keys.LCO, set_default_type=Optional[LoggerClient], value=client
        )
        if (
            self.logger_engine
            and self.logger_engine.logs_queue
            and self.logger_client
            and client.logs_queue is None
        ):
            self.logger_client.logs_queue = self.logger_engine.logs_queue

    def run(self) -> None:
        """Process the logging queue until stopped.

        ### Raises:
        * ValueError: When required engine or client references are missing.
        """
        # check list
        if self.logger_engine is None:
            raise Raise.error(
                "LoggerEngine not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        if self.logger_client is None:
            raise Raise.error(
                "LoggerClient not set.",
                ValueError,
                self._c_name,
                currentframe(),
            )
        if self._debug:
            self.logger_client.message_debug = f"[{self._c_name}] starting..."
        # run
        while not self.stopped:
            self.logger_engine.send()
            time.sleep(self.sleep_period)
        if self._debug:
            self.logger_client.message_debug = f"[{self._c_name}] stopped."
        self.logger_engine.send()

    def stop(self) -> None:
        """Request the background thread to stop.

        ### Returns:
        None - Signals the internal stop event.
        """
        if self._debug and self.logger_client:
            self.logger_client.message_debug = f"[{self._c_name}] stopping..."
        if self._stop_event:
            self._stop_event.set()

    @property
    def stopped(self) -> bool:
        """Return True when the stop event has been set.

        ### Returns:
        bool - Stop flag state.
        """
        if self._stop_event:
            return self._stop_event.is_set()
        return True


# #[EOF]#######################################################################
