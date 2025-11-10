import logging
import sys
import traceback
from datetime import datetime
import os

# Создаем директорию для логов, если она не существует
log_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'logs')
os.makedirs(log_dir, exist_ok=True)

# Настройка форматирования
formatter = logging.Formatter(
    '%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Настройка вывода в консоль
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# Настройка вывода в файл
log_file = os.path.join(log_dir, f'browser_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
file_handler = logging.FileHandler(log_file)
file_handler.setFormatter(formatter)

# Настройка логгера
logger = logging.getLogger('browser_automation')
logger.setLevel(logging.INFO)
logger.addHandler(console_handler)
logger.addHandler(file_handler)

def log_exception(e: Exception, context: str = ""):
    """
    Логирует исключение с полным стектрейсом
    """
    error_msg = f"{context} Error: {str(e)}\nTraceback:\n{''.join(traceback.format_tb(e.__traceback__))}"
    logger.error(error_msg)

def log_info(message: str):
    """
    Логирует информационное сообщение
    """
    logger.info(message)

def log_debug(message: str):
    """
    Логирует отладочное сообщение
    """
    logger.debug(message)

def log_warning(message: str):
    """
    Логирует предупреждение
    """
    logger.warning(message)

def log_error(message: str):
    """
    Логирует ошибку
    """
    logger.error(message) 