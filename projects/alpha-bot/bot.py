"""Telegram-бот + веб-виджет для консультации по Альфа платформе.
Фаза 2: контекстная память."""

import os
import asyncio
import json
import logging
from dotenv import load_dotenv

load_dotenv()

from aiohttp import web
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
)

from llm import ask_llm
from rag import load_index
from conversation_memory import (
    init_db as init_conv_db, save_message, get_history, get_message_count,
    get_profile, update_profile, add_topic, is_followup, get_last_topic,
    build_context_prompt, extract_user_info, detect_topic,
    summarize_conversation, clear_session, get_stats,
)
from analytics import (
    init_analytics_db, analyze_and_track, format_analytics_telegram,
    get_full_analytics,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

MAX_HISTORY = 10
SUMMARIZE_THRESHOLD = 20  # саммаризировать после стольких сообщений


# ─── Telegram handlers ───

async def cmd_start(update: Update, context):
    session_id = f"tg_{update.effective_chat.id}"
    profile = get_profile(session_id)

    if profile and profile.get("display_name"):
        greeting = (
            f"С возвращением, {profile['display_name']}! 👋\n\n"
            "Рад снова вас видеть. Чем могу помочь сегодня?"
        )
        if profile.get("topics_asked"):
            last_topic = profile["topics_asked"][-1]
            greeting += f"\n\nВ прошлый раз мы обсуждали: {last_topic}"
    else:
        greeting = (
            "Здравствуйте! 👋\n\n"
            "Я — консультант по Альфа платформе (SCADA) от компании «Специальные Технологии».\n\n"
            "Задайте мне вопрос о продуктах, модулях, возможностях платформы — и я постараюсь помочь.\n\n"
            "Например:\n"
            "• Какие модули входят в Альфа платформу?\n"
            "• Чем Alpha.SCADA отличается от Alpha.One+?\n"
            "• Какие протоколы поддерживает Alpha.Server?"
        )

    await update.message.reply_text(greeting)


async def cmd_reset(update: Update, context):
    session_id = f"tg_{update.effective_chat.id}"
    clear_session(session_id)
    await update.message.reply_text("История диалога очищена. Задайте новый вопрос!")


async def cmd_stats_handler(update: Update, context):
    """Статистика бота (для админа)."""
    stats = get_stats()
    session_id = f"tg_{update.effective_chat.id}"
    profile = get_profile(session_id)

    text = (
        f"📊 Статистика бота\n\n"
        f"Всего сообщений: {stats['total_messages']}\n"
        f"Уникальных сессий: {stats['total_sessions']}\n"
        f"Профилей: {stats['total_profiles']}\n"
    )
    if profile:
        text += (
            f"\n--- Ваш профиль ---\n"
            f"Имя: {profile.get('display_name', '-')}\n"
            f"Компания: {profile.get('company', '-')}\n"
            f"Сообщений: {profile.get('message_count', 0)}\n"
            f"Тем: {len(profile.get('topics_asked', []))}\n"
        )
    await update.message.reply_text(text)


async def cmd_analytics_handler(update: Update, context):
    """Полная аналитика (для админа)."""
    args = context.args
    days = 30
    if args:
        try:
            days = int(args[0])
        except ValueError:
            pass

    report = format_analytics_telegram(days)
    await update.message.reply_text(report)


async def handle_message(update: Update, context):
    chat_id = update.effective_chat.id
    session_id = f"tg_{chat_id}"
    user_text = update.message.text
    user = update.effective_user

    if not user_text or not user_text.strip():
        return

    # Показываем "печатает..."
    await update.effective_chat.send_action("typing")

    # Сохраняем сообщение и трекаем аналитику
    save_message(session_id, "user", user_text)
    analyze_and_track(session_id, user_text, is_user=True)

    # Обновляем имя пользователя
    if user:
        display_name = user.first_name or user.username or ""
        profile = get_profile(session_id)
        if profile and not profile.get("display_name") and display_name:
            update_profile(session_id, display_name=display_name)

    # Извлекаем информацию о пользователе
    user_info = extract_user_info(user_text)
    if user_info:
        for key, value in user_info.items():
            update_profile(session_id, **{key: value})
        logger.info(f"Extracted user info: {user_info}")

    # Детектируем тему
    topic = detect_topic(user_text)
    if topic:
        add_topic(session_id, topic)

    # Получаем историю для LLM
    history = get_history(session_id, limit=MAX_HISTORY)
    llm_history = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]  # без текущего

    # Follow-up детекция
    if is_followup(user_text, llm_history):
        last_topic = get_last_topic(history)
        if last_topic:
            # Дополняем запрос контекстом
            user_text_enhanced = f"(Продолжение вопроса про: {last_topic[:100]})\n{user_text}"
            logger.info(f"Follow-up detected, context: {last_topic[:50]}")
        else:
            user_text_enhanced = user_text
    else:
        user_text_enhanced = user_text

    # Контекстный промпт
    context_prompt = build_context_prompt(session_id, user_text)

    # Спрашиваем LLM
    answer = await ask_llm(user_text_enhanced, llm_history, extra_context=context_prompt)

    # Сохраняем ответ
    save_message(session_id, "assistant", answer)

    # Саммаризация если диалог стал длинным
    msg_count = get_message_count(session_id)
    if msg_count > 0 and msg_count % SUMMARIZE_THRESHOLD == 0:
        asyncio.create_task(_do_summarize(session_id))

    await update.message.reply_text(answer)


