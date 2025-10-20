# -*- coding: utf-8 -*-
"""
Author:  Jacek 'Szumak' Kotlarski --<szumak@virthost.pl>
Created: 2024-10-07

Purpose: EDMC plugins individual logging subsystem classes.
"""

from inspect import currentframe
import logging
import os
from typing import Union, Optional, List, Dict
from logging.handlers import RotatingFileHandler
from queue import Queue, SimpleQueue

from ..edmctool.system import EnvLocal

from ..attribtool import ReadOnlyClass, NoDynamicAttributes
from ..basetool.data import BData
from ..raisetool import Raise


class _Keys(object, metaclass=ReadOnlyClass):
    """Internal Keys container class."""

    LOG_DATA: str = "__logger_data__"
    LOG_LEVEL: str = "__logger_level__"
    LOG_QUEUE: str = "__logger_queue__"
    LP_ENGINE: str = "__log_processor_engine__"
    LP_NAME: str = "__log_processor_name__"
    LP_LOGS_DIR: str = "__log_processor_logs_dir__"
    LP_MAX_BYTES: str = "__log_processor_max_bytes__"
    LP_BACKUP_COUNT: str = "__log_processor_backup_count__"


class Log(BData):
    """Create Log container class."""

    def __init__(self, level: int) -> None:
        """Class constructor.

        ### Arguments:
        * level: int - Logging level for this log instance.
        """
        # init data list
        self._set_data(key=_Keys.LOG_DATA, value=[], set_default_type=List)

        # init default loglevel
        ll_test = LogLevels()
        self._set_data(key=_Keys.LOG_LEVEL, value=ll_test.debug, set_default_type=int)

        if isinstance(level, int) and ll_test.has_key(level):
            self._set_data(key=_Keys.LOG_LEVEL, value=level)
        else:
            raise Raise.error(
                f"Int type level expected, '{type(level)}' received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def loglevel(self) -> int:
        """Return loglevel.

        ### Returns:
        int - The configured log level.
        """
        return self._get_data(key=_Keys.LOG_LEVEL)  # type: ignore

    @property
    def log(self) -> List[str]:
        """Get list of logs.

        ### Returns:
        List[str] - List of log messages.
        """
        return self._get_data(
            key=_Keys.LOG_DATA,
        )  # type: ignore

    @log.setter
    def log(self, arg: Optional[Union[List, str]]) -> None:
        """Set data log.

        ### Arguments:
        * arg: Optional[Union[List, str]] - Log message or list of messages to append, None to clear.
        """
        if arg is None or (isinstance(arg, List) and not bool(arg)):
            # cleanup list of logs
            self._set_data(
                key=_Keys.LOG_DATA,
                value=[],
            )
        if isinstance(arg, List):
            for msg in arg:
                self.log.append(f"{msg}")
        elif arg is None:
            pass
        else:
            self.log.append(f"{arg}")


class LogProcessor(BData):
    """Log processor access API."""

    def __init__(
        self,
        name: str,
        logs_dir: Optional[str] = None,
        max_bytes: int = 100000,
        backup_count: int = 5,
    ) -> None:
        """Create instance class object for processing single message.

        ### Arguments:
        * name: str - Name of the application or logger.
        * logs_dir: Optional[str] - Directory path for log files. Defaults to tmpdir if not provided.
        * max_bytes: int - Maximum size of log file in bytes before rotation. Defaults to 100000.
        * backup_count: int - Number of backup log files to keep. Defaults to 5.
        """
        # name of app
        self._set_data(key=_Keys.LP_NAME, value=name, set_default_type=str)
        # logs directory
        if logs_dir is None:
            logs_dir = EnvLocal().tmpdir
        self._set_data(
            key=_Keys.LP_LOGS_DIR,
            value=logs_dir,
            set_default_type=str,
        )
        # max bytes
        self._set_data(
            key=_Keys.LP_MAX_BYTES,
            value=max_bytes,
            set_default_type=int,
        )
        # backup count
        self._set_data(
            key=_Keys.LP_BACKUP_COUNT,
            value=backup_count,
            set_default_type=int,
        )
        self.loglevel = LogLevels().notset
        self.__logger_init()

    def __del__(self) -> None:
        """Destroy log instance."""
        self.close()

    @property
    def __engine(self) -> logging.Logger:
        """Return logger instance.

        ### Returns:
        logging.Logger - The underlying Python logging engine.
        """
        return self._get_data(key=_Keys.LP_ENGINE)  # type: ignore

    @__engine.setter
    def __engine(self, arg: logging.Logger) -> None:
        """Sets engine instance.

        ### Arguments:
        * arg: logging.Logger - Logger engine instance to assign.
        """
        self._set_data(key=_Keys.LP_ENGINE, value=arg, set_default_type=logging.Logger)

    def __logger_init(self) -> None:
        """Initialize logger engine."""
        self.close()

        self.__engine = logging.getLogger(self._get_data(key=_Keys.LP_NAME))
        self.__engine.setLevel(LogLevels().debug)

        log_handler = RotatingFileHandler(
            filename=os.path.join(
                f"{self._get_data(key=_Keys.LP_LOGS_DIR)}",
                f"{self._get_data(key=_Keys.LP_NAME)}.log",
            ),
            maxBytes=self._get_data(key=_Keys.LP_MAX_BYTES),  # type: ignore
            backupCount=self._get_data(key=_Keys.LP_BACKUP_COUNT),  # type: ignore
        )

        log_handler.setLevel(self.loglevel)
        log_handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
        self.__engine.addHandler(log_handler)
        self.__engine.info("Logger initialization complete")

    def close(self) -> None:
        """Close log subsystem."""
        if self.__engine is not None:
            for handler in self.__engine.handlers:
                handler.close()
                self.__engine.removeHandler(handler)

    def send(self, message: Log) -> None:
        """Send single message to log engine.

        ### Arguments:
        * message: Log - Log object containing messages and log level.

        ### Raises:
        * TypeError: Provided argument is not a Log instance.
        """
        if self.__engine is None:
            return
        lgl = LogLevels()
        if isinstance(message, Log):
            if message.loglevel == lgl.critical:
                for msg in message.log:
                    self.__engine.critical("%s", msg)
            elif message.loglevel == lgl.debug:
                for msg in message.log:
                    self.__engine.debug("%s", msg)
            elif message.loglevel == lgl.error:
                for msg in message.log:
                    self.__engine.error("%s", msg)
            elif message.loglevel == lgl.info:
                for msg in message.log:
                    self.__engine.info("%s", msg)
            elif message.loglevel == lgl.warning:
                for msg in message.log:
                    self.__engine.warning("%s", msg)
            else:
                for msg in message.log:
                    self.__engine.notset("%s", msg)  # type: ignore
        else:
            raise Raise.error(
                f"Log type expected, {type(message)} received.",
                TypeError,
                self._c_name,
                currentframe(),
            )

    @property
    def loglevel(self) -> int:
        """Property that returns loglevel.

        ### Returns:
        int - The configured log level.
        """
        return self._get_data(
            key=_Keys.LOG_LEVEL, default_value=LogLevels().notset
        )  # type: ignore

    @loglevel.setter
    def loglevel(self, arg: int) -> None:
        """Setter for log level parameter.

        ### Arguments:
        * arg: int - Log level constant from LogLevels.
        """
        if self.loglevel == arg:
            log = Log(LogLevels().debug)
            log.log = "LogLevel has not changed"
            self.send(log)
            return
        ll_test = LogLevels()
        if isinstance(arg, int) and ll_test.has_key(arg):
            self._set_data(key=_Keys.LOG_LEVEL, value=arg, set_default_type=int)
        else:
            tmp = "Unable to set LogLevel to {}, defaulted to INFO"
            log = Log(LogLevels().warning)
            log.log = tmp.format(arg)
            self.send(log)
            self._set_data(
                key=_Keys.LOG_LEVEL, value=LogLevels().info, set_default_type=int
            )
        self.__logger_init()


class LogClient(BData):
    """Log client class API."""

    def __init__(self, queue: Union[Queue, SimpleQueue]) -> None:
        """Create instance class object.

        ### Arguments:
        * queue: Union[Queue, SimpleQueue] - Queue object for sending log messages.
        """
        self._set_data(
            key=_Keys.LOG_QUEUE,
            value=queue,
            set_default_type=Union[Queue, SimpleQueue],
        )

    @property
    def queue(self) -> Union[Queue, SimpleQueue]:
        """Give me queue object.

        ### Returns:
        Union[Queue, SimpleQueue] - The queue object for log messages.
        """
        return self._get_data(
            key=_Keys.LOG_QUEUE,
        )  # type: ignore

    @property
    def critical(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @critical.setter
    def critical(self, message: Union[str, List]) -> None:
        """Setter for critical messages.

        ### Arguments:
        * message: Union[str, List] - Critical level log message or list of messages.
        """
        log = Log(LogLevels().critical)
        log.log = message
        self.queue.put(log)

    @property
    def debug(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @debug.setter
    def debug(self, message: Union[str, List]) -> None:
        """Setter for debug messages.

        ### Arguments:
        * message: Union[str, List] - Debug level log message or list of messages.
        """
        log = Log(LogLevels().debug)
        log.log = message
        self.queue.put(log)

    @property
    def error(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @error.setter
    def error(self, message: Union[str, List]) -> None:
        """Setter for error messages.

        ### Arguments:
        * message: Union[str, List] - Error level log message or list of messages.
        """
        log = Log(LogLevels().error)
        log.log = message
        self.queue.put(log)

    @property
    def info(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @info.setter
    def info(self, message: Union[str, List]) -> None:
        """Setter for info messages.

        ### Arguments:
        * message: Union[str, List] - Info level log message or list of messages.
        """
        log = Log(LogLevels().info)
        log.log = message
        self.queue.put(log)

    @property
    def warning(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @warning.setter
    def warning(self, message: Union[str, List]) -> None:
        """Setter for warning messages.

        ### Arguments:
        * message: Union[str, List] - Warning level log message or list of messages.
        """
        log = Log(LogLevels().warning)
        log.log = message
        self.queue.put(log)

    @property
    def notset(self) -> str:
        """Property that returns nothing.

        ### Returns:
        str - Empty string.
        """
        return ""

    @notset.setter
    def notset(self, message: Union[str, List]) -> None:
        """Setter for notset level messages.

        ### Arguments:
        * message: Union[str, List] - Message or list of messages to log.
        """
        log = Log(LogLevels().notset)
        log.log = message
        self.queue.put(log)


class LogLevels(NoDynamicAttributes):
    """Log levels keys.

    This is a container class with properties that return the proper
    logging levels defined in the logging module.
    """

    __keys: Dict[int, bool] = None  # type: ignore
    __txt: Dict[str, int] = None  # type: ignore

    def __init__(self) -> None:
        """Create Log instance."""
        # loglevel initialization database
        self.__keys = {
            self.info: True,
            self.debug: True,
            self.warning: True,
            self.error: True,
            self.notset: True,
            self.critical: True,
        }
        self.__txt = {
            "INFO": self.info,
            "DEBUG": self.debug,
            "WARNING": self.warning,
            "ERROR": self.error,
            "CRITICAL": self.critical,
            "NOTSET": self.notset,
        }

    def get(self, level: Union[int, str]) -> Optional[int]:
        """Get int log level."""
        if level in self.__txt:
            return self.__txt[level]
        return None

    def has_key(self, level: Union[int, str]) -> bool:
        """Check, if level is in proper keys.

        ### Returns:
        bool - True if level is valid, False otherwise.
        """
        if level in self.__keys or level in self.__txt:
            return True
        return False

    @property
    def info(self) -> int:
        """Return info level.

        ### Returns:
        int - The INFO log level constant.
        """
        return logging.INFO

    @property
    def debug(self) -> int:
        """Return debug level.

        ### Returns:
        int - The DEBUG log level constant.
        """
        return logging.DEBUG

    @property
    def warning(self) -> int:
        """Return warning level.

        ### Returns:
        int - The WARNING log level constant.
        """
        return logging.WARNING

    @property
    def error(self) -> int:
        """Return error level.

        ### Returns:
        int - The ERROR log level constant.
        """
        return logging.ERROR

    @property
    def critical(self) -> int:
        """Return critical level.

        ### Returns:
        int - The CRITICAL log level constant.
        """
        return logging.CRITICAL

    @property
    def notset(self) -> int:
        """Return notset level.

        ### Returns:
        int - The NOTSET log level constant.
        """
        return logging.NOTSET


# #[EOF]#######################################################################
