import logging
import os
import platform
from logging.config import dictConfig
from pathlib import Path
from typing import List
from wrappers.config_wrapper import ConfigWrapper

os_system = platform.system()


def disable_debug_mode_blocklist(logger_blocklist: List[str]):
    """
    Disable debug mode for specified loggers.

    :param logger_blocklist: List of logger names to disable debug mode for.
    """
    try:
        for module in logger_blocklist:
            logging.getLogger(module).setLevel(logging.CRITICAL)
    except Exception as e:
        logging.error(f"Error disabling debug mode for blocklist: {e}")


def get_logger(logger_name: str) -> logging.Logger:
    """
    Get a logger with the specified name.

    :param logger_name: Name of the logger.
    :return: Logger instance.
    """
    try:
        logging_config = ConfigWrapper().get_config_file("logging")

        logs_directory = os.path.join('.', 'logs')
        os.makedirs(logs_directory, exist_ok=True)

        if logging_config and 'handlers' in logging_config:
            [keys.update({'filename': fr'{logs_directory}/{Path(logger_name).stem}-{handler.split("_")[0]}.log'})
             for handler, keys in logging_config['handlers'].items() if handler.endswith('handler')]

        disable_debug_mode_blocklist([])  # Update with your logger blocklist

        dictConfig(logging_config)
        return logging.getLogger(logger_name)
    except Exception as e:
        logging.error(f"Error getting logger: {e}")
        return logging.getLogger(logger_name)

