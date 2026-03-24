"""Telegram-команды для управления агентом (только от владельца)."""

import logging
import json
from config import OWNER_ID, MISSION_TEMPLATES
from memory import (
    set_chat_mission, get_chat_mission, get_chat_stats,
    get_all_missions, toggle_mission, delete_mission,
)
from chat_learner import get_chat_style, get_active_users

logger = logging.getLogger(__name__)


def is_owner(user_id: int) -> bool:
    """Проверяет, является ли пользователь владельцем."""
    return user_id == OWNER_ID


def is_command(text: str) -> bool:
    """Проверяет, является ли текст командой агента."""
    return text.startswith('/') and any(
        text.startswith(cmd) for cmd in [
            '/mission', '/stats', '/chats', '/pause', '/resume',
            '/templates', '/help_agent', '/delete_mission', '/style',
        ]
    )


async def handle_command(event, client) -> str | None:
    """Обрабатывает команду. Возвращает текст ответа или None."""
    if not is_owner(event.sender_id):
        return None

    text = event.text.strip()
    parts = text.split(maxsplit=3)
    cmd = parts[0].lower()

    # Убираем @username из команды если есть
    if '@' in cmd:
        cmd = cmd.split('@')[0]

    try:
        if cmd == '/mission':
            return await cmd_mission(parts[1:], event, client)
        elif cmd == '/stats':
            return await cmd_stats(parts[1:], event)
        elif cmd == '/chats':
            return await cmd_chats()
        elif cmd == '/pause':
            return await cmd_toggle(parts[1:], active=False)
        elif cmd == '/resume':
            return await cmd_toggle(parts[1:], active=True)
        elif cmd == '/templates':
            return cmd_templates()
        elif cmd == '/delete_mission':
            return await cmd_delete(parts[1:])
        elif cmd == '/style':
            return await cmd_style(parts[1:], event)
        elif cmd == '/help_agent':
            return cmd_help()
        else:
            return None
    except Exception as e:
        logger.error(f"Command error: {e}")
        return f"❌ Ошибка: {e}"


async def cmd_mission(args: list, event, client) -> str:
    """Установить миссию.

    Форматы:
        /mission expert              — применить шаблон к ТЕКУЩЕМУ чату
        /mission -100123 expert      — применить шаблон к указанному чату
        /mission expert Алексей      — шаблон + кастомное имя
        /mission custom ...          — JSON-конфиг
    """
    if not args:
        return (
            "📋 Использование:\n"
            "/mission <шаблон> [имя]\n"
            "/mission <chat_id> <шаблон> [имя]\n\n"
            "Шаблоны: " + ", ".join(MISSION_TEMPLATES.keys()) + "\n"
            "Подробнее: /templates"
        )

    # Определяем chat_id и шаблон
    chat_id = event.chat_id
    template_name = args[0]
    custom_name = None

    # Если первый аргумент — число, это chat_id
    try:
        maybe_id = int(args[0])
        chat_id = maybe_id
        if len(args) < 2:
            return "❌ Укажи шаблон: /mission <chat_id> <шаблон>"
        template_name = args[1]
        custom_name = args[2] if len(args) > 2 else None
    except ValueError:
        custom_name = args[1] if len(args) > 1 else None

    # Ищем шаблон
    if template_name not in MISSION_TEMPLATES:
        return f"❌ Неизвестный шаблон: {template_name}\nДоступные: {', '.join(MISSION_TEMPLATES.keys())}"

    template = MISSION_TEMPLATES[template_name]

    persona = template["persona"]
    if custom_name:
        persona = f"{custom_name}. {persona}"

    set_chat_mission(
        chat_id,
        mission=template["mission"],
        persona=persona,
        style=template["style"],
        goals=template["goals"],
        triggers=template["triggers"],
    )

    # Пробуем получить название чата
    chat_name = str(chat_id)
    try:
        entity = await client.get_entity(chat_id)
        chat_name = getattr(entity, 'title', None) or getattr(entity, 'first_name', str(chat_id))
    except Exception:
        pass

    return (
        f"✅ Миссия установлена!\n\n"
        f"Чат: {chat_name} ({chat_id})\n"
        f"Тип: {template_name}\n"
        f"Персона: {persona}\n"
        f"Стиль: {template['style'][:50]}...\n"
        f"Триггеры: {', '.join(template['triggers'][:5])}{'...' if len(template['triggers']) > 5 else ''}"
    )


async def cmd_stats(args: list, event) -> str:
    """Статистика чата."""
    chat_id = event.chat_id
    if args:
        try:
            chat_id = int(args[0])
        except ValueError:
            return "❌ Укажи chat_id числом"

    stats = get_chat_stats(chat_id)
    mission = get_chat_mission(chat_id)

    result = f"📊 Статистика чата {chat_id}\n\n"
    result += f"Всего сообщений: {stats['total_messages']}\n"
    result += f"Ответов агента: {stats['agent_messages']}\n"
    result += f"Уникальных юзеров: {stats['unique_users']}\n"

    if stats['total_messages'] > 0:
        ratio = stats['agent_messages'] / stats['total_messages'] * 100
        result += f"Доля агента: {ratio:.1f}%\n"

    if mission:
        result += f"\nМиссия: {mission['mission']}\n"
        result += f"Персона: {mission.get('persona', '-')}\n"
        result += f"Активна: {'✅' if mission.get('active', True) else '⏸'}\n"
    else:
        result += "\n⚠️ Миссия не назначена"

    return result


