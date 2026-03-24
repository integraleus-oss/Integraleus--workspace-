"""RAG клиент для HumanLike Agent — использует индекс alpha-bot."""

import os
import json
import logging
import numpy as np
import aiohttp

logger = logging.getLogger(__name__)

OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"

# Пути к индексу alpha-bot
CHUNKS_FILE = "/opt/alpha-bot/chunks.json"
EMBEDDINGS_FILE = "/opt/alpha-bot/embeddings.npy"

_chunks = []
_embeddings = None


def load_index() -> bool:
    global _chunks, _embeddings
    if not os.path.exists(CHUNKS_FILE) or not os.path.exists(EMBEDDINGS_FILE):
        logger.warning("RAG index not found")
        return False
    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        _chunks = json.load(f)
    _embeddings = np.load(EMBEDDINGS_FILE)
    logger.info(f"RAG index loaded: {len(_chunks)} chunks")
    return True


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


async def search(query: str, top_k: int = 5) -> str:
    """Ищет релевантные чанки и возвращает текст контекста.
    Приоритизирует чанки из специализированных файлов (не только Альфа)."""
    global _chunks, _embeddings
    if not _chunks or _embeddings is None:
        if not load_index():
            return ""

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{OLLAMA_URL}/api/embed",
                json={"model": EMBED_MODEL, "input": query},
                timeout=aiohttp.ClientTimeout(total=5),
            ) as resp:
                data = await resp.json()
                query_emb = np.array(data["embeddings"][0], dtype=np.float32)
    except Exception as e:
        logger.error(f"RAG embed error: {e}")
        return ""

    scores = []
    for i, emb in enumerate(_embeddings):
        sim = cosine_similarity(query_emb, emb)
        # Буст для специализированных файлов (не AlphaPlatform_*)
        source = _chunks[i].get("source", "")
        if not source.startswith("AlphaPlatform_"):
            sim *= 1.15  # +15% для нон-альфа источников
        scores.append((sim, i))

    scores.sort(reverse=True)

    parts = []
    source_count = {}
    for sim, idx in scores[:top_k * 3]:  # берём больше кандидатов
        if sim > 0.30:
            source = _chunks[idx].get("source", "")
            # Не более 2 чанков из одного источника — для разнообразия
            if source_count.get(source, 0) >= 2:
                continue
            source_count[source] = source_count.get(source, 0) + 1
            parts.append(f"[{source}] {_chunks[idx]['text'][:500]}")
            if len(parts) >= top_k:
                break

    if parts:
        context = "\n---\n".join(parts)
        logger.info(f"RAG found {len(parts)} chunks ({len(context)} chars)")
        return context

    return ""
