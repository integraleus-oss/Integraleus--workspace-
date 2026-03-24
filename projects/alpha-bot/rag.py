"""RAG v2 — гибридный поиск (semantic + BM25) через ChromaDB + реранкинг."""

import os
import json
import glob
import logging
import re
import numpy as np
import aiohttp
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text")

# Пути (legacy numpy — для обратной совместимости)
CHUNKS_FILE = "/opt/alpha-bot-data/chunks.json"
EMBEDDINGS_FILE = "/opt/alpha-bot-data/embeddings.npy"

# ChromaDB
CHROMA_DIR = "/opt/alpha-bot-data/chroma_db"

# Глобальные объекты
_chroma_collection = None
_bm25_index = None
_bm25_chunks = []  # Чанки для BM25 поиска (text + metadata)

# ── Модуль → метаданные ──
MODULE_PATTERNS = {
    "Alpha.Server": ["alpha.server", "alpha server", "сервер сигналов", "ввод-вывод", "кластер", "резервирование"],
    "Alpha.HMI": ["alpha.hmi", "alpha hmi", "мнемосхем", "визуализат", "hmi", "дизайнер"],
    "Alpha.HMI.WebViewer": ["webviewer", "web viewer", "веб-интерфейс", "web-клиент"],
    "Alpha.Alarms": ["alpha.alarms", "тревог", "квитирован", "событи"],
    "Alpha.Trends": ["alpha.trends", "тренд", "графи", "историческ"],
    "Alpha.Historian": ["alpha.historian", "historian", "архивирован", "архив"],
    "Alpha.Reports": ["alpha.reports", "отчёт", "отчет", "report"],
    "Alpha.DevStudio": ["alpha.devstudio", "devstudio", "ide", "проектирован", "компиляц"],
    "Alpha.Om": ["alpha.om", "alpha om", "формул", "процедур"],
    "Alpha.Security": ["alpha.security", "безопасност", "ldap", "аудит", "доступ"],
    "Alpha.Diagnostics": ["alpha.diagnostics", "диагностик", "auditreport"],
    "Alpha.Tools": ["alpha.tools", "opcexplorer", "eventlogviewer"],
    "Alpha.Imitator": ["alpha.imitator", "имитатор"],
    "Alpha.Domain": ["alpha.domain", "домен"],
    "Alpha.AccessPoint": ["alpha.accesspoint", "accesspoint", "агрегац"],
    "Alpha.RMap": ["alpha.rmap", "rmap", "sql-интерфейс"],
    "Licensing": ["лицензи", "тариф", "sku", "артикул", "one+", "alpha.scada", "alpha.platform"],
    "PLC": ["плк", "plc", "контроллер", "iec 61131", "мэк", "codesys", "овен", "элеси"],
}


def _detect_module(text: str) -> str:
    """Определяет модуль по содержимому чанка."""
    text_lower = text.lower()
    scores = {}
    for module, keywords in MODULE_PATTERNS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > 0:
            scores[module] = score
    if scores:
        return max(scores, key=scores.get)
    return "General"


def _detect_section(text: str) -> str:
    """Определяет раздел документации по первой строке."""
    first_line = text.strip().split("\n")[0].strip()
    # Убираем markdown заголовки
    first_line = re.sub(r'^#{1,4}\s*', '', first_line)
    if len(first_line) > 80:
        first_line = first_line[:80]
    return first_line or "Unknown"


