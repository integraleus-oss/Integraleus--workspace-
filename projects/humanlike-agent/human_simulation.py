"""Имитация человеческого поведения — Фаза 1: Достоверность."""

import random
import asyncio
import logging
import time
import re
from datetime import datetime
from config import NIGHT_HOURS

logger = logging.getLogger(__name__)

# ─── Раскладка клавиатуры для опечаток по соседним клавишам ───
KEYBOARD_NEIGHBORS = {
    'й': 'цу', 'ц': 'йук', 'у': 'цке', 'к': 'уеа', 'е': 'кан',
    'н': 'еаг', 'г': 'наш', 'ш': 'гащ', 'щ': 'шаз', 'з': 'щх',
    'х': 'зъ', 'ъ': 'х',
    'ф': 'ыв', 'ы': 'фва', 'в': 'ыап', 'а': 'впр', 'п': 'аро',
    'р': 'пол', 'о': 'рлд', 'л': 'одж', 'д': 'лжэ', 'ж': 'дэ', 'э': 'жд',
    'я': 'чс', 'ч': 'яси', 'с': 'чим', 'м': 'сит', 'и': 'мтп',
    'т': 'иьо', 'ь': 'тбр', 'б': 'ьюл', 'ю': 'бд',
    'q': 'wa', 'w': 'qeas', 'e': 'wrds', 'r': 'etdf', 't': 'ryfg',
    'y': 'tugh', 'u': 'yihj', 'i': 'uojk', 'o': 'iplk', 'p': 'ol',
    'a': 'qwsz', 's': 'awedxz', 'd': 'serfcx', 'f': 'drtgvc',
    'g': 'ftyhbv', 'h': 'gyujnb', 'j': 'huiknm', 'k': 'jiolm',
    'l': 'kop',
    'z': 'asx', 'x': 'zsdc', 'c': 'xdfv', 'v': 'cfgb',
    'b': 'vghn', 'n': 'bhjm', 'm': 'njk',
}

# ─── Состояние сессии (per-chat engagement tracking) ───
_chat_state: dict[int, dict] = {}


def _get_chat_state(chat_id: int) -> dict:
    """Получить или создать состояние чата."""
    if chat_id not in _chat_state:
        _chat_state[chat_id] = {
            'last_agent_reply': 0,      # timestamp последнего ответа агента
            'last_incoming': 0,         # timestamp последнего входящего
            'active_dialog': False,     # сейчас в активном диалоге?
            'messages_in_burst': 0,     # сколько сообщений в текущей серии
            'pending_read': False,      # "прочитал но не ответил"
        }
    return _chat_state[chat_id]


def update_incoming(chat_id: int):
    """Вызывать при получении входящего сообщения."""
    state = _get_chat_state(chat_id)
    now = time.time()
    gap = now - state['last_agent_reply'] if state['last_agent_reply'] else 999

    # Если последний ответ агента был <2 мин назад — активный диалог
    state['active_dialog'] = gap < 120
    state['last_incoming'] = now

    if gap < 60:
        state['messages_in_burst'] += 1
    else:
        state['messages_in_burst'] = 1


def update_outgoing(chat_id: int):
    """Вызывать после отправки ответа."""
    state = _get_chat_state(chat_id)
    state['last_agent_reply'] = time.time()
    state['pending_read'] = False


# ─── Время суток ───

def is_night() -> bool:
    """Проверяет ночное время (по серверу)."""
    hour = datetime.now().hour
    start, end = NIGHT_HOURS
    if start > end:
        return hour >= start or hour < end
    return start <= hour < end


def _time_of_day_factor() -> float:
    """Фактор замедления по времени суток. 1.0 = норма, >1 = медленнее."""
    hour = datetime.now().hour
    if 9 <= hour < 22:
        return 1.0      # рабочее время — нормальная скорость
    elif 22 <= hour or hour < 1:
        return 1.5       # поздний вечер — чуть медленнее
    elif 1 <= hour < 7:
        return 3.0       # ночь — сонный
    else:  # 7-9
        return 1.2       # утро — ещё не проснулся


# ─── Задержки ───

async def simulate_reading(text_length: int):
    """Имитация чтения сообщения."""
    # ~25-35 символов/сек чтение, с джиттером
    speed = random.uniform(25, 35)
    read_time = max(0.3, text_length / speed)
    read_time = min(read_time, 4.0)
    jitter = random.uniform(0.2, 1.0)
    await asyncio.sleep(read_time + jitter)


