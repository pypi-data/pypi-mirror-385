# -*- coding: utf-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-10-07

Purpose: EDMC plugins individual logging subsystem base classes.
"""

from queue import SimpleQueue, Queue
from threading import Thread
from typing import Union

from ..basetool.data import BData
from ..attribtool import ReadOnlyClass

from .logs import LogClient, LogProcessor


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    # base logs
    LOGGER: str = "__logger__"
    LOG_PROCESSOR: str = "__logs_processor__"
    LOG_QUEUE: str = "__logger_queue__"
    TH_LOGGER: str = "__th_logger__"


class BLogProcessor(BData):
    """BLogProcessor base class.

    Container for logger processor methods.
    """

    @property
    def th_log(self) -> Thread:
        """Return the thread logger handler instance.

        ### Returns:
        Thread - The thread responsible for log processing.
        """
        return self._get_data(key=_Keys.TH_LOGGER, default_value=None)  # type: ignore

    @th_log.setter
    def th_log(self, value: Thread) -> None:
        """Assign the thread logger handler.

        ### Arguments:
        * value: Thread - The thread instance to use for log processing.
        """
        self._set_data(key=_Keys.TH_LOGGER, value=value, set_default_type=Thread)

    @property
    def qlog(self) -> Union[Queue, SimpleQueue]:
        """Return the logging queue instance.

        ### Returns:
        Union[Queue, SimpleQueue] - The queue used for log message passing.
        """
        return self._get_data(key=_Keys.LOG_QUEUE, default_value=None)  # type: ignore

    @qlog.setter
    def qlog(self, value: Union[Queue, SimpleQueue]) -> None:
        """Assign the logging queue instance.

        ### Arguments:
        * value: Union[Queue, SimpleQueue] - Queue instance for log processing.
        """
        self._set_data(
            key=_Keys.LOG_QUEUE,
            value=value,
            set_default_type=Union[Queue, SimpleQueue],
        )

    @property
    def log_processor(self) -> LogProcessor:
        """Return the log processor handler.

        ### Returns:
        LogProcessor - The processor instance responsible for log message handling.
        """
        return self._get_data(
            key=_Keys.LOG_PROCESSOR, default_value=None
        )  # type: ignore

    @log_processor.setter
    def log_processor(self, value: LogProcessor) -> None:
        """Assign the log processor instance.

        ### Arguments:
        * value: LogProcessor - Processor instance to handle log messages.
        """
        self._set_data(
            key=_Keys.LOG_PROCESSOR, value=value, set_default_type=LogProcessor
        )


class BLogClient(BData):
    """BLogClass base class.

    Container for logger methods.
    """

    @property
    def logger(self) -> LogClient:
        """Return the logger client handler.

        ### Returns:
        LogClient - The client interface for logging operations.
        """
        return self._get_data(key=_Keys.LOGGER, default_value=None)  # type: ignore

    @logger.setter
    def logger(self, arg: LogClient) -> None:
        """Assign the logger client instance.

        ### Arguments:
        * arg: LogClient - Logger client instance to use for logging operations.
        """
        self._set_data(key=_Keys.LOGGER, value=arg, set_default_type=LogClient)


# #[EOF]#######################################################################