def chunk_text(text: str, source: str, chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """Разбивает текст на чанки с перекрытием и метаданными."""
    chunks = []
    paragraphs = text.split("\n\n")

    current_chunk = ""
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        if len(current_chunk) + len(para) > chunk_size and current_chunk:
            module = _detect_module(current_chunk)
            section = _detect_section(current_chunk)
            chunks.append({
                "text": current_chunk.strip(),
                "source": source,
                "module": module,
                "section": section,
            })
            current_chunk = current_chunk[-overlap:] + "\n\n" + para
        else:
            current_chunk += "\n\n" + para if current_chunk else para

    if current_chunk.strip():
        module = _detect_module(current_chunk)
        section = _detect_section(current_chunk)
        chunks.append({
            "text": current_chunk.strip(),
            "source": source,
            "module": module,
            "section": section,
        })

    return chunks


def load_and_chunk_docs(docs_dir: str) -> list[dict]:
    """Загружает все markdown-файлы и разбивает на чанки."""
    all_chunks = []

    for filepath in glob.glob(os.path.join(docs_dir, "*.md")):
        filename = os.path.basename(filepath)
        if filename == "INDEX.md":
            continue

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                text = f.read()

            if len(text) > 150_000:
                logger.info(f"Skipping large file: {filename} ({len(text)} bytes)")
                continue

            chunks = chunk_text(text, source=filename)
            all_chunks.extend(chunks)
            logger.info(f"Chunked {filename}: {len(chunks)} chunks")
        except Exception as e:
            logger.error(f"Error reading {filepath}: {e}")

    return all_chunks


# ── Embedding helpers ──

def get_embedding_sync(text: str) -> list[float]:
    """Синхронный запрос эмбеддинга через Ollama."""
    import requests
    resp = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()["embeddings"][0]


async def get_embedding_async(text: str) -> list[float]:
    """Асинхронный запрос эмбеддинга через Ollama."""
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f"{OLLAMA_URL}/api/embed",
            json={"model": EMBED_MODEL, "input": text},
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            data = await resp.json()
            return data["embeddings"][0]


# ── ChromaDB ──

def _get_chroma_collection():
    """Возвращает (или создаёт) коллекцию ChromaDB."""
    global _chroma_collection
    if _chroma_collection is not None:
        return _chroma_collection

    import chromadb

    client = chromadb.PersistentClient(path=CHROMA_DIR)
    _chroma_collection = client.get_or_create_collection(
        name="alpha_docs",
        metadata={"hnsw:space": "cosine"},
    )
    return _chroma_collection


def build_index(docs_dir: str) -> None:
    """Строит ChromaDB индекс + BM25 из документов."""
    logger.info(f"Building RAG index from {docs_dir}...")

    chunks = load_and_chunk_docs(docs_dir)
    logger.info(f"Total chunks: {len(chunks)}")

    collection = _get_chroma_collection()

    # Очищаем старую коллекцию
    existing = collection.count()
    if existing > 0:
        logger.info(f"Clearing existing collection ({existing} docs)...")
        all_ids = collection.get()["ids"]
        if all_ids:
            # Удаляем батчами по 5000
            for i in range(0, len(all_ids), 5000):
                collection.delete(ids=all_ids[i:i+5000])

    # Индексируем батчами
    batch_size = 50
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i+batch_size]

        ids = [f"chunk_{i+j}" for j in range(len(batch))]
        documents = [c["text"][:2000] for c in batch]
        metadatas = [{"source": c["source"], "module": c["module"], "section": c["section"]} for c in batch]

        # Получаем эмбеддинги
        embeddings = []
        for c in batch:
            try:
                emb = get_embedding_sync(c["text"][:2000])
                embeddings.append(emb)
            except Exception as e:
                logger.error(f"Error embedding chunk: {e}")
                embeddings.append([0.0] * 768)

        collection.add(
            ids=ids,
            documents=documents,
            embeddings=embeddings,
            metadatas=metadatas,
        )

        logger.info(f"Indexed {min(i + batch_size, len(chunks))}/{len(chunks)}")

    # Сохраняем чанки для BM25 (JSON, для совместимости)
    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False, indent=2)

    logger.info(f"Index built: {len(chunks)} chunks in ChromaDB + JSON")


# ── BM25 index ──

def _tokenize(text: str) -> list[str]:
    """Простая токенизация для BM25."""
    text = text.lower()
    text = re.sub(r'[^\w\s]', ' ', text)
    return [w for w in text.split() if len(w) > 2]


def _build_bm25():
    """Строит BM25 индекс из чанков."""
    global _bm25_index, _bm25_chunks

    if not os.path.exists(CHUNKS_FILE):
        logger.warning("chunks.json not found, BM25 not available")
        return False

    with open(CHUNKS_FILE, "r", encoding="utf-8") as f:
        _bm25_chunks = json.load(f)

    tokenized = [_tokenize(c["text"]) for c in _bm25_chunks]
    _bm25_index = BM25Okapi(tokenized)
    logger.info(f"BM25 index built: {len(_bm25_chunks)} chunks")
    return True


# ── Load ──

def load_index() -> bool:
    """Загружает ChromaDB + BM25 индексы."""
    global _chroma_collection

    try:
        collection = _get_chroma_collection()
        count = collection.count()
        if count == 0:
            logger.warning("ChromaDB collection is empty")
            return False
        logger.info(f"ChromaDB loaded: {count} chunks")
    except Exception as e:
        logger.error(f"ChromaDB load error: {e}")
        return False

    _build_bm25()
    return True


# ── Hybrid search ──