async def simulate_thinking(chat_id: int = None):
    """Пауза "на подумать" — адаптивная."""
    state = _get_chat_state(chat_id) if chat_id else None
    tod = _time_of_day_factor()

    if state and state['active_dialog']:
        # В активном диалоге — быстрые ответы
        delay = random.uniform(0.5, 3.0)
    else:
        # Первый ответ после паузы — "открывает телегу"
        delay = random.uniform(3.0, 15.0)

        # Иногда задержка побольше (как будто отвлёкся)
        if random.random() < 0.15:
            delay = random.uniform(15.0, 45.0)

    delay *= tod
    await asyncio.sleep(delay)


async def simulate_app_opening(chat_id: int) -> float:
    """Имитация 'открытия приложения' — задержка перед тем как начать читать.
    Возвращает длительность задержки."""
    state = _get_chat_state(chat_id)

    if state['active_dialog']:
        # Уже "в приложении" — мгновенно
        return 0

    gap = time.time() - state['last_agent_reply'] if state['last_agent_reply'] else 999

    if gap < 60:
        delay = random.uniform(0.5, 2.0)
    elif gap < 300:
        delay = random.uniform(2.0, 10.0)  # отошёл ненадолго
    elif gap < 1800:
        delay = random.uniform(10.0, 40.0)  # занят другим
    else:
        delay = random.uniform(20.0, 90.0)  # давно не заходил

    delay *= _time_of_day_factor()

    # Кэп: не больше 2 минут
    delay = min(delay, 120.0)

    await asyncio.sleep(delay)
    return delay


def should_delay_response(chat_id: int) -> tuple[bool, float]:
    """Решает, стоит ли 'прочитать и ответить позже'.
    Возвращает (should_delay, delay_seconds)."""
    state = _get_chat_state(chat_id)

    if state['active_dialog']:
        return False, 0

    # 10% шанс "прочитал, но ответит позже"
    if random.random() < 0.10:
        delay = random.uniform(30.0, 180.0)  # 30 сек - 3 мин
        delay *= _time_of_day_factor()
        return True, min(delay, 300.0)

    return False, 0


# ─── Скорость печати ───

def calculate_typing_duration(text: str, chat_id: int = None) -> float:
    """Сколько секунд "печатать" текст — адаптивно."""
    state = _get_chat_state(chat_id) if chat_id else None
    length = len(text)

    # Базовая скорость: 8-15 cps в зависимости от контекста
    if state and state['active_dialog']:
        base_cps = random.uniform(11, 16)  # быстрее в активном диалоге
    else:
        base_cps = random.uniform(7, 12)   # медленнее в начале

    # Короткие ответы (<30 символов) печатаются быстрее
    if length < 30:
        base_cps *= 1.3

    # Ночью медленнее
    base_cps /= _time_of_day_factor()

    duration = length / base_cps

    # Ускорение к середине текста, замедление в конце (как человек)
    # Имитируем: быстрый старт, набирает скорость, потом замедляется думая как закончить
    duration *= random.uniform(0.85, 1.15)

    # Минимум 0.8 сек, максимум 25 сек (никто не печатает 30 секунд без остановки)
    return max(0.8, min(duration, 25.0))


def calculate_typing_chunks(text: str, chat_id: int = None) -> list[tuple[float, bool]]:
    """Разбивает печать на этапы: [(duration, show_typing), ...].
    Иногда typing пропадает (человек остановился подумать) и появляется снова."""
    total = calculate_typing_duration(text, chat_id)

    # Короткие тексты — одним куском
    if total < 4.0 or len(text) < 60:
        return [(total, True)]

    # Длинные — с паузами "задумался"
    chunks = []
    remaining = total

    while remaining > 1.0:
        chunk_duration = random.uniform(1.5, min(6.0, remaining))

        # 25% шанс "пауза — перестал печатать"
        if chunks and random.random() < 0.25:
            pause = random.uniform(0.5, 2.5)
            chunks.append((pause, False))  # typing off
            remaining -= pause

        chunks.append((min(chunk_duration, remaining), True))
        remaining -= chunk_duration

    return chunks


# ─── Решение отвечать ли ───

