# CliSelf/core/logger.py
import os
import logging
from logging.handlers import RotatingFileHandler

# مسیر پوشه‌ی لاگ‌ها (در کنار main.py)
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
LOGS_DIR = os.path.join(BASE_DIR, "logs")
os.makedirs(LOGS_DIR, exist_ok=True)

def get_logger(module_name: str) -> logging.Logger:
    """
    ایجاد و پیکربندی logger برای هر ماژول.
    - فایل جداگانه برای هر ماژول در مسیر logs/
    - نمایش همزمان در کنسول
    - پشتیبانی از Log Rotation
    """
    logger = logging.getLogger(module_name)

    if not logger.handlers:
        logger.setLevel(logging.INFO)

        log_file = os.path.join(LOGS_DIR, f"{module_name}.txt")

        # ✅ 1. Log Rotation
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=5 * 1024 * 1024,  # حداکثر ۵ مگابایت برای هر فایل
            backupCount=5,              # نگهداری تا ۵ نسخه قدیمی
            encoding="utf-8"
        )

        # ✅ 2. Console Handler (برای نمایش همزمان در ترمینال)
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)

        # ✅ 3. فرمت استاندارد
        formatter = logging.Formatter(
            fmt="%(asctime)s | %(levelname)-8s | [%(name)s] %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)

        # ✅ 4. افزودن هندلرها
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