async def _do_summarize(session_id: str):
    """Фоновая саммаризация."""
    try:
        summary = await summarize_conversation(session_id, _summarize_llm)
        if summary:
            logger.info(f"Auto-summarized {session_id}")
    except Exception as e:
        logger.error(f"Summarize error: {e}")


async def _summarize_llm(prompt: str, messages: list[dict]) -> str:
    """Обёртка для LLM-саммаризации."""
    return await ask_llm(prompt, messages)


# ─── Web widget API ───

WIDGET_HTML = """<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Альфа Платформа — Консультант</title>
<style>
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body { background: transparent !important; overflow: hidden; }
body { background-color: transparent !important; }

#alpha-chat-btn { display: none; }

#alpha-chat-widget {
    position: fixed; bottom: 0; right: 0; left: 0; top: 0;
    width: 100%; height: 100%;
    background: #fff;
    display: flex; flex-direction: column; overflow: hidden;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
}

#alpha-chat-header {
    background: linear-gradient(135deg, #0066cc, #004499);
    color: white; padding: 16px 20px;
    display: flex; align-items: center; justify-content: space-between;
}
#alpha-chat-header h3 { font-size: 15px; font-weight: 600; }
#alpha-chat-close { background: none; border: none; color: white; font-size: 20px; cursor: pointer; }

#alpha-chat-messages {
    flex: 1; overflow-y: auto; padding: 16px;
    display: flex; flex-direction: column; gap: 10px;
}

.msg { max-width: 85%; padding: 10px 14px; border-radius: 12px; font-size: 14px; line-height: 1.5; word-wrap: break-word; }
.msg-bot { background: #f0f4f8; color: #1a1a1a; align-self: flex-start; border-bottom-left-radius: 4px; }
.msg-user { background: #0066cc; color: white; align-self: flex-end; border-bottom-right-radius: 4px; }

#alpha-chat-input-wrap {
    display: flex; padding: 12px; border-top: 1px solid #e8e8e8; gap: 8px;
}
#alpha-chat-input {
    flex: 1; border: 1px solid #ddd; border-radius: 8px; padding: 10px 12px;
    font-size: 14px; outline: none; resize: none;
}
#alpha-chat-input:focus { border-color: #0066cc; }
#alpha-chat-send {
    background: #0066cc; color: white; border: none; border-radius: 8px;
    padding: 10px 16px; cursor: pointer; font-size: 14px; font-weight: 500;
}
#alpha-chat-send:hover { background: #004499; }
#alpha-chat-send:disabled { opacity: 0.5; cursor: not-allowed; }

.typing-indicator { display: flex; gap: 4px; padding: 10px 14px; align-self: flex-start; }
.typing-indicator span {
    width: 8px; height: 8px; border-radius: 50%; background: #ccc;
    animation: typing 1.2s infinite;
}
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }
@keyframes typing { 0%,100% { opacity: 0.3; } 50% { opacity: 1; } }

@media (max-width: 480px) {
    #alpha-chat-widget { width: calc(100vw - 16px); right: 8px; bottom: 88px; }
}
</style>
</head>
<body>

<button id="alpha-chat-btn" onclick="toggleChat()">
    <svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/><path d="M7 9h10v2H7zm0-3h10v2H7z"/></svg>
</button>

<div id="alpha-chat-widget">
    <div id="alpha-chat-header">
        <h3>💬 Альфа Платформа</h3>
        <button id="alpha-chat-close" onclick="toggleChat()">✕</button>
    </div>
    <div id="alpha-chat-messages">
        <div class="msg msg-bot">Здравствуйте! Я консультант по Альфа платформе. Чем могу помочь?</div>
    </div>
    <div id="alpha-chat-input-wrap">
        <input id="alpha-chat-input" placeholder="Введите вопрос..." onkeydown="if(event.key==='Enter')sendMsg()">
        <button id="alpha-chat-send" onclick="sendMsg()">→</button>
    </div>
</div>

<script>
const API_URL = window.ALPHA_BOT_API || '';
let sessionId = localStorage.getItem('alpha_session_id');
if (!sessionId) {
    sessionId = 'web_' + Math.random().toString(36).substr(2, 9);
    localStorage.setItem('alpha_session_id', sessionId);
}

function toggleChat() {
    if(window.parent !== window) {
        window.parent.postMessage('alpha-chat-close', '*');
    }
}

async function sendMsg() {
    const input = document.getElementById('alpha-chat-input');
    const text = input.value.trim();
    if (!text) return;

    const msgs = document.getElementById('alpha-chat-messages');
    msgs.innerHTML += '<div class="msg msg-user">' + escHtml(text) + '</div>';
    input.value = '';
    scrollBottom();

    const typing = document.createElement('div');
    typing.className = 'typing-indicator';
    typing.innerHTML = '<span></span><span></span><span></span>';
    msgs.appendChild(typing);
    scrollBottom();

    document.getElementById('alpha-chat-send').disabled = true;

    try {
        const resp = await fetch(API_URL + '/api/chat', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({message: text, session_id: sessionId})
        });
        const data = await resp.json();
        typing.remove();
        msgs.innerHTML += '<div class="msg msg-bot">' + escHtml(data.reply) + '</div>';
    } catch(e) {
        typing.remove();
        msgs.innerHTML += '<div class="msg msg-bot">Извините, произошла ошибка. Попробуйте позже.</div>';
    }

    document.getElementById('alpha-chat-send').disabled = false;
    scrollBottom();
}

function scrollBottom() {
    const msgs = document.getElementById('alpha-chat-messages');
    msgs.scrollTop = msgs.scrollHeight;
}

function escHtml(t) {
    return t.replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/\n/g,'<br>');
}
</script>
</body>
</html>"""


