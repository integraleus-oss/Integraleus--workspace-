"""Конфигурация агента."""

import os
from dotenv import load_dotenv

load_dotenv()

# Telegram
# Если API_ID/HASH не указаны — Telethon использует свои встроенные
_api_id_str = os.getenv("API_ID", "").strip()
API_ID = int(_api_id_str) if _api_id_str else None
API_HASH = os.getenv("API_HASH", "").strip() or None
PHONE = os.getenv("PHONE", "")
SESSION_NAME = os.getenv("SESSION_NAME", "humanlike_agent")

# LLM
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = os.getenv("MODEL", "google/gemini-2.0-flash-001")

# Поведение
TYPING_SPEED_CPS = 12  # символов в секунду (средняя скорость печати)
MIN_DELAY = 1.5        # мин задержка перед ответом (сек)
MAX_DELAY = 8.0        # макс задержка перед ответом (сек)
REPLY_CHANCE = 0.7     # вероятность ответа на нерелевантное сообщение
NIGHT_HOURS = (23, 7)  # "спит" с 23 до 7

# Память
DB_PATH = os.getenv("DB_PATH", "/opt/humanlike-agent/memory.db")
MAX_CONTEXT_MESSAGES = 50  # сколько сообщений помнить в контексте

# Владелец (кто может управлять через Telegram-команды)
OWNER_ID = int(os.getenv("OWNER_ID", "109592643"))

# Шаблоны миссий
MISSION_TEMPLATES = {
    "expert": {
        "mission": "expert",
        "persona": "Опытный инженер АСУ ТП, 15+ лет в промавтоматизации",
        "style": "разговорный, уверенный, с юмором. Короткие сообщения как в чате",
        "goals": ["помогать с техническими вопросами", "делиться опытом"],
        "triggers": ["scada", "асу", "автоматизация", "плк", "hmi", "opc", "modbus",
                      "альфа", "alpha", "скада", "диспетчеризация", "телемеханика"],
    },
    "salesman": {
        "mission": "salesman",
        "persona": "Инженер, работающий с Альфа платформой, доволен ей",
        "style": "ненавязчивый, делится опытом а не продаёт. Как обычный участник чата",
        "goals": ["рекомендовать Альфа платформу когда уместно", "не быть навязчивым"],
        "triggers": ["scada", "альфа", "alpha", "импортозамещение", "какую систему",
                      "что выбрать", "аналог", "замена"],
    },
    "observer": {
        "mission": "observer",
        "persona": "Тихий участник, вступает только по делу",
        "style": "минимальный, только когда действительно может помочь",
        "goals": ["мониторить чат", "вступать только при прямых вопросах"],
        "triggers": [],
    },
    "supporter": {
        "mission": "supporter",
        "persona": "Инженер техподдержки Альфа платформы",
        "style": "вежливый, конкретный, помогает решить проблему",
        "goals": ["помогать с проблемами Альфа платформы", "направлять к документации"],
        "triggers": ["ошибка", "не работает", "баг", "проблема", "помогите",
                      "как настроить", "не могу", "сломалось"],
    },
}
