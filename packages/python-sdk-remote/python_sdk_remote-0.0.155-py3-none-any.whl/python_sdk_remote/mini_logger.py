import logging
import os
import sys
# from enum import Enum
import inspect
from .constants_src_mini_logger_and_logger import LogMessageSeverity, StartEndEnum

# TODO LOGGER_MINIMAL_SEVERITY_DEFAULT
LOGGER_MINIMUM_SEVERITY = os.getenv("LOGGER_MINIMUM_SEVERITY", "INFORMATION").upper()

# Convert enum values to logging levels
def _get_logging_level(severity):
    if isinstance(severity, LogMessageSeverity):
        if severity == LogMessageSeverity.DEBUG:
            return logging.DEBUG
        elif severity == LogMessageSeverity.INFORMATION:
            return logging.INFO
        elif severity == LogMessageSeverity.WARNING:
            return logging.WARNING
        elif severity == LogMessageSeverity.ERROR:
            return logging.ERROR
        elif severity == LogMessageSeverity.CRITICAL:
            return logging.CRITICAL
        else:
            return logging.INFO
    elif isinstance(severity, str):
        if severity == "INFORMATION":
            return logging.INFO
        else:
            return getattr(logging, severity, logging.INFO)
    else:
        return logging.INFO

# logging expects NOTSET/DEBUG/INFO/WARNING/ERROR/CRITICAL
if LOGGER_MINIMUM_SEVERITY.isdigit():
    # TODO logger_minimal_severity_default_value
    logger_minimum_severity = int(LOGGER_MINIMUM_SEVERITY)
    # TODO Change Magic Numbers and use the values from Logger.MessageSeverity
    if logger_minimum_severity < StartEndEnum.START.value:
        # TODO LOGGER_MINIMAL_SEVERITY_DEFAULT_NAME =
        # TODO Change "DEBUG", "INFORMATION", "WARNING" ... into enum values from Logger.LogMessageSeverity
        LOGGER_MINIMUM_SEVERITY = LogMessageSeverity.DEBUG
    elif logger_minimum_severity < LogMessageSeverity.WARNING.value:
        LOGGER_MINIMUM_SEVERITY = LogMessageSeverity.INFORMATION
    elif logger_minimum_severity < LogMessageSeverity.ERROR.value:
        LOGGER_MINIMUM_SEVERITY = LogMessageSeverity.WARNING
    elif logger_minimum_severity < LogMessageSeverity.CRITICAL.value:
        LOGGER_MINIMUM_SEVERITY = LogMessageSeverity.ERROR
    else:
        LOGGER_MINIMUM_SEVERITY = LogMessageSeverity.CRITICAL

logging.basicConfig(level=_get_logging_level(LOGGER_MINIMUM_SEVERITY), stream=sys.stdout,
                    format="%(asctime)s - %(message)s")
logger = logging.getLogger(__name__)


class MiniLogger:
    # TODO Can we so one generic function call by all

    _is_write_to_sql = False  # Should be always False in MiniLogger

    @staticmethod
    def _log(level: LogMessageSeverity, start_or_end: StartEndEnum = None, log_message: str = None, **kwargs):
        """
        Private method to unify all log methods

        Parameters:
            level (MessageSeverity): log level
            log_message (str): The message to be printed.
        """
        object = kwargs.get("object")

        if level.name == "INFORMATION":
            method_name = "info"
        else:
            method_name = level.name.lower()
        method = getattr(logger, method_name)
        if not start_or_end:
            action_name = level.name
        else:
            action_name = start_or_end.name
        stk = inspect.stack()[2]
        function = stk.function
        line = stk.lineno
        if object is None:
            method(f"Function: {function}, Line: {line}; {action_name} - {log_message}")
        else:
            method(f"Function: {function}, Line: {line}; {action_name} - {log_message} - {object}")

    @staticmethod
    # TODO Add a new file called align_logger_and_minilogger_test.py, which makes sure the signature of all methods of MiniLogger and Logger are the same and we can change from MiniLogger to Logger and vice versa by changing only one line in our code. If we should change the signatures, we should make them backward compatible.  # noqa E501
    def start(log_message: str = None, **kwargs):
        """
        Print a log message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        MiniLogger._log(LogMessageSeverity.DEBUG, StartEndEnum.START, log_message, **kwargs)

    @staticmethod
    def end(log_message: str = None, **kwargs):
        """
        Print a log message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        MiniLogger._log(LogMessageSeverity.DEBUG, StartEndEnum.END, log_message, **kwargs)

    # TODO convert all those methods (debug, info, warning, error) into one unified private method
    # TODO Add to the unified private method print of the name of method, version
    # and line number of the calling function/method to the mini_logger methods
    @staticmethod
    def debug(log_message: str = None, **kwargs):
        """
        Print a log message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        MiniLogger._log(LogMessageSeverity.DEBUG, log_message=log_message, **kwargs)

    @staticmethod
    def info(log_message: str = None, **kwargs):
        """
        Print a log message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        MiniLogger._log(LogMessageSeverity.INFORMATION, log_message=log_message, **kwargs)

    @staticmethod
    def warning(log_message: str = None, **kwargs):
        """
        Print a log message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        # TODO Add the source of the message - We should add the object or at least some parts of it  # noqa E501
        MiniLogger._log(LogMessageSeverity.WARNING, log_message=log_message, **kwargs)

    @staticmethod
    def error(log_message: str = None, **kwargs):
        """
        Print a log error message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        MiniLogger._log(LogMessageSeverity.ERROR, log_message=log_message, **kwargs)

    @staticmethod
    def exception(self, log_message: str = None, **kwargs):
        """
        Print a log error message with the current time.

        Parameters:
            log_message (str): The message to be printed.
        """
        object = kwargs.get("object")
        if isinstance(object, Exception):
            exception = object
        elif isinstance(object, dict):
            exception = object.get("exception")
        else:
            exception = None

        if object is None:
            logger.exception(f"EXCEPTION - {log_message}")
        else:
            logger.exception(f"EXCEPTION- {log_message} - {object}", exc_info=exception)

    def is_write_to_sql(self):
        return self._is_write_to_sql
