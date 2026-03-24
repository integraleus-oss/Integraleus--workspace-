#!/usr/bin/env python3
"""
RAG Pipeline — локальная база знаний с поиском по документам.
Используется: Ollama nomic-embed-text + FAISS + PyMuPDF.

Команды:
    python3 rag.py add <file_or_dir>     — добавить PDF/TXT/MD файл(ы)
    python3 rag.py add-url <url>          — добавить веб-страницу
    python3 rag.py add-youtube <url>      — добавить YouTube (субтитры)
    python3 rag.py search <query> [--top N] — поиск по базе
    python3 rag.py ask <question> [--top N] — поиск + форматированный ответ
    python3 rag.py list                   — список документов в базе
    python3 rag.py stats                  — статистика базы
    python3 rag.py remove <source_name>   — удалить документ из базы
"""

import argparse
import json
import hashlib
import os
import sys
import subprocess
import textwrap
import time
from pathlib import Path
from typing import Optional

import numpy as np
import faiss
import fitz  # PyMuPDF

# --- Config ---
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
INDEX_DIR = BASE_DIR / "index"
CHUNKS_FILE = INDEX_DIR / "chunks.json"
FAISS_FILE = INDEX_DIR / "faiss.index"
META_FILE = INDEX_DIR / "meta.json"

OLLAMA_MODEL = "nomic-embed-text"
EMBED_DIM = 768
CHUNK_SIZE = 1000  # символов
CHUNK_OVERLAP = 200

# --- Embedding via Ollama ---
def get_embedding(text: str) -> np.ndarray:
    """Получить эмбеддинг текста через Ollama."""
    import urllib.request
    data = json.dumps({"model": OLLAMA_MODEL, "prompt": text}).encode()
    req = urllib.request.Request(
        "http://localhost:11434/api/embeddings",
        data=data,
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        result = json.loads(resp.read())
    return np.array(result["embedding"], dtype=np.float32)


def get_embeddings_batch(texts: list[str], batch_size: int = 10) -> np.ndarray:
    """Получить эмбеддинги пакетами."""
    all_embs = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        for t in batch:
            emb = get_embedding(t)
            all_embs.append(emb)
        if i + batch_size < len(texts):
            sys.stdout.write(f"\r  Эмбеддинги: {min(i + batch_size, len(texts))}/{len(texts)}")
            sys.stdout.flush()
    if len(texts) > batch_size:
        print()
    return np.vstack(all_embs)


# --- Text extraction ---
def extract_pdf(path: str) -> str:
    """Извлечь текст из PDF."""
    doc = fitz.open(path)
    text = ""
    for page in doc:
        text += page.get_text() + "\n"
    doc.close()
    return text


def extract_text(path: str) -> str:
    """Извлечь текст из файла (PDF, TXT, MD)."""
    ext = Path(path).suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    elif ext in (".txt", ".md", ".markdown", ".rst"):
        return Path(path).read_text(encoding="utf-8", errors="ignore")
    else:
        # Попробовать как текст
        try:
            return Path(path).read_text(encoding="utf-8", errors="ignore")
        except Exception:
            print(f"  ⚠ Не могу прочитать {path}")
            return ""


def extract_url(url: str) -> str:
    """Извлечь текст с веб-страницы."""
    try:
        import urllib.request
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            html = resp.read().decode("utf-8", errors="ignore")
        # Простая очистка от тегов
        import re
        text = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL)
        text = re.sub(r'<style[^>]*>.*?</style>', '', text, flags=re.DOTALL)
        text = re.sub(r'<[^>]+>', ' ', text)
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    except Exception as e:
        print(f"  ⚠ Ошибка загрузки URL: {e}")
        return ""


def extract_youtube(url: str) -> str:
    """Извлечь субтитры YouTube через yt-dlp."""
    try:
        result = subprocess.run(
            ["yt-dlp", "--write-auto-sub", "--sub-lang", "ru,en",
             "--skip-download", "--sub-format", "vtt",
             "-o", "/tmp/yt_sub_%(id)s", url],
            capture_output=True, text=True, timeout=60,
        )
        # Найти файл субтитров
        import glob
        vtt_files = glob.glob("/tmp/yt_sub_*.vtt")
        if not vtt_files:
            # Попробовать json субтитры
            result2 = subprocess.run(
                ["yt-dlp", "--write-auto-sub", "--sub-lang", "ru,en",
                 "--skip-download", "--sub-format", "json3",
                 "-o", "/tmp/yt_sub_%(id)s", url],
                capture_output=True, text=True, timeout=60,
            )
            vtt_files = glob.glob("/tmp/yt_sub_*.json3")

        if vtt_files:
            text = Path(vtt_files[0]).read_text(errors="ignore")
            # Очистить VTT от таймкодов
            import re
            text = re.sub(r'\d{2}:\d{2}:\d{2}[\.,]\d{3}\s*-->\s*\d{2}:\d{2}:\d{2}[\.,]\d{3}', '', text)
            text = re.sub(r'<[^>]+>', '', text)
            text = re.sub(r'WEBVTT.*?\n', '', text)
            text = re.sub(r'\n{2,}', '\n', text).strip()
            # Удалить дублирующиеся строки (auto-sub повторяет)
            lines = text.split('\n')
            seen = set()
            unique = []
            for line in lines:
                clean = line.strip()
                if clean and clean not in seen:
                    seen.add(clean)
                    unique.append(clean)
            # Cleanup tmp
            for f in glob.glob("/tmp/yt_sub_*"):
                os.remove(f)
            return ' '.join(unique)
        else:
            print("  ⚠ Субтитры не найдены")
            return ""
    except Exception as e:
        print(f"  ⚠ Ошибка yt-dlp: {e}")
        return ""