async def handle_api_chat(request: web.Request) -> web.Response:
    """API endpoint для веб-виджета."""
    try:
        data = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    message = data.get("message", "").strip()
    session_id = data.get("session_id", "web_anonymous")

    if not message:
        return web.json_response({"error": "Empty message"}, status=400)

    # Сохраняем сообщение и трекаем
    save_message(session_id, "user", message)
    analyze_and_track(session_id, message, is_user=True)

    # Извлекаем инфо
    user_info = extract_user_info(message)
    if user_info:
        for key, value in user_info.items():
            update_profile(session_id, **{key: value})

    topic = detect_topic(message)
    if topic:
        add_topic(session_id, topic)

    # История
    history = get_history(session_id, limit=MAX_HISTORY)
    llm_history = [{"role": m["role"], "content": m["content"]} for m in history[:-1]]

    # Follow-up
    if is_followup(message, llm_history):
        last_topic = get_last_topic(history)
        if last_topic:
            message_enhanced = f"(Продолжение вопроса про: {last_topic[:100]})\n{message}"
        else:
            message_enhanced = message
    else:
        message_enhanced = message

    # Контекст
    context_prompt = build_context_prompt(session_id, message)

    # LLM
    reply = await ask_llm(message_enhanced, llm_history, extra_context=context_prompt)

    # Сохраняем
    save_message(session_id, "assistant", reply)

    # Саммаризация
    msg_count = get_message_count(session_id)
    if msg_count > 0 and msg_count % SUMMARIZE_THRESHOLD == 0:
        asyncio.create_task(_do_summarize(session_id))

    return web.json_response({"reply": reply})


async def handle_widget(request: web.Request) -> web.Response:
    """Отдаёт HTML виджета."""
    return web.Response(text=WIDGET_HTML, content_type="text/html")


