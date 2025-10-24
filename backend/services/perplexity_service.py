"""
Klient do obsługi API Perplexity (Agent X).
"""

def search_perplexity(query: str) -> str:
    """
    Wykonuje zapytanie do Perplexity API.
    """
    print(f"--- WYWOŁANIE (MOCK) PERPLEXITY API ---")
    print(f"ZAPYTANIE: {query}")
    
    # Symulacja odpowiedzi
    return "To jest przykładowe podsumowanie z Perplexity, znalezione w sieci."