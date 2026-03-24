"""LLM клиент для агента."""

import os
import asyncio
import logging
import aiohttp
from config import OPENROUTER_API_KEY, MODEL

logger = logging.getLogger(__name__)

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

FALLBACK_MODELS = [
    "google/gemma-3-12b-it:free",
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openrouter/free",
]


async def ask_llm(system_prompt: str, messages: list[dict], max_tokens: int = 512) -> str | None:
    """Отправляет запрос в LLM. Возвращает None если не нужно отвечать."""
    api_key = OPENROUTER_API_KEY

    all_messages = [{"role": "system", "content": system_prompt}]
    all_messages.extend(messages)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    # Пробуем основную модель, потом fallback
    models_to_try = [MODEL] + FALLBACK_MODELS

    for model in models_to_try:
        payload = {
            "model": model,
            "messages": all_messages,
            "max_tokens": max_tokens,
            "temperature": 0.7,
        }

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    OPENROUTER_URL, headers=headers, json=payload,
                    timeout=aiohttp.ClientTimeout(total=30)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        reply = data["choices"][0]["message"]["content"]

                        # Если LLM решил не отвечать
                        if reply.strip().upper() in ["[SKIP]", "[МОЛЧУ]", "[ПРОПУСК]"]:
                            return None

                        return reply.strip()
                    elif resp.status in (429, 402):
                        await asyncio.sleep(1)
                        continue
                    else:
                        continue
        except Exception as e:
            logger.error(f"LLM error ({model}): {e}")
            continue

    logger.error("All LLM models failed")
    return None
