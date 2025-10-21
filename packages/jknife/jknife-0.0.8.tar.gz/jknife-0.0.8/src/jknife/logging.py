import logging
import logging.config
from os import mkdir, listdir
from typing_extensions import Annotated, Doc
from settings import LOG_SETTINGS, DEBUG_MODE


# create logs folder to store log files.
if "logs" not in listdir():
    mkdir("logs")

# set logging config from settings.py
# apply default key:value for dictConfig
LOG_SETTINGS.update({"version": 1, "disable_existing_loggers": False})
logging.config.dictConfig(config=LOG_SETTINGS)


# define LoggerMgmt for multiple logging
class LoggerMgmt:
    """
    This class is designed to implement multiple logging system in FastAPI.

    :param logger_names: assign the logger name that you want to use in specific area.
                         you can define it in settings.py with LOG_SETTINGS and *_LOGGER_LIST
    """

    def __init__(self,
                 logger_names: Annotated[list[str],
                                         Doc("assign the name of loggers to record activities")]):
        self.__loggers = [logging.getLogger(name=name) for name in logger_names]
        if DEBUG_MODE:
            uvicorn_logger = logging.getLogger(name="uvicorn")
            uvicorn_logger.setLevel(level="DEBUG")
            self.__loggers.append(uvicorn_logger)

    def critical(self, msg: Annotated[str,
                                      Doc("log message for critical level")]) -> None:
        for logger in self.__loggers:
            logger.critical(msg=msg)

        return None

    def error(self, msg: Annotated[str,
                                   Doc("log message for error level")]) -> None:
        for logger in self.__loggers:
            logger.error(msg=msg)

        return None

    def warning(self, msg: Annotated[str,
                                     Doc("log message for warning level")]) -> None:
        for logger in self.__loggers:
            logger.warning(msg=msg)

        return None

    def info(self, msg: Annotated[str,
                                  Doc("log message for info level")]) -> None:
        for logger in self.__loggers:
            logger.info(msg=msg)

        return None

    def debug(self, msg: Annotated[str,
                                  Doc("log message for debug level")]) -> None:
        for logger in self.__loggers:
            logger.debug(msg=msg)

        return None