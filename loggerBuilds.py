import logging
import os
from logging import FileHandler, StreamHandler


#if for some reason the logs folder was deleted create a new one
LOG_DIR = "logs"
os.makedirs(LOG_DIR, exist_ok=True)

loggers = {}

def get_logger(name, file_name, default_level=logging.INFO, to_stdout=False):
    if(name in loggers):
        return loggers[name]

    logger = logging.getLogger(name)
    logger.setLevel(default_level)

    formatter = logging.Formatter(fmt="%(asctime)s %(levelname)s: %(message)s | request #%(_request_id)d",
                                  datefmt="%d-%m-%Y %H:%M:%S.%f")

    file_handler = FileHandler(f"{LOG_DIR}/{file_name}", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    if to_stdout:
        stdout_handler = StreamHandler()
        stdout_handler.setFormatter(formatter)
        logger.addHandler(stdout_handler)

    logger.propagate = False

    loggers[name] = logger
    return logger


#get the current level
def get_logger_level(name: str) -> str:
    logger = loggers.get(name)
    if logger is None:
        raise ValueError(f"logger {name} not found")
    return logging.getLevelName(logger.level)


#set the current level
def set_logger_level(name: str, level_str: str) -> int:
    logger = loggers.get(name)
    if logger is None:
        raise ValueError(f"logger {name} not found")

    level = getattr(logging, level_str.upper(), None)
    if level is None:
        raise ValueError("Invalid level (use DEBUG, INFO, or ERROR)")
    logger.setLevel(level)
    return level






