import os
import json
import uuid
from typing import List, Dict, Tuple

import numpy as np
import faiss
import requests

from backend.services.config import settings  # zakładam że masz Settings() z env_file

# Ścieżki wyjściowe (artefakty po budowie indeksu)
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
METADATA_PATH    = os.path.join(os.path.dirname(__file__), "metadata.json")

# Tymczasowe wejście (mock); docelowo to pójdzie z waszej bazy/S3
MOCK_INPUT_PATH  = os.path.join(os.path.dirname(__file__), "mock_input.json")

# Nazwa modelu do embeddingów w Scaleway
EMBED_MODEL_NAME = "bge-multilingual-gemma2"


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> List[str]:
    """
    Dzieli dłuższy tekst na fragmenty ~chunk_size znaków
    z nakładaniem overlap (żeby nie urywać kontekstu między chunkami).
    """
    chunks = []
    start = 0
    n = len(text)

    while start < n:
        end = min(start + chunk_size, n)
        chunk = text[start:end]
        chunks.append(chunk)
        # przesuwamy się do przodu o chunk_size-overlap
        start = end - overlap
        if start < 0:
            start = 0

    return chunks


def get_embedding_from_scaleway(texts: List[str], batch_size: int = 8) -> np.ndarray:
    """
    Wysyła paczki tekstów do Scaleway Embeddings API i zwraca macierz numpy shape (N, dim).
    Przetwarza w mniejszych batch'ach aby nie przekroczyć limitów pamięci.
    """
    if not texts:
        return np.array([])

    api_key = settings.scaleway_api_key
    embeddings_url = settings.SCALEWAY_EMBEDDINGS_URL

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    all_vectors = []
    
    # Przetwarzaj w mniejszych batch'ach
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i:i + batch_size]
        print(f"[RAG] Przetwarzanie batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(batch_texts)} tekstów)...")
        
        payload = {
            "model": EMBED_MODEL_NAME,
            "input": batch_texts
        }

        try:
            response = requests.post(embeddings_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            data = response.json()

            # Zakładamy odpowiedź w stylu:
            # {
            #   "data": [
            #       { "embedding": [0.123, 0.987, ...], "index": 0 },
            #       { "embedding": [ ... ], "index": 1 }
            #   ]
            # }

            for item in data["data"]:
                vec = np.array(item["embedding"], dtype="float32")
                all_vectors.append(vec)
        except Exception as e:
            print(f"[RAG] Błąd podczas przetwarzania batch {i//batch_size + 1}: {e}")
            raise

    return np.vstack(all_vectors)  # shape (N, dim)


def build_index(
    docs: List[Dict],
    index_path: str = FAISS_INDEX_PATH,
    meta_path: str = METADATA_PATH,
    chunk_size: int = 500,
    overlap: int = 100
) -> Tuple[faiss.Index, List[Dict]]:
    """
    Główna funkcja:
    - bierze listę dokumentów w formacie:
        {
          "url": "...",
          "operator": "Orange",
          "timestamp": "2025-10-25T10:32:00Z",
          "text": "oczyszczony tekst..."
        }
    - chunkuje,
    - robi embeddingi,
    - buduje FAISS index (cosine),
    - zapisuje index + metadata do plików.
    - zwraca (index, metadata_list) w pamięci.
    """

    metadata_entries: List[Dict] = []
    vectors_all: List[np.ndarray] = []

    vector_id_counter = 0

    # --- 1. Przygotuj listę wszystkich chunków do embedowania
    batch_texts = []
    batch_meta  = []

    print(f"[RAG] Przetwarzanie {len(docs)} dokumentów...")
    
    for doc in docs:
        chunks = chunk_text(doc["text"], chunk_size=chunk_size, overlap=overlap)
        for ch in chunks:
            batch_texts.append(ch)
            batch_meta.append({
                "url": doc["url"],
                "operator": doc["operator"],
                "timestamp": doc["timestamp"],
                "chunk_text": ch,
                # dodatkowo przyda się unikalne ID chunka
                "chunk_uuid": str(uuid.uuid4())
            })

    print(f"[RAG] Utworzono {len(batch_texts)} chunków z {len(docs)} dokumentów")
    
    # --- 2. Wywołaj embeddings w paczce
    # (jeśli chcesz batchować w kawałkach np. po 16, 32, możesz tu dodać pętle)
    print(f"[RAG] Rozpoczynam tworzenie embeddingów...")
    embeddings = get_embedding_from_scaleway(batch_texts)
    # embeddings: np.ndarray shape (N, dim), float32

    # --- 3. Zbuduj strukturę metadanych + wektory
    # przypisz każdemu wektorowi własne vector_id
    vectors_np_list = []
    for i, emb_vec in enumerate(embeddings):
        entry = {
            "vector_id": vector_id_counter,
            "url": batch_meta[i]["url"],
            "operator": batch_meta[i]["operator"],
            "timestamp": batch_meta[i]["timestamp"],
            "chunk_text": batch_meta[i]["chunk_text"],
            "chunk_uuid": batch_meta[i]["chunk_uuid"]
        }
        metadata_entries.append(entry)
        vectors_np_list.append(emb_vec.reshape(1, -1))
        vector_id_counter += 1

    # sklej w jeden duży array
    vectors_np = np.vstack(vectors_np_list).astype("float32")

    # --- 4. Normalizacja L2 żeby móc użyć Inner Product jako cosine similarity
    faiss.normalize_L2(vectors_np)
    dim = vectors_np.shape[1]

    # --- 5. FAISS index (płaski IP - szybki i wystarczający na start)
    index = faiss.IndexFlatIP(dim)
    index.add(vectors_np)

    # --- 6. Zapis artefaktów
    faiss.write_index(index, index_path)

    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata_entries, f, ensure_ascii=False, indent=2)

    print(f"[RAG] Zapisano indeks FAISS ({vectors_np.shape[0]} wektorów) → {index_path}")
    print(f"[RAG] Zapisano metadane ({len(metadata_entries)} wpisów) → {meta_path}")

    return index, metadata_entries


if __name__ == "__main__":
    # 1. Wczytujemy mock_input.json (tymczasowo pracujesz na mocku,
    #    docelowo koledzy zamiast tego dadzą Ci realne artykuły z S3/bazy)
    with open(MOCK_INPUT_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)

    # 2. Budujemy indeks
    build_index(docs)