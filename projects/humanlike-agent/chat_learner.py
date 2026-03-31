"""Адаптивное обучение — анализ стиля чата и адаптация поведения.

Агент учится из каждого чата:
1. Средняя длина сообщений участников → адаптирует свои ответы
2. Уровень формальности → переключает стиль
3. Активные часы → знает когда чат живёт
4. Ключевые темы → лучше понимает контекст
5. Частота сообщений → адаптирует свою частоту
6. Стиль пунктуации/emoji → зеркалит
"""

import sqlite3
import json
import time
import re
import logging
from collections import Counter
from config import DB_PATH

logger = logging.getLogger(__name__)

# ─── Схема БД ───

def init_learner_db():
    """Создаёт таблицы для адаптивного обучения."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS chat_style (
            chat_id INTEGER PRIMARY KEY,
            avg_msg_length REAL DEFAULT 0,
            formality_score REAL DEFAULT 0.5,
            emoji_frequency REAL DEFAULT 0,
            avg_messages_per_hour REAL DEFAULT 0,
            active_hours TEXT DEFAULT '[]',
            top_topics TEXT DEFAULT '[]',
            punctuation_style TEXT DEFAULT 'normal',
            slang_level REAL DEFAULT 0,
            typical_response_length INTEGER DEFAULT 100,
            samples_count INTEGER DEFAULT 0,
            last_updated REAL DEFAULT 0
        );

        CREATE TABLE IF NOT EXISTS user_style (
            chat_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            avg_msg_length REAL DEFAULT 0,
            emoji_frequency REAL DEFAULT 0,
            formality REAL DEFAULT 0.5,
            message_count INTEGER DEFAULT 0,
            last_seen REAL DEFAULT 0,
            PRIMARY KEY (chat_id, user_id)
        );
    """)
    conn.close()


# ─── Анализ стиля сообщения ───

# Формальные маркеры
FORMAL_MARKERS = [
    'здравствуйте', 'добрый день', 'уважаем', 'пожалуйста', 'благодарю',
    'подскажите', 'не могли бы', 'будьте добры', 'с уважением', 'коллеги',
    'прошу', 'извините', 'разрешите',
]

INFORMAL_MARKERS = [
    'привет', 'здаров', 'чё', 'ваще', 'норм', 'ок', 'лол', 'хз',
    'фигня', 'блин', 'офигеть', 'круто', 'кайф', 'жесть', 'ахах',
    'имхо', 'кста', 'кстати', 'ну', 'типа', 'короч', 'прикинь',
    'реально', 'чел', 'братан', 'мужик', 'пацан', '))', ')))','хех',
    'ржу', 'чот', 'помойму', 'по-моему', 'нифига', 'прикол',
]

EMOJI_PATTERN = re.compile(
    r'[\U0001F600-\U0001F64F\U0001F300-\U0001F5FF\U0001F680-\U0001F6FF'
    r'\U0001F900-\U0001F9FF\U0001FA00-\U0001FA6F\U0001FA70-\U0001FAFF'
    r'\U00002702-\U000027B0\U000024C2-\U0001F251]'
)


def analyze_message(text: str) -> dict:
    """Анализирует стилистические характеристики сообщения."""
    text_lower = text.lower()
    words = text_lower.split()

    # Длина
    length = len(text)
    word_count = len(words)

    # Формальность (0 = супер неформально, 1 = супер формально)
    formal_count = sum(1 for m in FORMAL_MARKERS if m in text_lower)
    informal_count = sum(1 for m in INFORMAL_MARKERS if m in text_lower)

    if formal_count + informal_count > 0:
        formality = formal_count / (formal_count + informal_count)
    else:
        # Эвристики
        formality = 0.5
        # Капитализация первой буквы → чуть формальнее
        if text and text[0].isupper():
            formality += 0.05
        # Точка в конце → формальнее
        if text.rstrip().endswith('.'):
            formality += 0.05
        # Скобочки )) → неформально
        if ')' in text:
            formality -= 0.1
        # Без пунктуации → неформально
        if not any(c in text for c in '.!?,;:'):
            formality -= 0.05

    formality = max(0.0, min(1.0, formality))

    # Emoji
    emoji_count = len(EMOJI_PATTERN.findall(text))
    # Скобочки тоже считаем за "эмодзи"
    bracket_smileys = len(re.findall(r'[)]{2,}|[:(]{2,}|[:;]-?[)(DdPp]', text))
    emoji_total = emoji_count + bracket_smileys

    # Пунктуация
    if text.rstrip().endswith('...'):
        punct_style = 'ellipsis'
    elif text.rstrip().endswith('!!!') or text.rstrip().endswith('???'):
        punct_style = 'emphatic'
    elif not any(c in text for c in '.!?'):
        punct_style = 'none'
    else:
        punct_style = 'normal'

    # Сленг
    slang_count = sum(1 for m in INFORMAL_MARKERS if m in text_lower)
    slang_level = min(1.0, slang_count / max(1, word_count) * 5)

    return {
        'length': length,
        'word_count': word_count,
        'formality': formality,
        'emoji_count': emoji_total,
        'punct_style': punct_style,
        'slang_level': slang_level,
    }


