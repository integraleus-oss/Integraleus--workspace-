"""Пакетная индексация больших файлов для RAG."""

import os
import sys
import json
import logging
import time
import glob
import numpy as np

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

sys.path.insert(0, "/opt/alpha-bot")
from rag import chunk_text, get_embedding_sync, CHUNKS_FILE, EMBEDDINGS_FILE

DOCS_DIR = "/opt/alpha-bot/docs"


def main():
    # Загружаем существующий индекс
    if os.path.exists(CHUNKS_FILE) and os.path.exists(EMBEDDINGS_FILE):
        with open(CHUNKS_FILE, "r") as f:
            existing_chunks = json.load(f)
        existing_embeddings = np.load(EMBEDDINGS_FILE).tolist()
        # Запоминаем какие файлы уже проиндексированы
        indexed_sources = set(c["source"] for c in existing_chunks)
        logger.info(f"Existing index: {len(existing_chunks)} chunks from {len(indexed_sources)} files")
    else:
        existing_chunks = []
        existing_embeddings = []
        indexed_sources = set()

    # Находим непроиндексированные файлы
    all_files = glob.glob(os.path.join(DOCS_DIR, "**", "*.md"), recursive=True)
    all_files = [f for f in all_files if "/archive/" not in f and not f.endswith("/INDEX.md")]
    new_files = [f for f in all_files if os.path.relpath(f, DOCS_DIR) not in indexed_sources]
    
    if not new_files:
        logger.info("All files already indexed!")
        return

    logger.info(f"New files to index: {len(new_files)}")

    all_chunks = list(existing_chunks)
    all_embeddings = list(existing_embeddings)

    for filepath in sorted(new_files):
        relpath = os.path.relpath(filepath, DOCS_DIR)

        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()

        logger.info(f"Processing {relpath} ({len(text)} bytes)...")
        chunks = chunk_text(text, source=relpath)
        logger.info(f"  → {len(chunks)} chunks")

        for i, chunk in enumerate(chunks):
            try:
                emb = get_embedding_sync(chunk["text"][:2000])
                all_chunks.append(chunk)
                all_embeddings.append(emb)
                time.sleep(0.1)  # Rate limiting для ollama
                
                if (i + 1) % 20 == 0:
                    logger.info(f"  Embedded {i+1}/{len(chunks)}")
                    # Сохраняем промежуточно
                    with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
                        json.dump(all_chunks, f, ensure_ascii=False)
                    np.save(EMBEDDINGS_FILE, np.array(all_embeddings, dtype=np.float32))
                    
            except Exception as e:
                logger.error(f"  Error on chunk {i}: {e}")
                all_embeddings.append([0.0] * 768)
                all_chunks.append(chunk)

        # Сохраняем после каждого файла
        with open(CHUNKS_FILE, "w", encoding="utf-8") as f:
            json.dump(all_chunks, f, ensure_ascii=False)
        np.save(EMBEDDINGS_FILE, np.array(all_embeddings, dtype=np.float32))
        logger.info(f"  Saved. Total: {len(all_chunks)} chunks")

    logger.info(f"Done! Total: {len(all_chunks)} chunks")


if __name__ == "__main__":
    main()