async def search(query: str, top_k: int = 5, module_filter: str | None = None) -> list[dict]:
    """Гибридный поиск: ChromaDB (semantic) + BM25 (keyword) → rerank."""
    collection = _get_chroma_collection()
    if collection.count() == 0:
        return []

    # ── 1. Semantic search (ChromaDB) ──
    try:
        query_emb = await get_embedding_async(query)

        chroma_kwargs = {
            "query_embeddings": [query_emb],
            "n_results": top_k * 3,  # Берём больше для реранкинга
        }
        if module_filter:
            chroma_kwargs["where"] = {"module": module_filter}

        results = collection.query(**chroma_kwargs)

        semantic_results = []
        if results and results["documents"]:
            for doc, meta, dist in zip(
                results["documents"][0],
                results["metadatas"][0],
                results["distances"][0],
            ):
                score = 1 - dist  # cosine distance → similarity
                semantic_results.append({
                    "text": doc,
                    "source": meta.get("source", ""),
                    "module": meta.get("module", ""),
                    "section": meta.get("section", ""),
                    "semantic_score": max(0, score),
                })
    except Exception as e:
        logger.error(f"Semantic search error: {e}")
        semantic_results = []

    # ── 2. BM25 keyword search ──
    bm25_results = []
    if _bm25_index and _bm25_chunks:
        try:
            tokens = _tokenize(query)
            if tokens:
                scores = _bm25_index.get_scores(tokens)
                top_indices = np.argsort(scores)[::-1][:top_k * 3]

                for idx in top_indices:
                    if scores[idx] > 0:
                        chunk = _bm25_chunks[idx]
                        bm25_results.append({
                            "text": chunk["text"],
                            "source": chunk.get("source", ""),
                            "module": chunk.get("module", ""),
                            "section": chunk.get("section", ""),
                            "bm25_score": float(scores[idx]),
                        })
        except Exception as e:
            logger.error(f"BM25 search error: {e}")

    # ── 3. Merge + Rerank ──
    merged = _merge_and_rerank(semantic_results, bm25_results, top_k)

    return merged


def _merge_and_rerank(
    semantic: list[dict],
    bm25: list[dict],
    top_k: int,
    semantic_weight: float = 0.6,
    bm25_weight: float = 0.4,
) -> list[dict]:
    """Объединяет результаты semantic и BM25, реранкирует."""
    # Нормализуем BM25 scores (0..1)
    if bm25:
        max_bm25 = max(r.get("bm25_score", 0) for r in bm25)
        if max_bm25 > 0:
            for r in bm25:
                r["bm25_score_norm"] = r.get("bm25_score", 0) / max_bm25
        else:
            for r in bm25:
                r["bm25_score_norm"] = 0

    # Собираем в единую карту по тексту (дедупликация)
    seen = {}
    for r in semantic:
        key = r["text"][:200]  # Ключ — начало текста
        seen[key] = {
            "text": r["text"],
            "source": r["source"],
            "module": r.get("module", ""),
            "section": r.get("section", ""),
            "semantic_score": r.get("semantic_score", 0),
            "bm25_score_norm": 0,
        }

    for r in bm25:
        key = r["text"][:200]
        if key in seen:
            # Найден в обоих — бонус!
            seen[key]["bm25_score_norm"] = r.get("bm25_score_norm", 0)
        else:
            seen[key] = {
                "text": r["text"],
                "source": r["source"],
                "module": r.get("module", ""),
                "section": r.get("section", ""),
                "semantic_score": 0,
                "bm25_score_norm": r.get("bm25_score_norm", 0),
            }

    # Итоговый скор
    for key, r in seen.items():
        r["combined_score"] = (
            semantic_weight * r["semantic_score"]
            + bm25_weight * r["bm25_score_norm"]
        )
        # Бонус за совпадение в обоих методах
        if r["semantic_score"] > 0 and r["bm25_score_norm"] > 0:
            r["combined_score"] *= 1.2

    # Сортируем и берём top_k
    ranked = sorted(seen.values(), key=lambda x: x["combined_score"], reverse=True)

    results = []
    for r in ranked[:top_k]:
        if r["combined_score"] > 0.1:
            results.append({
                "text": r["text"],
                "source": r["source"],
                "module": r["module"],
                "section": r["section"],
                "score": round(r["combined_score"], 3),
            })

    return results


# ── Legacy compatibility ──

def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    """Косинусное сходство (legacy, используется в humanlike-agent)."""
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-8))


if __name__ == "__main__":
    """Запуск индексации: python rag.py [docs_dir]"""
    import sys
    logging.basicConfig(level=logging.INFO)

    docs_dir = sys.argv[1] if len(sys.argv) > 1 else "/opt/alpha-bot-data/docs"
    build_index(docs_dir)
    print("Done!")
