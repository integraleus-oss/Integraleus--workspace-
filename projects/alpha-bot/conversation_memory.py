"""Контекстная память Alpha-Bot — SQLite + профили + саммаризация."""

import sqlite3
import json
import time
import logging
import re
from collections import defaultdict

logger = logging.getLogger(__name__)

DB_PATH = "/opt/alpha-bot-data/conversations.db"

# ─── Инициализация ───

def init_db():
    """Создаёт таблицы если не существуют."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp REAL NOT NULL
        );

        CREATE TABLE IF NOT EXISTS user_profiles (
            session_id TEXT PRIMARY KEY,
            display_name TEXT,
            company TEXT,
            role TEXT,
            interests TEXT DEFAULT '[]',
            topics_asked TEXT DEFAULT '[]',
            first_seen REAL,
            last_seen REAL,
            message_count INTEGER DEFAULT 0,
            summary TEXT
        );

        CREATE TABLE IF NOT EXISTS conversation_summaries (
            session_id TEXT NOT NULL,
            summary TEXT NOT NULL,
            message_range TEXT,
            created_at REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_messages_session ON messages(session_id, timestamp);
        CREATE INDEX IF NOT EXISTS idx_summaries_session ON conversation_summaries(session_id);
    """)
    conn.close()
    logger.info("Conversation DB initialized")


# ─── Сохранение/получение сообщений ───

def save_message(session_id: str, role: str, content: str):
    """Сохраняет сообщение."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
        (session_id, role, content, time.time())
    )

    # Обновляем счётчик профиля
    conn.execute("""
        INSERT INTO user_profiles (session_id, first_seen, last_seen, message_count)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(session_id) DO UPDATE SET
            last_seen = ?,
            message_count = message_count + 1
    """, (session_id, time.time(), time.time(), time.time()))

    conn.commit()
    conn.close()


def get_history(session_id: str, limit: int = 10) -> list[dict]:
    """Получает последние сообщения сессии."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT role, content, timestamp FROM messages "
        "WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?",
        (session_id, limit)
    ).fetchall()
    conn.close()

    return [
        {"role": r[0], "content": r[1], "timestamp": r[2]}
        for r in reversed(rows)
    ]


def get_message_count(session_id: str) -> int:
    """Количество сообщений в сессии."""
    conn = sqlite3.connect(DB_PATH)
    count = conn.execute(
        "SELECT COUNT(*) FROM messages WHERE session_id = ?",
        (session_id,)
    ).fetchone()[0]
    conn.close()
    return count


# ─── Профили пользователей ───

