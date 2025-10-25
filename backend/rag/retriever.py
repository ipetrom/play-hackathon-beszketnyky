import os
import json
from typing import List, Dict

import numpy as np
import faiss
import requests

from ..utils.config import settings  # wczyta klucze z .env

# Ścieżki do artefaktów wygenerowanych przez index_builder.py
FAISS_INDEX_PATH = os.path.join(os.path.dirname(__file__), "faiss_index.bin")
METADATA_PATH    = os.path.join(os.path.dirname(__file__), "metadata.json")

# Ten sam model embeddingów, którego użyliśmy przy budowie indeksu
EMBED_MODEL_NAME = "bge-multilingual-gemma2"


def _load_index_and_metadata():
    """
    Ładuje zapisany indeks FAISS i metadane z plików.
    Robimy to raz przy imporcie modułu.
    """
    if not os.path.exists(FAISS_INDEX_PATH):
        raise FileNotFoundError(f"Brak pliku FAISS index: {FAISS_INDEX_PATH}")
    if not os.path.exists(METADATA_PATH):
        raise FileNotFoundError(f"Brak pliku metadata.json: {METADATA_PATH}")

    index = faiss.read_index(FAISS_INDEX_PATH)

    with open(METADATA_PATH, "r", encoding="utf-8") as f:
        metadata_entries = json.load(f)

    # żeby szybciej odpytywać po ID, robimy mapę {vector_id: metadata_dict}
    meta_by_id = {int(m["vector_id"]): m for m in metadata_entries}

    return index, meta_by_id


# Ładujemy indeks i metadane przy imporcie modułu.
_FAISS_INDEX, _META_BY_ID = _load_index_and_metadata()


def _embed_query_scaleway(query: str) -> np.ndarray:
    """
    Robi embedding jednego pytania (query) przy użyciu tego samego modelu,
    którego użyliśmy do budowy indeksu.
    Zwraca wektor float32 o kształcie (1, dim), znormalizowany L2.
    """

    api_key = settings.SCALEWAY_API_KEY
    embeddings_url = settings.SCALEWAY_EMBEDDINGS_URL  # musi być w .env i config.py

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": EMBED_MODEL_NAME,
        "input": [query]
    }

    response = requests.post(embeddings_url, headers=headers, json=payload, timeout=30)
    response.raise_for_status()
    data = response.json()

    # Zakładamy, że data["data"][0]["embedding"] istnieje
    vec = np.array(data["data"][0]["embedding"], dtype="float32").reshape(1, -1)

    # normalizacja L2 żeby zgadzała się metryka z FAISS IndexFlatIP
    faiss.normalize_L2(vec)

    return vec


def retrieve_relevant_chunks(question: str, top_k: int = 5) -> List[Dict]:
    """
    Główna funkcja, której będą używać agenci.

    Wejście:
    - question: pytanie biznesowe od managera ("Co Orange robi z pakietami 50 GB?")
    - top_k: ile najlepszych fragmentów zwrócić

    Wyjście:
    Lista dictów:
    [
      {
        "rank": 0,
        "score": 0.92,
        "operator": "Orange",
        "timestamp": "...",
        "url": "https://...",
        "text": "Orange wprowadza pakiet 50GB...",
      },
      ...
    ]

    To jest gotowe do użycia w prompt'cie LLM-a.
    """

    # 1. embedding zapytania
    query_vec = _embed_query_scaleway(question)

    # 2. przeszukiwanie FAISS
    # _FAISS_INDEX to IndexFlatIP znormalizowany na cosine-like similarity
    distances, indices = _FAISS_INDEX.search(query_vec, top_k)

    results = []
    for rank, vector_id in enumerate(indices[0]):
        # UWAGA: FAISS potrafi zwrócić -1 przy braku trafienia, ale w IndexFlatIP raczej nie
        vector_id_int = int(vector_id)
        meta = _META_BY_ID.get(vector_id_int)

        if meta is None:
            # jeżeli z jakiegoś powodu nie znajdziemy metadanych
            continue

        results.append({
            "rank": rank,
            "score": float(distances[0][rank]),  # im wyższe tym bardziej podobne
            "operator": meta.get("operator"),
            "timestamp": meta.get("timestamp"),
            "url": meta.get("url"),
            "text": meta.get("chunk_text"),
            "vector_id": vector_id_int
        })

    return results


if __name__ == "__main__":
    # Szybki manualny test
    question = "Jakie ruchy marketingowe Orange zrobił przy pakietach 50GB?"
    hits = retrieve_relevant_chunks(question, top_k=3)

    print(f"Pytanie: {question}")
    print("Top 3 trafienia:\n")
    for h in hits:
        print("-----")
        print(f"RANK {h['rank']} | SCORE {h['score']:.4f}")
        print(f"OPERATOR: {h['operator']}")
        print(f"TIME    : {h['timestamp']}")
        print(f"URL     : {h['url']}")
        print("TEKST:")
        print(h["text"])
        print()