async def cmd_chats() -> str:
    """Список всех чатов с миссиями."""
    missions = get_all_missions()

    if not missions:
        return "📭 Нет активных миссий.\nНазначь: /mission <шаблон>"

    result = "📋 Миссии агента:\n\n"
    for m in missions:
        status = "✅" if m.get("active", True) else "⏸"
        chat_id = m["chat_id"]
        mission_type = m.get("mission", "?")
        persona = m.get("persona", "-")
        # Обрезаем длинную персону
        if len(persona) > 40:
            persona = persona[:37] + "..."
        result += f"{status} {chat_id}: {mission_type} — {persona}\n"

    result += f"\nВсего: {len(missions)}"
    return result


async def cmd_toggle(args: list, active: bool) -> str:
    """Пауза/возобновление миссии."""
    if not args:
        return f"❌ Укажи chat_id: /{'resume' if active else 'pause'} <chat_id>"

    try:
        chat_id = int(args[0])
    except ValueError:
        return "❌ chat_id должен быть числом"

    mission = get_chat_mission(chat_id)
    if not mission:
        return f"❌ Миссия для чата {chat_id} не найдена"

    toggle_mission(chat_id, active)

    action = "возобновлена ✅" if active else "приостановлена ⏸"
    return f"Миссия в чате {chat_id} {action}"


async def cmd_delete(args: list) -> str:
    """Удалить миссию."""
    if not args:
        return "❌ Укажи chat_id: /delete_mission <chat_id>"

    try:
        chat_id = int(args[0])
    except ValueError:
        return "❌ chat_id должен быть числом"

    delete_mission(chat_id)
    return f"🗑 Миссия для чата {chat_id} удалена"


def cmd_templates() -> str:
    """Показать доступные шаблоны."""
    result = "📦 Шаблоны миссий:\n\n"
    for name, t in MISSION_TEMPLATES.items():
        result += f"🔹 {name}\n"
        result += f"   Персона: {t['persona'][:50]}...\n"
        result += f"   Стиль: {t['style'][:50]}...\n"
        result += f"   Триггеры: {', '.join(t['triggers'][:4])}{'...' if len(t['triggers']) > 4 else ''}\n\n"

    result += "Применить: /mission <шаблон> [имя персонажа]"
    return result


async def cmd_style(args: list, event) -> str:
    """Показать выученный стиль чата."""
    chat_id = event.chat_id
    if args:
        try:
            chat_id = int(args[0])
        except ValueError:
            return "❌ chat_id должен быть числом"

    style = get_chat_style(chat_id)
    if not style:
        return f"📊 Стиль чата {chat_id}: недостаточно данных (нужно минимум 5 сообщений)"

    formality_label = (
        "🎩 формальный" if style['formality'] > 0.6 else
        "👔 нейтральный" if style['formality'] > 0.35 else
        "🤙 неформальный"
    )

    result = (
        f"📊 Выученный стиль чата {chat_id}\n\n"
        f"Образцов: {style['samples_count']}\n"
        f"Средняя длина: {style['avg_msg_length']:.0f} символов\n"
        f"Формальность: {formality_label} ({style['formality']:.2f})\n"
        f"Emoji: {style['emoji_frequency']:.1f} на сообщение\n"
        f"Сленг: {style['slang_level']:.2f}\n"
        f"Пиковые часы: {', '.join(f'{h}:00' for h in style['peak_hours'])}\n"
        f"Рекомендуемая длина ответа: {style['typical_response_length']} символов\n"
    )

    users = get_active_users(chat_id, limit=5)
    if users:
        result += f"\nТоп юзеров ({len(users)}):\n"
        for u in users:
            f_label = "📝" if u['formality'] > 0.5 else "💬"
            result += f"  {f_label} {u['user_id']}: {u['message_count']} сообщ., длина ~{u['avg_msg_length']:.0f}\n"

    return result


def cmd_help() -> str:
    """Справка по командам."""
    return """🤖 HumanLike Agent — Команды

/mission <шаблон> [имя] — назначить миссию текущему чату
/mission <chat_id> <шаблон> [имя] — назначить миссию другому чату
/templates — список шаблонов миссий
/stats [chat_id] — статистика чата
/style [chat_id] — выученный стиль чата
/chats — все активные миссии
/pause <chat_id> — приостановить миссию
/resume <chat_id> — возобновить миссию
/delete_mission <chat_id> — удалить миссию
/help_agent — эта справка

Шаблоны: expert, salesman, observer, supporter

Примеры:
/mission expert Алексей
/mission -1001234567 salesman Дмитрий
/style -1001234567
/pause -1001234567"""