async def handle_widget_js(request: web.Request) -> web.Response:
    """Embeddable JS-скрипт для вставки на сайт."""
    port = os.getenv("PORT", "8090")
    host = request.headers.get("Host", f"localhost:{port}")
    forwarded_proto = request.headers.get("X-Forwarded-Proto", "")
    scheme = "https" if (request.secure or forwarded_proto == "https" or "bot.specialtechnology.ru" in host) else "http"
    base_url = f"{scheme}://{host}"

    js = f"""(function(){{
    if(document.getElementById('alpha-chat-fab')) return;

    var btn=document.createElement('div');
    btn.id='alpha-chat-fab';
    btn.innerHTML='<svg viewBox="0 0 24 24" width="28" height="28" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H5.17L4 17.17V4h16v12z"/><path d="M7 9h10v2H7zm0-3h10v2H7z"/></svg>';
    btn.style.cssText='position:fixed;bottom:20px;right:20px;z-index:99999;width:44px;height:44px;border-radius:50%;background:linear-gradient(135deg,#0066cc,#004499);display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 4px 16px rgba(0,102,204,0.4);transition:transform 0.2s;';
    btn.onmouseover=function(){{this.style.transform='scale(1.1)'}};
    btn.onmouseout=function(){{this.style.transform='scale(1)'}};

    var frame=document.createElement('iframe');
    frame.id='alpha-chat-frame';
    frame.src='{base_url}/widget';
    var isMobile=window.innerWidth<=480;
    frame.style.cssText=isMobile?'position:fixed;bottom:0;right:0;left:0;width:100%;height:85vh;border:none;border-radius:16px 16px 0 0;z-index:100000;display:none;box-shadow:0 -4px 32px rgba(0,0,0,0.3);':'position:fixed;bottom:24px;right:24px;width:400px;height:520px;border:none;border-radius:16px;z-index:100000;display:none;box-shadow:0 8px 32px rgba(0,0,0,0.25);';

    var isOpen=false;
    btn.onclick=function(){{
        isOpen=true;
        frame.style.display='block';
        btn.style.display='none';
    }};

    window.addEventListener('message',function(e){{
        if(e.data==='alpha-chat-close'){{
            isOpen=false;
            frame.style.display='none';
            btn.style.display='flex';
        }}
    }});

    document.body.appendChild(btn);
    document.body.appendChild(frame);
    }})();"""

    return web.Response(text=js, content_type="application/javascript")


async def handle_api_analytics(request: web.Request) -> web.Response:
    """API endpoint для аналитики."""
    days = int(request.query.get('days', '30'))
    data = get_full_analytics(days)
    return web.json_response(data)


async def handle_health(request: web.Request) -> web.Response:
    return web.json_response({"status": "ok"})


async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    port = int(os.getenv("PORT", "8090"))

    # ─── Инициализация ───
    init_conv_db()
    init_analytics_db()

    if not load_index():
        logger.warning("RAG index not loaded — bot will work without document search")

    # ─── Telegram bot ───
    app_tg = Application.builder().token(token).build()
    app_tg.add_handler(CommandHandler("start", cmd_start))
    app_tg.add_handler(CommandHandler("reset", cmd_reset))
    app_tg.add_handler(CommandHandler("stats", cmd_stats_handler))
    app_tg.add_handler(CommandHandler("analytics", cmd_analytics_handler))
    app_tg.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # ─── Web server ───
    app_web = web.Application()
    app_web.router.add_post("/api/chat", handle_api_chat)
    app_web.router.add_get("/api/analytics", handle_api_analytics)
    app_web.router.add_get("/widget", handle_widget)
    app_web.router.add_get("/widget.js", handle_widget_js)
    app_web.router.add_get("/health", handle_health)

    # CORS
    from aiohttp.web_middlewares import middleware

    @middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            resp = web.Response()
        else:
            resp = await handler(request)
        resp.headers["Access-Control-Allow-Origin"] = "*"
        resp.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        resp.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return resp

    app_web.middlewares.append(cors_middleware)

    runner = web.AppRunner(app_web)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port, reuse_address=True)
    await site.start()

    logger.info(f"Web server started on port {port}")
    logger.info(f"Widget: http://localhost:{port}/widget")

    # Запускаем Telegram polling
    await app_tg.initialize()
    await app_tg.start()
    await app_tg.updater.start_polling(drop_pending_updates=True)

    logger.info("Alpha-Bot started (Phase 2: contextual memory)")

    try:
        while True:
            await asyncio.sleep(3600)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down...")
        await app_tg.updater.stop()
        await app_tg.stop()
        await app_tg.shutdown()
        await runner.cleanup()


if __name__ == "__main__":
    asyncio.run(main())