# ─── Обновление профиля чата ───

def update_chat_style(chat_id: int, text: str, user_id: int = None,
                       is_agent: bool = False):
    """Обновляет стилевой профиль чата на основе нового сообщения."""
    if is_agent:
        return  # Не учимся на своих сообщениях

    analysis = analyze_message(text)
    now = time.time()
    hour = int(time.strftime('%H'))

    conn = sqlite3.connect(DB_PATH)

    # Получаем текущий профиль чата
    row = conn.execute(
        "SELECT avg_msg_length, formality_score, emoji_frequency, "
        "active_hours, slang_level, samples_count FROM chat_style WHERE chat_id = ?",
        (chat_id,)
    ).fetchone()

    if row:
        n = row[5]
        # Экспоненциальное скользящее среднее (α = 0.1)
        alpha = 0.1 if n > 20 else 0.3  # Быстрее учимся в начале
        new_avg_len = row[0] * (1 - alpha) + analysis['length'] * alpha
        new_formality = row[1] * (1 - alpha) + analysis['formality'] * alpha
        new_emoji = row[2] * (1 - alpha) + analysis['emoji_count'] * alpha
        new_slang = row[4] * (1 - alpha) + analysis['slang_level'] * alpha

        # Активные часы
        active_hours = json.loads(row[3])
        active_hours.append(hour)
        if len(active_hours) > 200:
            active_hours = active_hours[-200:]

        conn.execute("""
            UPDATE chat_style SET
                avg_msg_length = ?, formality_score = ?, emoji_frequency = ?,
                active_hours = ?, slang_level = ?, samples_count = ?,
                typical_response_length = ?, last_updated = ?
            WHERE chat_id = ?
        """, (
            new_avg_len, new_formality, new_emoji,
            json.dumps(active_hours), new_slang, n + 1,
            _calc_response_length(new_avg_len, new_formality),
            now, chat_id,
        ))
    else:
        conn.execute("""
            INSERT INTO chat_style
                (chat_id, avg_msg_length, formality_score, emoji_frequency,
                 active_hours, slang_level, samples_count, typical_response_length, last_updated)
            VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """, (
            chat_id, analysis['length'], analysis['formality'],
            analysis['emoji_count'], json.dumps([hour]),
            analysis['slang_level'],
            _calc_response_length(analysis['length'], analysis['formality']),
            now,
        ))

    # Обновляем стиль пользователя
    if user_id:
        row = conn.execute(
            "SELECT avg_msg_length, emoji_frequency, formality, message_count "
            "FROM user_style WHERE chat_id = ? AND user_id = ?",
            (chat_id, user_id)
        ).fetchone()

        if row:
            n = row[3]
            alpha = 0.15
            conn.execute("""
                UPDATE user_style SET
                    avg_msg_length = ?, emoji_frequency = ?, formality = ?,
                    message_count = ?, last_seen = ?
                WHERE chat_id = ? AND user_id = ?
            """, (
                row[0] * (1 - alpha) + analysis['length'] * alpha,
                row[1] * (1 - alpha) + analysis['emoji_count'] * alpha,
                row[2] * (1 - alpha) + analysis['formality'] * alpha,
                n + 1, now, chat_id, user_id,
            ))
        else:
            conn.execute("""
                INSERT INTO user_style
                    (chat_id, user_id, avg_msg_length, emoji_frequency, formality,
                     message_count, last_seen)
                VALUES (?, ?, ?, ?, ?, 1, ?)
            """, (
                chat_id, user_id, analysis['length'],
                analysis['emoji_count'], analysis['formality'], now,
            ))

    conn.commit()
    conn.close()