def get_profile(session_id: str) -> dict | None:
    """Получает профиль пользователя."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT display_name, company, role, interests, topics_asked, "
        "first_seen, last_seen, message_count, summary "
        "FROM user_profiles WHERE session_id = ?",
        (session_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    return {
        "display_name": row[0],
        "company": row[1],
        "role": row[2],
        "interests": json.loads(row[3]) if row[3] else [],
        "topics_asked": json.loads(row[4]) if row[4] else [],
        "first_seen": row[5],
        "last_seen": row[6],
        "message_count": row[7],
        "summary": row[8],
    }


def update_profile(session_id: str, **kwargs):
    """Обновляет поля профиля."""
    conn = sqlite3.connect(DB_PATH)

    for key, value in kwargs.items():
        if key in ("interests", "topics_asked"):
            value = json.dumps(value, ensure_ascii=False)
        if key in ("display_name", "company", "role", "interests",
                    "topics_asked", "summary"):
            conn.execute(
                f"UPDATE user_profiles SET {key} = ? WHERE session_id = ?",
                (value, session_id)
            )

    conn.commit()
    conn.close()


def add_topic(session_id: str, topic: str):
    """Добавляет тему в список спрошенных."""
    profile = get_profile(session_id)
    if not profile:
        return

    topics = profile["topics_asked"]
    if topic not in topics:
        topics.append(topic)
        # Храним последние 20 тем
        if len(topics) > 20:
            topics = topics[-20:]
        update_profile(session_id, topics_asked=topics)


# ─── Follow-up детекция ───

FOLLOWUP_PATTERNS = [
    r'^а ещё\??',
    r'^а еще\??',
    r'^ещё\??',
    r'^еще\??',
    r'^а что насчёт',
    r'^а что насчет',
    r'^подробнее',
    r'^расскажи подробнее',
    r'^расскажи больше',
    r'^а как насчёт',
    r'^а как насчет',
    r'^ну и\??',
    r'^и ещё',
    r'^и еще',
    r'^а если',
    r'^что ещё',
    r'^что еще',
    r'^а можно подробнее',
    r'^можно подробнее',
    r'^а поподробнее',
    r'^давай подробнее',
    r'^покажи ещё',
    r'^покажи еще',
    r'^tell me more',
    r'^more details',
    r'^go on',
    r'^continue',
    r'^and\??$',
    r'^\?\??\s*$',  # просто вопросительный знак
]

# Короткие сообщения которые скорее всего follow-up
FOLLOWUP_SHORT_WORDS = {
    'да', 'ага', 'угу', 'ок', 'ну', 'и?', 'а?', 'хм', 'ясно',
    'понял', 'понятно', 'дальше', 'продолжай', 'ещё', 'еще',
}


def is_followup(text: str, history: list[dict]) -> bool:
    """Определяет, является ли сообщение follow-up к предыдущему."""
    if not history:
        return False

    text_lower = text.strip().lower()

    # Проверяем паттерны
    for pattern in FOLLOWUP_PATTERNS:
        if re.match(pattern, text_lower):
            return True

    # Короткие слова
    if text_lower in FOLLOWUP_SHORT_WORDS:
        return True

    # Очень короткое сообщение (< 15 символов) после ответа бота
    if len(text_lower) < 15 and history and history[-1]["role"] == "assistant":
        return True

    return False


def get_last_topic(history: list[dict]) -> str:
    """Извлекает тему последнего вопроса пользователя из истории."""
    for msg in reversed(history):
        if msg["role"] == "user" and len(msg["content"]) > 15:
            return msg["content"]
    return ""


# ─── Контекстный промпт ───

def build_context_prompt(session_id: str, current_message: str) -> str:
    """Строит дополнительный контекст для LLM на основе памяти."""
    profile = get_profile(session_id)
    if not profile:
        return ""

    parts = []

    # Информация о пользователе
    user_info = []
    if profile.get("display_name"):
        user_info.append(f"Имя: {profile['display_name']}")
    if profile.get("company"):
        user_info.append(f"Компания: {profile['company']}")
    if profile.get("role"):
        user_info.append(f"Роль: {profile['role']}")

    if user_info:
        parts.append("Информация о клиенте: " + ", ".join(user_info))

    # Ранее спрашивал
    if profile.get("topics_asked"):
        recent_topics = profile["topics_asked"][-5:]
        parts.append(
            "Клиент ранее интересовался: " + "; ".join(recent_topics)
        )

    # Краткое резюме предыдущих разговоров
    if profile.get("summary"):
        parts.append(f"Краткое резюме предыдущих обращений: {profile['summary']}")

    # Число обращений
    if profile.get("message_count", 0) > 5:
        parts.append(f"Это постоянный клиент ({profile['message_count']} сообщений)")

    if not parts:
        return ""

    return "\n## Контекст клиента (из памяти)\n" + "\n".join(f"- {p}" for p in parts)


# ─── Извлечение информации о пользователе ───

def extract_user_info(text: str) -> dict:
    """Пытается извлечь информацию о пользователе из сообщения."""
    info = {}

    # Компания
    company_patterns = [
        r'(?:работаю|работаем)\s+(?:в|на)\s+[«"]?([A-ZА-ЯЁa-zа-яё][A-ZА-ЯЁa-zа-яё\s\-\.]{2,25}?)(?:\s+(?:инженером|программистом|наладчиком|оператором|менеджером|техником|руководителем)|\s*[»",.!?]|$)',
        r'(?:компания|предприятие|завод|комбинат|фабрика)\s+[«"]?([^»",.]{3,30}?)[»",.!?\s]',
        r'(?:мы|наша компания|наш завод)\s+[-—]\s+([^,.]{3,30})',
    ]
    for pattern in company_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["company"] = match.group(1).strip()
            break

    # Роль
    role_patterns = [
        r'(?:я|работаю)\s+(?:как\s+)?(\w*инженер\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*програм\w+)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*проектиров\w+)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*наладчик\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*техник\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*оператор\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*менеджер\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*руководител\w*)',
        r'(?:я|работаю)\s+(?:как\s+)?(\w*диспетчер\w*)',
    ]
    for pattern in role_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            info["role"] = match.group(1).strip()
            break

    return info


def detect_topic(text: str) -> str | None:
    """Определяет тему вопроса для сохранения в профиль."""
    text_lower = text.lower()

    # Модули Альфы
    module_keywords = {
        "Alpha.Server": ["server", "сервер сигналов", "ввод-вывод"],
        "Alpha.HMI": ["hmi", "мнемосхем", "визуализац"],
        "Alpha.Historian": ["historian", "архивирован", "архив данных"],
        "Alpha.Alarms": ["тревог", "alarm", "квитирован"],
        "Alpha.Reports": ["отчёт", "отчет", "report"],
        "Alpha.DevStudio": ["devstudio", "ide", "среда разработки"],
        "Лицензирование": ["лицензи", "цена", "стоимость", "купить", "тариф"],
        "Протоколы": ["modbus", "opc", "iec", "протокол", "драйвер"],
        "Импортозамещение": ["импортозамещ", "замена", "аналог", "wincc", "mastersсada"],
        "Linux": ["linux", "astra", "ред ос", "альт"],
        "Резервирование": ["резерв", "кластер", "отказоустойч"],
    }

    for topic, keywords in module_keywords.items():
        for kw in keywords:
            if kw in text_lower:
                return topic

    # Если вопрос достаточно длинный — берём первые 50 символов как тему
    if len(text) > 30 and '?' in text:
        # Берём текст до вопросительного знака
        q = text.split('?')[0].strip()
        if len(q) > 15:
            return q[:50]

    return None


# ─── Саммаризация (через LLM) ───

async def summarize_conversation(session_id: str, ask_llm_func) -> str | None:
    """Создаёт саммари длинной истории через LLM.

    Вызывается когда история становится слишком длинной (>20 сообщений).
    """
    history = get_history(session_id, limit=30)
    if len(history) < 10:
        return None

    # Формируем текст для саммаризации
    conv_text = "\n".join(
        f"{'Клиент' if m['role'] == 'user' else 'Консультант'}: {m['content'][:200]}"
        for m in history
    )

    summary_prompt = (
        "Кратко (2-3 предложения) опиши о чём был этот диалог. "
        "Укажи: что интересовало клиента, какие модули/продукты обсуждались, "
        "какие решения были предложены. Отвечай только саммари, без преамбул."
    )

    summary = await ask_llm_func(
        summary_prompt,
        [{"role": "user", "content": f"Диалог:\n{conv_text}"}],
    )

    if summary:
        # Сохраняем
        conn = sqlite3.connect(DB_PATH)
        conn.execute(
            "INSERT INTO conversation_summaries (session_id, summary, message_range, created_at) "
            "VALUES (?, ?, ?, ?)",
            (session_id, summary, f"1-{len(history)}", time.time())
        )
        conn.commit()
        conn.close()

        # Обновляем профиль
        update_profile(session_id, summary=summary)

        logger.info(f"Summary created for {session_id}: {summary[:80]}...")

    return summary


# ─── Очистка ───

def clear_session(session_id: str):
    """Очищает историю сессии (но сохраняет профиль и саммари)."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("DELETE FROM messages WHERE session_id = ?", (session_id,))
    conn.commit()
    conn.close()


def get_stats() -> dict:
    """Общая статистика."""
    conn = sqlite3.connect(DB_PATH)
    total_messages = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
    total_sessions = conn.execute("SELECT COUNT(DISTINCT session_id) FROM messages").fetchone()[0]
    total_profiles = conn.execute("SELECT COUNT(*) FROM user_profiles").fetchone()[0]
    conn.close()

    return {
        "total_messages": total_messages,
        "total_sessions": total_sessions,
        "total_profiles": total_profiles,
    }
