import os
import logging
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path

from .logger_config import LOGGING_DIR, LOGGING_FILE, LOGGING_WHEN, LOGGING_INTERVAL, \
    LOGGING_TITLE, LOGGING_LEVEL, LOGGING_HANDLERS, LOGGING_FORMAT, FORCE_LOG_DEBUG


class AppLogger:
    """
    A singleton class for application logging.

    This class configures a logger to write logs to a file and console with specified formatting.
    It uses a TimedRotatingFileHandler for log files to rotate them at midnight and keeps 7 days of backup.
    The logger is configured to be a singleton to ensure that only one instance is used throughout the application.
    """
    _instance = None

    def __new__(cls, *args, **kwargs):
        """
        Ensures that only one instance of the class is created.
        """
        if not cls._instance:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, name):
        """
        Initializes the logger with file and console handlers if not already initialized.

        Args:
            - name: The name of the logger, typically the __name__ of the module creating the logger.
        """
        # Prevent re-initialization if already initialized
        if hasattr(self, "logger"):
            return
        # Configuration settings from the config (YAML file)
        # Config handlers
        self._config_handlers()

        # Create logger
        self.logger = logging.getLogger(name)
        self.logger.propagate = False

        if not self.logger.handlers and len(self.log_handlers) > 0:
            level = getattr(logging, LOGGING_LEVEL.upper(), logging.INFO) \
                if not FORCE_LOG_DEBUG else logging.DEBUG
            self.logger.setLevel(level)

            # "%(asctime)s - [%(name)s] - %(levelname)-5s - %(message)s"
            logFormatter = logging.Formatter(
                LOGGING_FORMAT
            )

            # Add file handler if it is configured
            if "file_handler" in self.log_handlers:
                self.log_dir = LOGGING_DIR
                self.log_file = LOGGING_FILE

                Path(self.log_dir).mkdir(parents=True, exist_ok=True)
                file_path = os.path.join(self.log_dir, self.log_file)
                fileHandler = TimedRotatingFileHandler(
                    file_path,
                    when=LOGGING_WHEN,
                    interval=LOGGING_INTERVAL,
                    encoding="utf-8"
                )
                fileHandler.suffix = "%Y%m%d_%H%M%S.log"
                fileHandler.setFormatter(logFormatter)

                self.logger.addHandler(fileHandler)

            if "console" in self.log_handlers:
                consoleHandler = logging.StreamHandler()
                consoleHandler.setFormatter(logFormatter)
                self.logger.addHandler(consoleHandler)

    def _config_handlers(self):
        # Create list of handlers
        _handlers = str(LOGGING_HANDLERS)
        self.log_handlers = [
            r.strip().lower() for r in _handlers.strip().split(",")
        ] if len(_handlers) > 0 else []

    def debug(self, message):
        self.logger.debug(message)

    def info(self, message):
        self.logger.info(message)

    def warning(self, message):
        self.logger.warning(message)

    def error(self, message):
        self.logger.error(message)

    def critical(self, message):
        self.logger.critical(message)


logger = AppLogger(LOGGING_TITLE)
