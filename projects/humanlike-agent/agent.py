"""Главный модуль агента — Telethon userbot. Фаза 1: достоверность поведения."""

import asyncio
import logging
import random
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.messages import SetTypingRequest, ReadHistoryRequest, SendReactionRequest
from telethon.tl.types import SendMessageTypingAction, SendMessageCancelAction, ReactionEmoji

from config import API_ID, API_HASH, PHONE, SESSION_NAME, MAX_CONTEXT_MESSAGES

# Telethon built-in credentials (если свои не указаны)
TELETHON_API_ID = API_ID or 2040
TELETHON_API_HASH = API_HASH or "b18441a1ff607e10a989891a5462e627"

# StringSession из .env (стабильная, не ломается при рестартах)
import os as _os
STRING_SESSION = _os.environ.get("STRING_SESSION", "")
from memory import init_db, save_message, get_chat_history, get_chat_mission
from persona import build_system_prompt, format_chat_for_llm
from human_simulation import (
    simulate_reading, simulate_thinking, calculate_typing_duration,
    calculate_typing_chunks, should_reply, split_message,
    maybe_add_typo_correction, is_night,
    update_incoming, update_outgoing, simulate_app_opening,
    should_delay_response, pause_between_parts, normalize_reply_text,
)
from llm_client import ask_llm
from rag_client import search as rag_search, load_index as load_rag_index
from commands import is_command, handle_command, is_owner
from chat_learner import (
    init_learner_db, update_chat_style, build_style_instructions,
    get_adaptive_max_tokens,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Клиент
if STRING_SESSION:
    client = TelegramClient(StringSession(STRING_SESSION), TELETHON_API_ID, TELETHON_API_HASH)
else:
    SESSION_PATH = _os.path.join("/opt/humanlike-agent", SESSION_NAME)
    client = TelegramClient(SESSION_PATH, TELETHON_API_ID, TELETHON_API_HASH)

# Антифлуд: не отвечать на своё же
MY_ID = None

# Отложенные ответы (chat_id -> asyncio.Task)
_delayed_tasks: dict[int, asyncio.Task] = {}

# Активные генерации/отправки (chat_id -> asyncio.Task)
_active_reply_tasks: dict[int, asyncio.Task] = {}

# Счётчик поколений ответа по чату: новое сообщение инвалидирует старую генерацию
_reply_generation: dict[int, int] = {}

# Дебаунс: накапливаем сообщения перед ответом
# chat_id -> {"task": asyncio.Task, "events": [(event, first_name, text)], "generation": int}
_debounce: dict[int, dict] = {}
DEBOUNCE_SECONDS = 8  # ждём паузу в потоке сообщений

# Счётчик сообщений для реакций
_msg_counter: dict[int, int] = {}
REACTION_EVERY = 7  # ставить реакцию примерно каждые N сообщений
REACTION_EMOJIS = ["👍", "😄", "🔥", "👀", "💯", "🤔", "👏", "😅"]

# Чаты, о которых уже уведомили владельца
_notified_chats: set[int] = set()


async def _maybe_react(event, chat_id: int):
    """Ставит случайную реакцию на сообщение."""
    try:
        emoji = random.choice(REACTION_EMOJIS)
        await asyncio.sleep(random.uniform(0.5, 3.0))  # задержка как у человека
        await client(SendReactionRequest(
            peer=chat_id,
            msg_id=event.id,
            reaction=[ReactionEmoji(emoticon=emoji)],
        ))
        logger.info(f"Reacted {emoji} in {chat_id}")
    except Exception as e:
        logger.debug(f"React failed: {e}")


async def _notify_owner(text: str):
    """Отправить уведомление владельцу."""
    from config import OWNER_ID
    try:
        await client.send_message(OWNER_ID, text)
    except Exception as e:
        logger.error(f"Failed to notify owner: {e}")


async def get_my_id():
    global MY_ID
    me = await client.get_me()
    MY_ID = me.id
    logger.info(f"Agent ID: {MY_ID}, username: @{me.username}, name: {me.first_name}")


async def send_typing(chat_id: int, typing: bool):
    """Отправить статус typing/stop typing."""
    try:
        action = SendMessageTypingAction() if typing else SendMessageCancelAction()
        await client(SetTypingRequest(chat_id, action))
    except Exception:
        pass


async def mark_as_read(chat_id: int, max_id: int):
    """Пометить сообщения как прочитанные."""
    try:
        await client(ReadHistoryRequest(
            peer=chat_id,
            max_id=max_id,
        ))
    except Exception as e:
        logger.debug(f"Could not mark as read: {e}")


async def do_typing_animation(chat_id: int, text: str):
    """Реалистичная анимация печати с паузами."""
    chunks = calculate_typing_chunks(text, chat_id)

    for duration, show_typing in chunks:
        if show_typing:
            await send_typing(chat_id, True)
        else:
            await send_typing(chat_id, False)
        await asyncio.sleep(duration)

    await send_typing(chat_id, False)


@client.on(events.NewMessage)
async def handle_message(event):
    """Обработка входящих сообщений."""
    global MY_ID

    # Пропускаем свои сообщения
    if event.sender_id == MY_ID:
        return

    # Пропускаем сервисные сообщения
    if not event.text:
        return

    # ─── Команды управления (от владельца) ───
    if is_command(event.text) and is_owner(event.sender_id):
        response = await handle_command(event, client)
        if response:
            await event.reply(response)
        return

    sender = await event.get_sender()
    chat = await event.get_chat()
    chat_id = event.chat_id
    is_private = event.is_private

    username = getattr(sender, "username", "") or ""
    first_name = getattr(sender, "first_name", "") or ""
    text = event.text

    logger.info(f"MSG [{chat_id}] {first_name} (@{username}): {text[:80]}")

    # Жёсткий ночной режим: 00:00-07:00 — полная тишина
    from datetime import datetime
    hour = datetime.now().hour
    if 0 <= hour < 7 and not is_private:
        return

    # Трекинг активности
    update_incoming(chat_id)

    # Сохраняем сообщение в память
    save_message(chat_id, event.sender_id, username, first_name, text)

    # Обучение на стиле чата
    update_chat_style(chat_id, text, user_id=event.sender_id, is_agent=False)

    # ─── Реакции эмодзи (вместо ответа) ───
    _msg_counter[chat_id] = _msg_counter.get(chat_id, 0) + 1
    if not is_private and _msg_counter[chat_id] % REACTION_EVERY == 0:
        if random.random() < 0.6:  # 60% шанс поставить реакцию
            await _maybe_react(event, chat_id)
            # Не прерываем — реакция может быть И до ответа

    # Проверяем миссию чата
    mission = get_chat_mission(chat_id)
    if mission and not mission.get("active", True):
        return  # Миссия отключена

    # Авто-обнаружение: уведомляем владельца о новом чате без миссии
    if not mission and not is_private and chat_id not in _notified_chats:
        _notified_chats.add(chat_id)
        chat_title = getattr(chat, 'title', str(chat_id))
        await _notify_owner(
            f"🆕 Новый чат без миссии:\n"
            f"{chat_title} ({chat_id})\n\n"
            f"Назначить: /mission {chat_id} expert [имя]"
        )

    # Проверяем, упомянули ли нас
    mentioned = False
    is_reply = False

    if event.is_reply:
        replied = await event.get_reply_message()
        if replied and replied.sender_id == MY_ID:
            is_reply = True

    me = await client.get_me()
    my_names = [me.first_name, me.username]
    for name in my_names:
        if name and name.lower() in text.lower():
            mentioned = True
    # Также проверяем упоминание через tg://user ссылку
    if str(MY_ID) in text:
        mentioned = True
    # Проверяем entities сообщения (mention)
    if event.message and event.message.entities:
        for entity in event.message.entities:
            if hasattr(entity, 'user_id') and entity.user_id == MY_ID:
                mentioned = True

    # Продолжение диалога?
    is_continuation = False
    history = get_chat_history(chat_id, 5)
    if history:
        user_msgs_after_agent = 0
        for msg in reversed(history):
            if msg["is_agent"]:
                looks_like_followup = any(x in text.lower() for x in [
                    "?", "а ты", "а как", "что думаешь", "почему", "как", "зачем",
                    "расскажи", "объясни", "уточни", "имеешь в виду", "то есть",
                    "подробнее", "можно подробнее", "в смысле", "то есть как"
                ])
                # continuation только если это правда короткое уточнение
                # сразу после нашего ответа, а не обычная болтовня в группе.
                is_continuation = (user_msgs_after_agent == 1 and looks_like_followup and len(text) <= 220)
                break
            elif msg["user_id"] == event.sender_id:
                user_msgs_after_agent += 1
            else:
                break

    # Решаем, отвечать ли
    triggers = mission.get("triggers", []) if mission else []

    # В группах отвечаем только если:
    # 1) был прямой reply/mention,
    # 2) это короткое осмысленное уточнение после нашего ответа,
    # 3) или это явный вопрос/триггер.
    if not is_private and not is_continuation and not should_reply(text, triggers, mentioned, is_reply):
        logger.info(f"SKIP in {chat_id} from {first_name}: reply={is_reply}, mention={mentioned}, cont={is_continuation}, triggers_hit=false")
        return

    logger.info(f"Will reply in {chat_id} to {first_name} (reply={is_reply}, mention={mentioned}, cont={is_continuation})")

    # Новое сообщение инвалидирует все прошлые незавершённые ответы по чату
    generation = _reply_generation.get(chat_id, 0) + 1
    _reply_generation[chat_id] = generation

    if chat_id in _delayed_tasks:
        _delayed_tasks[chat_id].cancel()
        del _delayed_tasks[chat_id]

    if chat_id in _active_reply_tasks:
        _active_reply_tasks[chat_id].cancel()
        del _active_reply_tasks[chat_id]

    # ─── Дебаунс: ждём паузу в потоке сообщений ───
    # На прямой mention/reply отвечаем сразу, без дебаунса.
    if is_reply or mentioned or is_private:
        task = asyncio.create_task(_process_reply_flow(
            event, chat_id, first_name, text, mission,
            is_private, is_reply, mentioned, is_continuation, generation,
        ))
        _active_reply_tasks[chat_id] = task
    else:
        # Дебаунс: накапливаем, ждём паузу
        if chat_id in _debounce:
            _debounce[chat_id]["events"].append((event, first_name, text))
            _debounce[chat_id]["task"].cancel()
        else:
            _debounce[chat_id] = {"events": [(event, first_name, text)]}

        _debounce[chat_id]["generation"] = generation
        _debounce[chat_id]["mission"] = mission
        _debounce[chat_id]["is_continuation"] = is_continuation
        _debounce[chat_id]["task"] = asyncio.create_task(
            _debounce_wait(chat_id, generation)
        )


async def _debounce_wait(chat_id: int, generation: int):
    """Ждёт паузу в потоке сообщений, потом отвечает на последнее."""
    try:
        await asyncio.sleep(DEBOUNCE_SECONDS)
        if _reply_generation.get(chat_id) != generation:
            return

        buf = _debounce.pop(chat_id, None)
        if not buf or not buf["events"]:
            return

        # Берём последнее сообщение как контекст для ответа
        last_event, last_first_name, last_text = buf["events"][-1]
        mission = buf.get("mission")
        is_continuation = buf.get("is_continuation", False)

        logger.info(f"Debounce fired in {chat_id}: {len(buf['events'])} msgs accumulated, replying to last")

        task = asyncio.create_task(_process_reply_flow(
            last_event, chat_id, last_first_name, last_text, mission,
            False, False, False, is_continuation, generation,
        ))
        _active_reply_tasks[chat_id] = task
    except asyncio.CancelledError:
        pass


async def _process_reply_flow(event, chat_id: int, first_name: str, text: str,
                              mission: dict | None, is_private: bool,
                              is_reply: bool, mentioned: bool,
                              is_continuation: bool, generation: int):
    """Один актуальный pipeline ответа на чат.
    Если пришло новое сообщение, generation изменится и старый pipeline должен умереть."""
    try:
        # 1. Имитация "открытия приложения"
        if not is_private or not (is_reply or mentioned):
            await simulate_app_opening(chat_id)
        if _reply_generation.get(chat_id) != generation:
            return

        # 2. Помечаем прочитанным
        await mark_as_read(chat_id, event.id)

        # 3. Проверяем "прочитал, но ответит позже"
        should_delay, delay_secs = should_delay_response(chat_id)
        if should_delay and not (is_reply or mentioned):
            logger.info(f"Delaying response in {chat_id} by {delay_secs:.0f}s")
            task = asyncio.create_task(_delayed_reply(
                event, chat_id, first_name, text, mission, delay_secs, generation
            ))
            _delayed_tasks[chat_id] = task
            return

        # 4. Чтение + размышление
        if is_reply or mentioned:
            await asyncio.sleep(random.uniform(0.2, 0.8))
        elif is_continuation:
            await asyncio.sleep(random.uniform(0.4, 1.2))
        else:
            await simulate_reading(len(text))
            await simulate_thinking(chat_id)

        if _reply_generation.get(chat_id) != generation:
            return

        # 5. Генерация и отправка ответа
        await _generate_and_send(event, chat_id, first_name, text, mission, generation)
    except asyncio.CancelledError:
        logger.info(f"Reply flow in {chat_id} cancelled (new message)")
    finally:
        if _active_reply_tasks.get(chat_id) is asyncio.current_task():
            _active_reply_tasks.pop(chat_id, None)


async def _delayed_reply(event, chat_id: int, first_name: str, text: str,
                         mission: dict | None, delay: float, generation: int):
    """Отложенный ответ — "прочитал, ответил позже"."""
    try:
        await asyncio.sleep(delay)
        if _reply_generation.get(chat_id) != generation:
            return
        logger.info(f"Sending delayed reply in {chat_id}")
        await simulate_thinking(chat_id)
        if _reply_generation.get(chat_id) != generation:
            return
        await _generate_and_send(event, chat_id, first_name, text, mission, generation)
    except asyncio.CancelledError:
        logger.info(f"Delayed reply in {chat_id} cancelled (new message)")
    finally:
        if _delayed_tasks.get(chat_id) is asyncio.current_task():
            _delayed_tasks.pop(chat_id, None)


async def _generate_and_send(event, chat_id: int, first_name: str, text: str,
                              mission: dict | None, generation: int):
    """Генерирует ответ LLM и отправляет с реалистичной анимацией."""
    # Получаем историю чата
    history = get_chat_history(chat_id, MAX_CONTEXT_MESSAGES)
    llm_history = format_chat_for_llm(history)

    # RAG: best effort. Для живого чата важнее ответить быстро, чем ждать поиск.
    rag_context = ""
    try:
        rag_context = await asyncio.wait_for(rag_search(text, top_k=3), timeout=1.5)
    except asyncio.TimeoutError:
        logger.warning(f"RAG timeout in {chat_id}; replying without RAG")
    except Exception as e:
        logger.error(f"RAG error: {e}")

    # Промпт
    system_prompt = build_system_prompt(mission)

    # Адаптация стиля на основе обучения
    style_instructions = build_style_instructions(chat_id)
    if style_instructions:
        system_prompt += style_instructions

    alpha_topic = any(x in text.lower() for x in ["alpha", "альфа", "alpha.hmi", "alpha.server", "alpha.om", "webviewer", "historian", "devstudio", "типизац", "мнемо", "scada"])

    if rag_context:
        system_prompt += (
            f"\n\n## Твои знания по этой теме (ОБЯЗАТЕЛЬНО используй!):\n"
            f"Это то, что ты реально знаешь из своего опыта. Отвечай на основе этого, своими словами, кратко. "
            f"Не говори 'не знаю' или 'не работал' если информация есть ниже.\n\n{rag_context}"
        )
    elif alpha_topic:
        system_prompt += (
            "\n\n## ВАЖНО ПО АЛЬФЕ\n"
            "RAG-контекст не найден. Значит нельзя уверенно утверждать детали по продукту. "
            "Не выдумывай API, классы, методы, языки, внутренние механизмы и названия модулей. "
            "Если спросят по деталям — скажи, что точно не помнишь и надо смотреть документацию."
        )

    llm_history.append({"role": "user", "content": f"[{first_name}]: {text}"})

    # Адаптивный max_tokens
    max_tokens = get_adaptive_max_tokens(chat_id)

    # Спрашиваем LLM
    reply = await ask_llm(system_prompt, llm_history, max_tokens=max_tokens)

    if not reply:
        logger.info(f"LLM decided to skip or failed")
        return

    reply = normalize_reply_text(reply)

    if not reply:
        logger.info(f"Reply became empty after normalization")
        return

    # Разбиваем на части
    parts = split_message(reply)

    # Может добавить опечатку + исправление
    parts = maybe_add_typo_correction(parts, intensity=0.04)

    # Отправляем части
    for i, part in enumerate(parts):
        if _reply_generation.get(chat_id) != generation:
            logger.info(f"Abort stale send in {chat_id}: generation changed before part {i+1}")
            return

        # Анимация печати
        await do_typing_animation(chat_id, part)

        if _reply_generation.get(chat_id) != generation:
            logger.info(f"Abort stale send in {chat_id}: generation changed after typing part {i+1}")
            return

        # Отправка
        await event.respond(part)
        save_message(chat_id, MY_ID, "", "Agent", part, is_agent=True)
        update_outgoing(chat_id)

        # Пауза между частями
        if i < len(parts) - 1:
            delay = pause_between_parts(i, len(parts), chat_id)
            await asyncio.sleep(delay)


async def main():
    init_db()
    init_learner_db()
    load_rag_index()
    await client.connect()

    if not await client.is_user_authorized():
        logger.error("Not authorized! Session file is invalid or missing.")
        logger.error("Run manually: cd /opt/humanlike-agent && source venv/bin/activate && python agent.py")
        logger.error("Exiting to avoid flood-requesting codes.")
        import sys
        sys.exit(1)
    else:
        logger.info("Session restored, already authorized")

    await get_my_id()
    await catch_up_missed()

    logger.info("HumanLike agent started! (Phase 1: realistic behavior)")
    await client.run_until_disconnected()


async def catch_up_missed():
    """Проверяет непрочитанные диалоги и отвечает на упоминания."""
    logger.info("Checking for missed messages...")
    try:
        dialogs = await client.get_dialogs(limit=20)
        for dialog in dialogs:
            if dialog.unread_count == 0:
                continue

            chat_id = dialog.id
            logger.info(f"Unread in {dialog.name}: {dialog.unread_count} messages")

            messages = await client.get_messages(chat_id, limit=dialog.unread_count)

            for msg in reversed(messages):
                if not msg.text or msg.sender_id == MY_ID:
                    continue
                if msg.sender_id == 777000:
                    continue

                sender = await msg.get_sender()
                first_name = getattr(sender, "first_name", "") or ""
                username = getattr(sender, "username", "") or ""
                text = msg.text

                save_message(chat_id, msg.sender_id, username, first_name, text)

                me = await client.get_me()
                mentioned = False
                for name in [me.first_name, me.username]:
                    if name and name.lower() in text.lower():
                        mentioned = True

                is_reply = False
                if msg.reply_to and msg.reply_to.reply_to_msg_id:
                    try:
                        replied = await client.get_messages(chat_id, ids=msg.reply_to.reply_to_msg_id)
                        if replied and replied.sender_id == MY_ID:
                            is_reply = True
                    except Exception:
                        pass

                is_private = not dialog.is_group and not dialog.is_channel
                if not is_private and not mentioned and not is_reply:
                    continue

                logger.info(f"Catch-up reply to {first_name} in {dialog.name}: {text[:50]}")

                history = get_chat_history(chat_id, MAX_CONTEXT_MESSAGES)
                llm_history = format_chat_for_llm(history)

                mission = get_chat_mission(chat_id)
                system_prompt = build_system_prompt(mission)

                llm_history.append({"role": "user", "content": f"[{first_name}]: {text}"})

                reply = await ask_llm(system_prompt, llm_history, max_tokens=500)
                if reply:
                    parts = split_message(reply)
                    parts = maybe_add_typo_correction(parts, intensity=0.04)

                    for i, part in enumerate(parts):
                        await do_typing_animation(chat_id, part)
                        await msg.reply(part)
                        save_message(chat_id, MY_ID, "", "Agent", part, is_agent=True)
                        update_outgoing(chat_id)
                        if i < len(parts) - 1:
                            await asyncio.sleep(random.uniform(1, 3))

                    await asyncio.sleep(random.uniform(2, 5))

        logger.info("Catch-up complete")
    except Exception as e:
        logger.error(f"Catch-up error: {e}")


if __name__ == "__main__":
    try:
        client.loop.run_until_complete(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
    # НЕ вызываем client.disconnect() — это инвалидирует сессию!
