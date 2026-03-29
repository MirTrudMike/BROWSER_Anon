import logging
import sys
import traceback
from datetime import datetime
import os


class AppLogger:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._setup()
        return cls._instance

    def _setup(self):
        log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'logs')
        os.makedirs(log_dir, exist_ok=True)

        formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)

        log_file = os.path.join(
            log_dir,
            f'browser_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)

        self._logger = logging.getLogger('browser_automation')
        self._logger.setLevel(logging.INFO)
        self._logger.addHandler(console_handler)
        self._logger.addHandler(file_handler)

    def info(self, message: str):
        self._logger.info(message)

    def debug(self, message: str):
        self._logger.debug(message)

    def warning(self, message: str):
        self._logger.warning(message)

    def error(self, message: str):
        self._logger.error(message)

    def exception(self, e: Exception, context: str = ""):
        error_msg = (
            f"{context} Error: {str(e)}\n"
            f"Traceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
        )
        self._logger.error(error_msg)


logger = AppLogger()
