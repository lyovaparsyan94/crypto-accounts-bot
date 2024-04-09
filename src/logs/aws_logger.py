import inspect
import logging
import logging.config
import os

import yaml
from config import configs


class AwsLogger:
    def __init__(self, conf_file: str) -> None:
        """
        Initializes an instance of AwsLogger.

        Args:
            conf_file (str): Path to the log configuration file. Defaults to LOG_CONFIG_FILE.
        """
        self._update_log_config(conf_file)
        self._initialize_logger(conf_file)

    def _update_log_config(self, conf_file: str) -> None:
        """
        Updates the log configuration file with the correct log file path.

        Args:
            conf_file (str): Path to the log configuration file.
        """
        dirname = os.path.dirname(__file__)
        with open(conf_file) as config_file:
            config = yaml.safe_load(config_file)
            config['handlers']['file']['filename'] = os.path.join(dirname, configs.dir_configs.LOG_FILE)
        with open(conf_file, 'w') as config_file:
            yaml.dump(config, config_file)

    def _initialize_logger(self, conf_file: str) -> None:
        """
        Configures the logger using the updated configuration.

        Assumes that the configuration file has been updated.

        Sets the logger name based on the calling function.
        """
        config = yaml.safe_load(open(conf_file))
        logging.config.dictConfig(config)
        logger_name = inspect.stack()[1][3]
        self.logger = logging.getLogger(logger_name)

    def log_debug(self, message: str) -> None:
        """
        Logs a debug message.

        Args:
            message (str): The message to log.
        """
        self.logger.debug(message)

    def log_info(self, message: str) -> None:
        """
        Logs an info message.

        Args:
            message (str): The message to log.
        """
        self.logger.info(message)

    def log_warning(self, message: str) -> None:
        """
        Logs a warning message.

        Args:
            message (str): The message to log.
        """
        self.logger.warning(message)

    def log_error(self, message: str) -> None:
        """
        Logs an error message.

        Args:
            message (str): The message to log.
        """
        self.logger.error(message)

    def log_critical(self, message: str) -> None:
        """
        Logs a critical message.

        Args:
            message (str): The message to log.
        """
        self.logger.critical(message)


awslogger = AwsLogger(conf_file=configs.dir_configs.LOG_CONFIG_FILE)
