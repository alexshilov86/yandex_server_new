import logging
from logging.handlers import RotatingFileHandler

def init_logger():
    LOG_FILE = "bot_server.log"
    # 1. Получаем корневой (главный) логгер всего приложения
    root_logger = logging.getLogger()
    # Устанавливаем минимальный порог. DEBUG позволит обработчикам 
    # самим решать, какие сообщения пропускать, а какие нет.
    root_logger.setLevel(logging.DEBUG)

    # Защита от дублирования логов при повторном вызове init_logger
    if root_logger.hasHandlers():
        root_logger.handlers.clear()

    # 2. НАСТРОЙКА ВЫВОДА В КОНСОЛЬ
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO) # В консоли смотрим только важные логи (INFO и выше)
    
    # Короткий формат для консоли: [УРОВЕНЬ] Сообщение
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )    
    console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
    console_handler.setFormatter(formatter)        

    # 3. НАСТРОЙКА ЗАПИСИ В ФАЙЛ
    # encoding="utf-8" обязателен, чтобы кириллица в файле не превратилась в иероглифы
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3, encoding="utf-8")
    file_handler.setLevel(logging.DEBUG) # В файл пишем абсолютно всё (даже отладочный DEBUG)

    # Подробный формат для файла: Дата Время [УРОВЕНЬ] Имя_файла: Сообщение
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(file_formatter)

    # 4. Добавляем оба обработчика к главному логгеру
    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)