def should_reply(message_text: str, triggers: list[str] = None,
                 mentioned: bool = False, is_reply_to_agent: bool = False) -> bool:
    """Решает, стоит ли отвечать на сообщение.
    В группах — только на прямой запрос, а не по случайности."""
    if mentioned or is_reply_to_agent:
        return True

    text_lower = message_text.lower().strip()

    if triggers:
        for trigger in triggers:
            if trigger.lower() in text_lower:
                return True

    question_markers = [
        "?", "почему", "зачем", "как", "что", "когда", "где", "какой", "какая",
        "какие", "можно ли", "нужно ли", "стоит ли", "объясни", "расскажи", "подскажи",
        "посоветуй", "имеет смысл", "в чем", "в чём"
    ]
    if any(marker in text_lower for marker in question_markers):
        return True

    return False


# ─── Разбивка сообщений ───

def split_message(text: str) -> list[str]:
    """Короткие — целиком. Длинные (>500 символов) — максимум 2 части."""
    if len(text) < 500:
        return [text]

    # Ищем точку разбивки примерно посередине
    mid = len(text) // 2
    # Ищем ближайшую точку/перенос к середине
    best = mid
    for offset in range(0, min(100, mid)):
        for pos in [mid + offset, mid - offset]:
            if 0 < pos < len(text) and text[pos-1] in '.!?\n':
                best = pos
                break
        else:
            continue
        break

    if best == mid:
        return [text]  # не нашли хорошую точку — целиком

    return [text[:best].strip(), text[best:].strip()]