def _calc_response_length(avg_msg_length: float, formality: float) -> int:
    """Рассчитывает рекомендуемую длину ответа."""
    # Если в чате пишут коротко — отвечаем коротко
    # Если формально — можно чуть длиннее
    base = min(300, max(30, avg_msg_length * 1.5))
    if formality > 0.6:
        base *= 1.3  # Формальный = длиннее
    if formality < 0.3:
        base *= 0.7  # Неформальный = короче
    return int(base)


# ─── Получение стиля чата ───

def get_chat_style(chat_id: int) -> dict | None:
    """Получает стилевой профиль чата."""
    conn = sqlite3.connect(DB_PATH)
    row = conn.execute(
        "SELECT avg_msg_length, formality_score, emoji_frequency, "
        "active_hours, slang_level, samples_count, typical_response_length, "
        "punctuation_style FROM chat_style WHERE chat_id = ?",
        (chat_id,)
    ).fetchone()
    conn.close()

    if not row:
        return None

    active_hours = json.loads(row[3])
    # Вычисляем пиковые часы
    if active_hours:
        hour_counts = Counter(active_hours)
        peak_hours = [h for h, _ in hour_counts.most_common(5)]
    else:
        peak_hours = list(range(9, 18))

    return {
        'avg_msg_length': row[0],
        'formality': row[1],
        'emoji_frequency': row[2],
        'peak_hours': sorted(peak_hours),
        'slang_level': row[4],
        'samples_count': row[5],
        'typical_response_length': row[6],
        'punctuation_style': row[7],
    }


def get_active_users(chat_id: int, limit: int = 10) -> list[dict]:
    """Получает активных пользователей чата."""
    conn = sqlite3.connect(DB_PATH)
    rows = conn.execute(
        "SELECT user_id, avg_msg_length, emoji_frequency, formality, "
        "message_count, last_seen "
        "FROM user_style WHERE chat_id = ? ORDER BY message_count DESC LIMIT ?",
        (chat_id, limit)
    ).fetchall()
    conn.close()

    return [
        {
            'user_id': r[0],
            'avg_msg_length': r[1],
            'emoji_frequency': r[2],
            'formality': r[3],
            'message_count': r[4],
            'last_seen': r[5],
        }
        for r in rows
    ]


# ─── Адаптивный промпт ───

def build_style_instructions(chat_id: int) -> str:
    """Строит инструкции по стилю для LLM на основе выученного стиля чата."""
    style = get_chat_style(chat_id)
    if not style or style['samples_count'] < 5:
        return ""  # Недостаточно данных

    parts = []

    # Длина ответов
    target_len = style['typical_response_length']
    if target_len < 60:
        parts.append("Пиши ОЧЕНЬ коротко — 1-2 предложения максимум, как SMS.")
    elif target_len < 120:
        parts.append("Пиши коротко — 1-3 предложения, как в мессенджере.")
    elif target_len < 250:
        parts.append("Средняя длина ответа — 2-4 предложения.")
    # Если длиннее — не ограничиваем

    # Формальность
    f = style['formality']
    if f < 0.25:
        parts.append("Стиль: очень неформальный. Сленг ок, скобочки вместо смайлов, без заглавных.")
    elif f < 0.4:
        parts.append("Стиль: неформальный, разговорный. Короткие фразы, можно без точек.")
    elif f > 0.7:
        parts.append("Стиль: достаточно формальный. Вежливые обороты, полные предложения.")
    # 0.4-0.7 — нейтральный, не трогаем

    # Emoji
    if style['emoji_frequency'] > 1.5:
        parts.append("Используй эмодзи часто — тут так принято.")
    elif style['emoji_frequency'] > 0.5:
        parts.append("Иногда используй эмодзи — тут это нормально.")
    elif style['emoji_frequency'] < 0.1:
        parts.append("НЕ используй эмодзи — тут их не используют.")

    # Сленг
    if style['slang_level'] > 0.3:
        parts.append("Можешь использовать сленг и сокращения — тут так общаются.")

    if not parts:
        return ""

    return "\n\n## Адаптация стиля (основано на наблюдении за чатом)\n" + "\n".join(f"- {p}" for p in parts)


# ─── Адаптация max_tokens ───

def get_adaptive_max_tokens(chat_id: int) -> int:
    """Возвращает адаптивный max_tokens для LLM на основе стиля чата."""
    style = get_chat_style(chat_id)
    if not style or style['samples_count'] < 5:
        return 220  # дефолт: коротко для чатов

    target = style['typical_response_length']
    # Токены ≈ символы / 3 для русского
    tokens = max(180, min(320, int(target / 3.5)))
    return tokens
