import logging

# Создаем логгер
logger = logging.getLogger("main_logger")
logger.setLevel(logging.INFO)

# Формат сообщений
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(funcName)s -  %(message)s')

# Обработчик для консоли
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# Добавляем обработчик к логгеру (если его ещё нет)
if not logger.hasHandlers():
    logger.addHandler(console_handler)


def log_enter_exit(func):
    def wrapper(*args, **kwargs):
        logger.info(f"Вход в {func.__name__}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Выход из {func.__name__}")
            return result
        except Exception as e:
            logger.error(f"{func.__name__}: {e}")
            raise  # выбросить ошибку дальше, чтобы она не пропала
    return wrapper