def _split_message_old(text: str) -> list[str]:
    """Старая версия — оставлена для справки."""
    if len(text) < 100:
        return [text]

    if random.random() < 0.40:
        return [text]

    parts = []

    if '\n\n' in text:
        raw_parts = text.split('\n\n')
        raw_parts = [p.strip() for p in raw_parts if p.strip()]
        if 2 <= len(raw_parts) <= 4:
            return raw_parts

    # По одинарному переносу (если получается 2-3 части)
    if '\n' in text:
        raw_parts = text.split('\n')
        raw_parts = [p.strip() for p in raw_parts if p.strip()]
        if 2 <= len(raw_parts) <= 4:
            # Склеиваем слишком короткие
            merged = _merge_short_parts(raw_parts, min_len=30)
            if 2 <= len(merged) <= 4:
                return merged

    # По предложениям
    sentences = re.split(r'(?<=[.!?])\s+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 1:
        return [text]

    if len(sentences) == 2:
        return sentences

    # 3+ предложений — группируем в 2-3 сообщения
    if len(sentences) <= 4:
        mid = len(sentences) // 2
        return [
            ' '.join(sentences[:mid]),
            ' '.join(sentences[mid:]),
        ]

    # Много предложений — 3 части
    third = len(sentences) // 3
    return [
        ' '.join(sentences[:third]),
        ' '.join(sentences[third:third*2]),
        ' '.join(sentences[third*2:]),
    ]


def _merge_short_parts(parts: list[str], min_len: int = 30) -> list[str]:
    """Склеивает слишком короткие части с соседними."""
    if not parts:
        return parts

    merged = [parts[0]]
    for p in parts[1:]:
        if len(merged[-1]) < min_len or len(p) < min_len:
            merged[-1] += '\n' + p
        else:
            merged.append(p)
    return merged


# Запрещённые паттерны: если модель всё равно сгенерила это — вырезаем
BANNED_PHRASES = [
    "надо быть более",
    "путать людей с ботами",
    "более внимательными",
    "более добрыми",
    "различать",
    "лечить без спроса",
    "я так, философствую",
    "нам всем надо",
    "больше - различать",
    "меньше лечить",
    "просто общаться",
    "я просто иногда задумываюсь",
]


def normalize_reply_text(text: str, max_chars: int = 280) -> str:
    """Убирает повторы и подрезает слишком длинные простыни для группового чата."""
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    # Вырезаем строки с запрещёнными паттернами
    lines = text.split('\n')
    lines = [l for l in lines if not any(bp in l.lower() for bp in BANNED_PHRASES)]
    text = '\n'.join(lines).strip()

    # Убираем дословно повторяющиеся абзацы/строки
    blocks = [b.strip() for b in re.split(r'\n+', text) if b.strip()]
    uniq_blocks = []
    seen = set()
    for b in blocks:
        key = re.sub(r'\s+', ' ', b.lower()).strip(' .,!?:;')
        if key in seen:
            continue
        seen.add(key)
        uniq_blocks.append(b)
    text = '\n'.join(uniq_blocks)

    # Если модель нагенерила длинную простыню без переносов — режем по предложениям без дублей
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', text) if s.strip()]
    uniq_sentences = []
    seen = set()
    for s in sentences:
        key = re.sub(r'\s+', ' ', s.lower()).strip(' .,!?:;')
        if key in seen:
            continue
        seen.add(key)
        uniq_sentences.append(s)

    text = ' '.join(uniq_sentences).strip()

    if len(text) > max_chars:
        cut = text[:max_chars]
        m = re.search(r'^(.+[.!?])\s+[^.!?]*$', cut)
        text = m.group(1).strip() if m else cut.rstrip() + '…'

    return text


# ─── Опечатки ───

def add_typos(text: str, intensity: float = 0.03) -> tuple[str, str | None] | None:
    """Генерирует опечатку в тексте.

    Возвращает:
        (typo_text, correction) — текст с опечаткой и исправление (*слово)
        None — если без опечатки

    Типы опечаток:
    1. Соседняя клавиша (40%) — "привет" → "проивет"
    2. Перестановка букв (25%) — "привет" → "приевт"
    3. Пропуск буквы (15%) — "привет" → "привт"
    4. Удвоение буквы (10%) — "привет" → "приввет"
    5. Пропуск пробела (10%) — "привет как" → "приветкак"
    """
    if random.random() > intensity or len(text) < 15:
        return None

    words = text.split()
    if len(words) < 2:
        return None

    # Выбираем слово для опечатки (не первое и не последнее — менее заметно)
    eligible = [i for i, w in enumerate(words) if len(w) >= 4 and w.isalpha()]
    if not eligible:
        return None

    word_idx = random.choice(eligible)
    word = words[word_idx]

    typo_type = random.choices(
        ['neighbor', 'swap', 'skip', 'double', 'nospace'],
        weights=[40, 25, 15, 10, 10],
        k=1
    )[0]

    typo_word = _make_typo(word, typo_type)
    if typo_word == word:
        return None  # не получилось сделать опечатку

    # Собираем текст с опечаткой
    typo_words = words.copy()

    if typo_type == 'nospace' and word_idx < len(words) - 1:
        # Склеиваем два слова
        typo_words[word_idx] = words[word_idx] + words[word_idx + 1]
        typo_words.pop(word_idx + 1)
    else:
        typo_words[word_idx] = typo_word

    typo_text = ' '.join(typo_words)

    # Исправление: *правильное_слово (как люди делают в чате)
    correction = f'*{word}'

    return (typo_text, correction)


def _make_typo(word: str, typo_type: str) -> str:
    """Делает опечатку в слове."""
    chars = list(word)

    if typo_type == 'neighbor':
        # Заменяем букву на соседнюю по клавиатуре
        pos = random.randint(1, len(chars) - 2)  # не первую и не последнюю
        char_lower = chars[pos].lower()
        neighbors = KEYBOARD_NEIGHBORS.get(char_lower, '')
        if neighbors:
            replacement = random.choice(neighbors)
            if chars[pos].isupper():
                replacement = replacement.upper()
            chars[pos] = replacement
        else:
            return word

    elif typo_type == 'swap':
        # Перестановка двух соседних букв
        pos = random.randint(1, len(chars) - 2)
        chars[pos], chars[pos + 1] = chars[pos + 1], chars[pos]

    elif typo_type == 'skip':
        # Пропускаем букву
        pos = random.randint(1, len(chars) - 2)
        chars.pop(pos)

    elif typo_type == 'double':
        # Удваиваем букву
        pos = random.randint(1, len(chars) - 2)
        chars.insert(pos, chars[pos])

    elif typo_type == 'nospace':
        return word  # обрабатывается в add_typos

    return ''.join(chars)


def maybe_add_typo_correction(parts: list[str], intensity: float = 0.04) -> list[str]:
    """Опечатки отключены: они выглядят палевно и засоряют чат."""
    return parts


# ─── Паузы между частями ───

def pause_between_parts(part_index: int, total_parts: int, chat_id: int = None) -> float:
    """Пауза между частями сообщения."""
    state = _get_chat_state(chat_id) if chat_id else None

    if state and state['active_dialog']:
        base = random.uniform(0.5, 2.0)
    else:
        base = random.uniform(1.0, 4.0)

    # Если это коррекция опечатки (обычно очень короткое) — быстро
    return base * _time_of_day_factor()
