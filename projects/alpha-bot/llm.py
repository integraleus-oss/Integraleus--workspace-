"""OpenRouter LLM клиент с гибридным RAG v2."""

import os
import json
import asyncio
import logging
import aiohttp
from knowledge_base import SYSTEM_PROMPT
from rag import search as rag_search, MODULE_PATTERNS

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

# Модели с fallback
FREE_MODELS = [
    ("google/gemma-3-12b-it:free", False),              # нет system role
    ("nvidia/nemotron-3-super-120b-a12b:free", True),   # 120B, system role OK
    ("openrouter/free", True),                          # авто-роутинг
]


def _detect_module_filter(query: str) -> str | None:
    """Определяет модуль из запроса для фильтрации поиска."""
    query_lower = query.lower()
    scores = {}
    for module, keywords in MODULE_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in query_lower)
        if score > 0:
            scores[module] = score
    if scores:
        best = max(scores, key=scores.get)
        if scores[best] >= 2:  # Нужно минимум 2 совпадения для фильтрации
            return best
    return None


async def _build_context(user_message: str) -> str:
    """Ищет релевантные куски документации через гибридный RAG."""
    try:
        # Определяем фильтр по модулю
        module_filter = _detect_module_filter(user_message)
        if module_filter:
            logger.info(f"Module filter: {module_filter}")

        # Гибридный поиск (semantic + BM25 + rerank)
        results = await rag_search(user_message, top_k=5, module_filter=module_filter)

        if not results:
            # Без фильтра если с фильтром ничего не нашли
            if module_filter:
                results = await rag_search(user_message, top_k=5, module_filter=None)

        if not results:
            return ""

        context_parts = []
        for r in results:
            source = r.get("source", "")
            module = r.get("module", "")
            section = r.get("section", "")
            score = r.get("score", 0)

            header = f"[Модуль: {module} | Источник: {source} | Раздел: {section} | Релевантность: {score}]"
            context_parts.append(f"{header}\n{r['text']}")

        return "\n\n---\n\n".join(context_parts)
    except Exception as e:
        logger.error(f"RAG search error: {e}")
    return ""


def _build_messages(user_message: str, history: list[dict] | None, supports_system: bool,
                     rag_context: str = "", extra_context: str = "") -> list[dict]:
    """Собирает список сообщений для LLM."""
    messages = []

    full_prompt = SYSTEM_PROMPT
    if extra_context:
        full_prompt += "\n" + extra_context
    if rag_context:
        full_prompt += (
            "\n\n## Дополнительный контекст из документации\n"
            "Используй эту информацию для ответа. ОБЯЗАТЕЛЬНО ссылайся на источник "
            "(модуль, раздел), чтобы пользователь мог найти подробности.\n\n"
            f"{rag_context}"
        )

    if supports_system:
        messages.append({"role": "system", "content": full_prompt})
        if history:
            messages.extend(history[-10:])
        messages.append({"role": "user", "content": user_message})
    else:
        if history:
            messages.extend(history[-10:])
        messages.append({"role": "user", "content": f"<instructions>\n{full_prompt}\n</instructions>\n\nВопрос клиента: {user_message}"})

    return messages


async def ask_llm(user_message: str, history: list[dict] | None = None, extra_context: str = "") -> str:
    """Отправляет вопрос в LLM через OpenRouter с fallback между моделями."""
    api_key = os.getenv("OPENROUTER_API_KEY")
    primary_model = os.getenv("MODEL", "google/gemma-3-12b-it:free")

    models = [(primary_model, True)]
    for m, s in FREE_MODELS:
        if m != primary_model:
            models.append((m, s))

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://specialtechnology.ru",
        "X-Title": "Alpha Platform Consultant",
    }

    # Гибридный RAG
    rag_context = await _build_context(user_message)
    if rag_context:
        logger.info(f"RAG context: {len(rag_context)} chars")

    last_error = ""
    for model, supports_system in models:
        messages = _build_messages(user_message, history, supports_system, rag_context, extra_context)
        payload = {
            "model": model,
            "messages": messages,
            "max_tokens": 2048,
            "temperature": 0.3,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL, headers=headers, json=payload, timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data["choices"][0]["message"]["content"]
                    elif resp.status == 429:
                        last_error = f"429 (rate limit) on {model}"
                        await asyncio.sleep(1)
                        continue
                    elif resp.status == 400:
                        last_error = f"400 on {model}"
                        continue
                    else:
                        last_error = f"HTTP {resp.status} on {model}"
                        continue
        except asyncio.TimeoutError:
            last_error = f"timeout on {model}"
            continue
        except Exception as e:
            last_error = f"error on {model}: {e}"
            continue

    logger.error(f"All models failed. Last error: {last_error}")
    return "Извините, все модели временно недоступны. Попробуйте через минуту."
