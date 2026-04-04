"""Облегчённая пересборка RAG-индекса. Обрабатывает файлы по одному, сохраняет после каждого."""
import os, sys, json, time, gc
import numpy as np
import requests

sys.path.insert(0, "/opt/alpha-bot")
from rag import chunk_text

DOCS_DIR = "/opt/alpha-bot-data/docs"
CHUNKS_FILE = "/opt/alpha-bot-data/chunks.json"
EMBEDDINGS_FILE = "/opt/alpha-bot-data/embeddings.npy"
OLLAMA_URL = "http://127.0.0.1:11434"
EMBED_MODEL = "nomic-embed-text"

def get_embedding(text: str) -> list[float]:
    """Синхронный запрос к Ollama."""
    resp = requests.post(f"{OLLAMA_URL}/api/embed",
                         json={"model": EMBED_MODEL, "input": text[:2000]},
                         timeout=10)
    data = resp.json()
    embs = data.get("embeddings", [])
    if embs and embs[0]:
        return embs[0]
    return [0.0] * 768

def main():
    # Собираем файлы, сортируем по размеру (маленькие первыми)
    files = []
    for f in sorted(os.listdir(DOCS_DIR)):
        if f.endswith(".md") and f != "INDEX.md":
            path = os.path.join(DOCS_DIR, f)
            files.append((os.path.getsize(path), f, path))
    files.sort()  # маленькие первыми

    all_chunks = []
    all_embeddings = []

    for size, filename, filepath in files:
        with open(filepath, "r", encoding="utf-8") as fh:
            text = fh.read()

        chunks = chunk_text(text, source=filename)
        print(f"{filename}: {len(chunks)} chunks ({size//1024}KB)", flush=True)

        for i, chunk in enumerate(chunks):
            try:
                emb = get_embedding(chunk["text"])
                all_chunks.append(chunk)
                all_embeddings.append(emb)
                time.sleep(0.1)  # Rate limiting для ollama
            except Exception as e:
                print(f"  Error chunk {i}: {e}")
                all_chunks.append(chunk)
                all_embeddings.append([0.0] * 768)

            if (i + 1) % 50 == 0:
                print(f"  {i+1}/{len(chunks)}", flush=True)

        # Сохраняем после каждого файла
        with open(CHUNKS_FILE, "w", encoding="utf-8") as fh:
            json.dump(all_chunks, fh, ensure_ascii=False)
        np.save(EMBEDDINGS_FILE, np.array(all_embeddings, dtype=np.float32))
        print(f"  Saved. Total: {len(all_chunks)} chunks, match={len(all_chunks)==len(all_embeddings)}", flush=True)

        # Освобождаем память
        del text, chunks
        gc.collect()

    print(f"\nDone! {len(all_chunks)} chunks, {len(all_embeddings)} embeddings", flush=True)

if __name__ == "__main__":
    main()