# --- Chunking ---
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Разбить текст на чанки с перекрытием."""
    if not text.strip():
        return []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        start += chunk_size - overlap
    return chunks


# --- Index management ---
def load_index() -> tuple[list[dict], Optional[faiss.Index], dict]:
    """Загрузить существующий индекс."""
    chunks = []
    index = None
    meta = {"total_chunks": 0, "sources": {}}

    if CHUNKS_FILE.exists():
        chunks = json.loads(CHUNKS_FILE.read_text())
    if FAISS_FILE.exists():
        index = faiss.read_index(str(FAISS_FILE))
    if META_FILE.exists():
        meta = json.loads(META_FILE.read_text())

    return chunks, index, meta


def save_index(chunks: list[dict], index: faiss.Index, meta: dict):
    """Сохранить индекс."""
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    CHUNKS_FILE.write_text(json.dumps(chunks, ensure_ascii=False, indent=2))
    faiss.write_index(index, str(FAISS_FILE))
    META_FILE.write_text(json.dumps(meta, ensure_ascii=False, indent=2))


def add_document(source_name: str, text: str, source_type: str = "file"):
    """Добавить документ в индекс."""
    chunks_data, index, meta = load_index()

    # Проверить дубликат
    if source_name in meta.get("sources", {}):
        print(f"  ⚠ '{source_name}' уже в базе. Используйте remove + add для обновления.")
        return

    # Чанкинг
    text_chunks = chunk_text(text)
    if not text_chunks:
        print(f"  ⚠ Пустой текст, пропускаю.")
        return

    print(f"  📄 {len(text_chunks)} чанков из '{source_name}'")

    # Эмбеддинги
    embeddings = get_embeddings_batch(text_chunks)

    # Добавить в FAISS
    if index is None:
        index = faiss.IndexFlatIP(EMBED_DIM)  # Inner Product (cosine на нормализованных)

    # Нормализация для cosine similarity
    faiss.normalize_L2(embeddings)
    index.add(embeddings)

    # Метаданные чанков
    start_id = len(chunks_data)
    for i, chunk in enumerate(text_chunks):
        chunks_data.append({
            "id": start_id + i,
            "source": source_name,
            "source_type": source_type,
            "text": chunk,
            "chunk_idx": i,
        })

    # Обновить мета
    meta["total_chunks"] = len(chunks_data)
    meta.setdefault("sources", {})[source_name] = {
        "type": source_type,
        "chunks": len(text_chunks),
        "chars": len(text),
        "added": time.strftime("%Y-%m-%d %H:%M"),
    }

    save_index(chunks_data, index, meta)
    print(f"  ✅ Добавлено: {len(text_chunks)} чанков, всего в базе: {len(chunks_data)}")


def search(query: str, top_k: int = 5) -> list[dict]:
    """Поиск по базе."""
    chunks_data, index, meta = load_index()
    if index is None or not chunks_data:
        print("  ⚠ База пуста. Добавьте документы: rag.py add <файл>")
        return []

    query_emb = get_embedding(query).reshape(1, -1)
    faiss.normalize_L2(query_emb)

    scores, indices = index.search(query_emb, min(top_k, len(chunks_data)))

    results = []
    for score, idx in zip(scores[0], indices[0]):
        if idx < 0:
            continue
        chunk = chunks_data[idx].copy()
        chunk["score"] = float(score)
        results.append(chunk)

    return results


# --- CLI ---
def cmd_add(args):
    """Добавить файл(ы)."""
    path = Path(args.path)
    if path.is_dir():
        files = list(path.glob("**/*.pdf")) + list(path.glob("**/*.txt")) + list(path.glob("**/*.md"))
        print(f"📁 Найдено {len(files)} файлов в {path}")
        for f in sorted(files):
            print(f"\n→ {f.name}")
            text = extract_text(str(f))
            if text.strip():
                add_document(f.name, text, "file")
    elif path.is_file():
        print(f"→ {path.name}")
        text = extract_text(str(path))
        if text.strip():
            add_document(path.name, text, "file")
    else:
        print(f"  ⚠ Файл не найден: {path}")


def cmd_add_url(args):
    """Добавить веб-страницу."""
    url = args.url
    print(f"🌐 Загрузка: {url}")
    text = extract_url(url)
    if text.strip():
        name = url.split("//")[-1][:80].replace("/", "_")
        add_document(name, text, "url")


def cmd_add_youtube(args):
    """Добавить YouTube видео."""
    url = args.url
    print(f"🎬 YouTube: {url}")
    text = extract_youtube(url)
    if text.strip():
        # Получить название
        try:
            result = subprocess.run(
                ["yt-dlp", "--get-title", url],
                capture_output=True, text=True, timeout=30,
            )
            name = result.stdout.strip()[:80] or url.split("v=")[-1][:20]
        except Exception:
            name = url.split("v=")[-1][:20]
        add_document(f"YT: {name}", text, "youtube")


def cmd_search(args):
    """Поиск по базе."""
    results = search(args.query, args.top)
    if not results:
        return
    print(f"\n🔍 Результаты по: «{args.query}»\n")
    for i, r in enumerate(results, 1):
        score_pct = r['score'] * 100
        print(f"{'─' * 60}")
        print(f"  #{i}  [{score_pct:.0f}%]  📄 {r['source']}")
        print(f"  {textwrap.shorten(r['text'], width=300, placeholder='...')}")
    print(f"{'─' * 60}")


def cmd_ask(args):
    """Поиск + форматированный контекст для LLM."""
    results = search(args.query, args.top)
    if not results:
        return

    print(f"\n📋 Контекст для «{args.query}»:\n")
    for i, r in enumerate(results, 1):
        print(f"[Источник: {r['source']} | Релевантность: {r['score']*100:.0f}%]")
        print(r['text'])
        print()


def cmd_list(args):
    """Список документов."""
    _, _, meta = load_index()
    sources = meta.get("sources", {})
    if not sources:
        print("📭 База пуста.")
        return
    print(f"\n📚 Документов в базе: {len(sources)}\n")
    for name, info in sources.items():
        print(f"  • {name}")
        print(f"    Тип: {info['type']} | Чанков: {info['chunks']} | "
              f"Символов: {info['chars']:,} | Добавлен: {info['added']}")


def cmd_stats(args):
    """Статистика."""
    chunks, index, meta = load_index()
    sources = meta.get("sources", {})
    total_chars = sum(s.get("chars", 0) for s in sources.values())
    print(f"\n📊 Статистика RAG")
    print(f"  Документов: {len(sources)}")
    print(f"  Чанков: {meta.get('total_chunks', 0)}")
    print(f"  Символов: {total_chars:,}")
    print(f"  Индекс FAISS: {'✅' if index else '❌'}")
    print(f"  Модель: {OLLAMA_MODEL}")


def cmd_remove(args):
    """Удалить документ из базы."""
    chunks_data, index, meta = load_index()
    source = args.source
    sources = meta.get("sources", {})

    if source not in sources:
        print(f"  ⚠ '{source}' не найден в базе.")
        print(f"  Доступные: {', '.join(sources.keys())}")
        return

    # Удалить чанки и пересобрать индекс
    new_chunks = [c for c in chunks_data if c["source"] != source]
    del sources[source]

    if new_chunks:
        # Пересоздать эмбеддинги
        print(f"  🔄 Пересобираю индекс ({len(new_chunks)} чанков)...")
        texts = [c["text"] for c in new_chunks]
        embeddings = get_embeddings_batch(texts)
        faiss.normalize_L2(embeddings)
        new_index = faiss.IndexFlatIP(EMBED_DIM)
        new_index.add(embeddings)
        # Обновить id
        for i, c in enumerate(new_chunks):
            c["id"] = i
    else:
        new_index = faiss.IndexFlatIP(EMBED_DIM)

    meta["total_chunks"] = len(new_chunks)
    save_index(new_chunks, new_index, meta)
    print(f"  ✅ Удалено: '{source}'")


def main():
    parser = argparse.ArgumentParser(description="RAG Pipeline — локальная база знаний")
    sub = parser.add_subparsers(dest="command")

    p_add = sub.add_parser("add", help="Добавить файл или папку")
    p_add.add_argument("path", help="Путь к файлу или папке")

    p_url = sub.add_parser("add-url", help="Добавить веб-страницу")
    p_url.add_argument("url", help="URL страницы")

    p_yt = sub.add_parser("add-youtube", help="Добавить YouTube видео")
    p_yt.add_argument("url", help="URL видео")

    p_search = sub.add_parser("search", help="Поиск по базе")
    p_search.add_argument("query", help="Поисковый запрос")
    p_search.add_argument("--top", type=int, default=5, help="Количество результатов")

    p_ask = sub.add_parser("ask", help="Поиск + контекст для LLM")
    p_ask.add_argument("query", help="Вопрос")
    p_ask.add_argument("--top", type=int, default=5, help="Количество результатов")

    sub.add_parser("list", help="Список документов")
    sub.add_parser("stats", help="Статистика базы")

    p_rm = sub.add_parser("remove", help="Удалить документ")
    p_rm.add_argument("source", help="Имя документа")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        return

    commands = {
        "add": cmd_add,
        "add-url": cmd_add_url,
        "add-youtube": cmd_add_youtube,
        "search": cmd_search,
        "ask": cmd_ask,
        "list": cmd_list,
        "stats": cmd_stats,
        "remove": cmd_remove,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
