"""Аналитика Alpha-Bot — темы, конверсия, качество."""

import sqlite3
import json
import time
import re
import logging
from collections import Counter
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

DB_PATH = "/opt/alpha-bot-data/conversations.db"

# ─── Схема ───

def init_analytics_db():
    """Добавляет аналитические таблицы."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS analytics_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            event_type TEXT NOT NULL,
            event_data TEXT DEFAULT '{}',
            timestamp REAL NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_events_type ON analytics_events(event_type, timestamp);
        CREATE INDEX IF NOT EXISTS idx_events_session ON analytics_events(session_id);
    """)
    conn.close()


# ─── Трекинг событий ───

def track_event(session_id: str, event_type: str, data: dict = None):
    """Записывает аналитическое событие."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        "INSERT INTO analytics_events (session_id, event_type, event_data, timestamp) "
        "VALUES (?, ?, ?, ?)",
        (session_id, event_type, json.dumps(data or {}, ensure_ascii=False), time.time())
    )
    conn.commit()
    conn.close()


# ─── Детекция намерений ───

CONVERSION_PATTERNS = {
    'contact_request': [
        r'(?:мой|мои)?\s*(?:email|почта|телефон|контакт)',
        r'(?:напишите|позвоните|свяжитесь)',
        r'(?:оставлю|оставить)\s+(?:контакт|почту|телефон)',
        r'@\w+\.\w+',  # email
        r'\+?\d[\d\s\-]{9,}',  # телефон
    ],
    'price_interest': [
        r'(?:сколько|какая)\s+(?:стоит|стоимость|цена)',
        r'(?:расчёт|расчет|калькулятор|ткп|кп)\b',
        r'(?:купить|приобрести|заказать|лицензи)',
        r'бюджет',
    ],
    'demo_request': [
        r'(?:демо|demo|попробовать|тест|пробн)',
        r'(?:скачать|download|дистрибутив)',
    ],
    'comparison': [
        r'(?:сравн|отлич|разниц|vs|versus)',
        r'(?:лучше|хуже)',
        r'(?:аналог|замена|альтернатив)',
        r'(?:mastersсada|wincc|genesis|лацерта)',
    ],
    'technical_deep': [
        r'(?:как\s+(?:настроить|подключить|сконфигурировать|интегрировать))',
        r'(?:ошибка|проблема|не\s+работает|баг)',
        r'(?:документация|инструкция|руководство)',
    ],
    'followup': [
        r'^(?:а ещё|а еще|подробнее|ещё|еще|продолж|дальше)\s*\??$',
        r'^\?\s*$',
    ],
    'satisfaction': [
        r'(?:спасибо|благодарю|отлично|супер|класс|помогло|понятно|ясно)',
    ],
}


def detect_intent(text: str) -> list[str]:
    """Определяет намерения пользователя."""
    text_lower = text.lower().strip()
    intents = []

    for intent, patterns in CONVERSION_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text_lower):
                intents.append(intent)
                break

    return intents


def analyze_and_track(session_id: str, text: str, is_user: bool = True):
    """Анализирует сообщение и трекает события."""
    if not is_user:
        return

    intents = detect_intent(text)
    for intent in intents:
        track_event(session_id, intent, {'text_preview': text[:100]})

    # Трекаем модуль/тему
    topic = _detect_topic_for_analytics(text)
    if topic:
        track_event(session_id, 'topic_asked', {'topic': topic})


def _detect_topic_for_analytics(text: str) -> str | None:
    """Определяет тему для аналитики."""
    text_lower = text.lower()

    topics = {
        'Alpha.Server': ['server', 'сервер сигналов', 'ввод-вывод', 'кластер'],
        'Alpha.HMI': ['hmi', 'мнемосхем', 'визуализац'],
        'Alpha.Historian': ['historian', 'архив'],
        'Alpha.Alarms': ['тревог', 'alarm', 'событи'],
        'Alpha.Reports': ['отчёт', 'отчет', 'report'],
        'Alpha.DevStudio': ['devstudio', 'ide', 'среда разработки'],
        'Alpha.WebViewer': ['webviewer', 'web viewer', 'веб'],
        'Alpha.Trends': ['trend', 'график'],
        'Alpha.Om': ['alpha.om', 'формул', 'процедур'],
        'Лицензирование': ['лицензи', 'цена', 'стоимость', 'купить', 'тариф', 'артикул'],
        'Протоколы': ['modbus', 'opc', 'iec', 'протокол', 'драйвер', 's7', 'snmp'],
        'Импортозамещение': ['импортозамещ', 'замена wincc', 'аналог', 'миграц'],
        'Linux': ['linux', 'astra', 'ред ос', 'альт'],
        'Резервирование': ['резерв', 'кластер', 'отказоустойч'],
        'Безопасность': ['security', 'безопасност', 'ldap', 'аудит'],
        'Общие вопросы': [],  # fallback
    }

    for topic, keywords in topics.items():
        for kw in keywords:
            if kw in text_lower:
                return topic

    return None


# ─── Отчёты ───

def get_top_topics(days: int = 30, limit: int = 10) -> list[dict]:
    """Топ тем за период."""
    since = time.time() - days * 86400
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT event_data FROM analytics_events "
        "WHERE event_type = 'topic_asked' AND timestamp > ?",
        (since,)
    ).fetchall()
    conn.close()

    topics = []
    for row in rows:
        data = json.loads(row[0])
        if data.get('topic'):
            topics.append(data['topic'])

    counter = Counter(topics)
    return [{'topic': t, 'count': c} for t, c in counter.most_common(limit)]


def get_conversion_funnel(days: int = 30) -> dict:
    """Воронка конверсии."""
    since = time.time() - days * 86400
    conn = sqlite3.connect(DB_PATH)

    # Всего уникальных сессий
    total = conn.execute(
        "SELECT COUNT(DISTINCT session_id) FROM messages WHERE timestamp > ?",
        (since,)
    ).fetchone()[0]

    # Сессии с >2 сообщениями (engaged)
    engaged = conn.execute(
        "SELECT COUNT(*) FROM ("
        "  SELECT session_id FROM messages WHERE timestamp > ? "
        "  GROUP BY session_id HAVING COUNT(*) > 2"
        ")",
        (since,)
    ).fetchone()[0]

    # По типам конверсий
    funnel = {'total_sessions': total, 'engaged': engaged}

    for event_type in ['price_interest', 'contact_request', 'demo_request',
                       'comparison', 'technical_deep', 'satisfaction']:
        count = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM analytics_events "
            "WHERE event_type = ? AND timestamp > ?",
            (event_type, since)
        ).fetchone()[0]
        funnel[event_type] = count

    conn.close()
    return funnel


def get_daily_stats(days: int = 7) -> list[dict]:
    """Статистика по дням."""
    result = []
    for i in range(days):
        date = datetime.now() - timedelta(days=i)
        day_start = datetime(date.year, date.month, date.day).timestamp()
        day_end = day_start + 86400

        conn = sqlite3.connect(DB_PATH)
        messages = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE timestamp >= ? AND timestamp < ?",
            (day_start, day_end)
        ).fetchone()[0]

        sessions = conn.execute(
            "SELECT COUNT(DISTINCT session_id) FROM messages WHERE timestamp >= ? AND timestamp < ?",
            (day_start, day_end)
        ).fetchone()[0]

        user_messages = conn.execute(
            "SELECT COUNT(*) FROM messages WHERE timestamp >= ? AND timestamp < ? AND role = 'user'",
            (day_start, day_end)
        ).fetchone()[0]

        conn.close()

        result.append({
            'date': date.strftime('%Y-%m-%d'),
            'messages': messages,
            'sessions': sessions,
            'user_messages': user_messages,
        })

    return list(reversed(result))


def get_session_quality(days: int = 30) -> dict:
    """Оценка качества ответов."""
    since = time.time() - days * 86400
    conn = sqlite3.connect(DB_PATH)

    # Сессии с satisfaction
    satisfied = conn.execute(
        "SELECT COUNT(DISTINCT session_id) FROM analytics_events "
        "WHERE event_type = 'satisfaction' AND timestamp > ?",
        (since,)
    ).fetchone()[0]

    # Сессии с followup (повторные вопросы — мог не понять)
    followups = conn.execute(
        "SELECT COUNT(DISTINCT session_id) FROM analytics_events "
        "WHERE event_type = 'followup' AND timestamp > ?",
        (since,)
    ).fetchone()[0]

    # Всего сессий
    total = conn.execute(
        "SELECT COUNT(DISTINCT session_id) FROM messages WHERE timestamp > ?",
        (since,)
    ).fetchone()[0]

    # Средняя длина диалога
    avg_length = conn.execute(
        "SELECT AVG(cnt) FROM ("
        "  SELECT COUNT(*) as cnt FROM messages WHERE timestamp > ? "
        "  GROUP BY session_id"
        ")",
        (since,)
    ).fetchone()[0] or 0

    conn.close()

    return {
        'total_sessions': total,
        'satisfied_sessions': satisfied,
        'satisfaction_rate': f"{satisfied / max(1, total) * 100:.1f}%",
        'followup_sessions': followups,
        'followup_rate': f"{followups / max(1, total) * 100:.1f}%",
        'avg_dialog_length': round(avg_length, 1),
    }


def get_full_analytics(days: int = 30) -> dict:
    """Полный аналитический отчёт."""
    return {
        'period_days': days,
        'top_topics': get_top_topics(days),
        'funnel': get_conversion_funnel(days),
        'quality': get_session_quality(days),
        'daily': get_daily_stats(min(days, 14)),
    }


# ─── Форматирование для Telegram ───

def format_analytics_telegram(days: int = 30) -> str:
    """Красивый отчёт для Telegram."""
    data = get_full_analytics(days)

    lines = [f"📊 Аналитика Alpha-Bot ({days} дней)\n"]

    # Воронка
    f = data['funnel']
    lines.append("🔽 Воронка:")
    lines.append(f"  Всего сессий: {f['total_sessions']}")
    lines.append(f"  Вовлечённых (>2 сообщ.): {f['engaged']}")
    lines.append(f"  Интерес к цене: {f['price_interest']}")
    lines.append(f"  Запрос контактов: {f['contact_request']}")
    lines.append(f"  Запрос демо: {f['demo_request']}")
    lines.append(f"  Сравнение: {f['comparison']}")
    lines.append(f"  Тех. вопросы: {f['technical_deep']}")
    lines.append(f"  Довольные: {f['satisfaction']}")

    # Качество
    q = data['quality']
    lines.append(f"\n⭐ Качество:")
    lines.append(f"  Удовлетворённость: {q['satisfaction_rate']}")
    lines.append(f"  Переспросы: {q['followup_rate']}")
    lines.append(f"  Средняя длина диалога: {q['avg_dialog_length']} сообщ.")

    # Топ тем
    topics = data['top_topics']
    if topics:
        lines.append(f"\n🏷 Топ тем:")
        for i, t in enumerate(topics[:7], 1):
            bar = '█' * min(20, t['count'])
            lines.append(f"  {i}. {t['topic']}: {t['count']} {bar}")

    # Daily
    daily = data['daily']
    if daily:
        lines.append(f"\n📅 По дням:")
        for d in daily[-7:]:
            bar = '▪' * min(20, d['user_messages'])
            lines.append(f"  {d['date']}: {d['user_messages']} вопр. / {d['sessions']} сесс. {bar}")

    return '\n'.join(lines)
