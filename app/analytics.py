import logging
import json
from datetime import datetime
import os

# Налаштування логера
# Ми записуватимемо події у файл 'events.log' у корені проекту
analytics_logger = logging.getLogger('volunteer_analytics')
analytics_logger.setLevel(logging.INFO)

# Щоб не дублювати логи, якщо модуль імпортується двічі
if not analytics_logger.handlers:
    # Записуємо файл у корінь проекту (на рівень вище папки app)
    log_file_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'events.log')
    file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
    formatter = logging.Formatter('%(asctime)s | %(message)s')
    file_handler.setFormatter(formatter)
    analytics_logger.addHandler(file_handler)

def track_event(event_name, **kwargs):
    """
    Функція для запису події.
    event_name: назва дії (наприклад, 'login', 'purchase')
    kwargs: додаткові деталі (наприклад, user_id=5)
    """
    data = {
        "event": event_name,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "meta": kwargs
    }
    # Записуємо у файл у форматі JSON
    analytics_logger.info(json.dumps(data, ensure_ascii=False))

def track_error(error_message, route=None):
    """Запис помилок виконання програми"""
    data = {
        "event": "CRITICAL_ERROR",
        "error": str(error_message),
        "route": route,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    analytics_logger.error(json.dumps(data, ensure_ascii=False))

# Повідомлення про старт системи (при першому імпорті модуля)
track_event("system_start", status="Application Initialized")