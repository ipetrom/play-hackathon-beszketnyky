import time

"""
Zunifikowany klient LLM. 
Abstrakcja nad Scaleway (szybki) i OpenAI (mądry).
"""

def invoke_fast_model(prompt: str) -> str:
    """
    Wywołuje szybki model (np. Scaleway/Mistral) do zadań
    takich jak filtrowanie i proste podsumowania.
    """
    print(f"--- WYWOŁANIE (MOCK) SZYBKIEGO LLM ---")
    print(f"PROMPT: {prompt[:100]}...")
    
    # Symulacja filtrowania "TAK/NIE"
    if "Odpowiedz tylko i wyłącznie \"TAK\" lub \"NIE\"" in prompt:
        print("MOCK: Zwracam 'TAK' (Agent Bramkarz)")
        return "TAK"
        
    # Symulacja podsumowania (Agent Writer)
    print("MOCK: Zwracam przykładowe podsumowanie (Agent Writer)")
    return "To jest przykładowe, wygenerowane podsumowanie od Agenta Writer."

def invoke_smart_model(prompt: str) -> str:
    """
    Wywołuje mądry model (np. GPT-4o) do zadań
    wymagających analizy, syntezy i generowania JSON.
    """
    print(f"--- WYWOŁANIE (MOCK) MĄDREGO LLM ---")
    print(f"PROMPT: {prompt[:100]}...")

    # Symulacja Agenta 5 (Tips/Alerts)
    if 'JSON' in prompt and 'alerts' in prompt:
        print("MOCK: Zwracam JSON z alertami i wskazówkami")
        return """
        {
            "alerts": "Krytyczny alert: Konkurencja obniżyła ceny o 20%.",
            "tips": "Sugerowana analiza portfolio cenowego."
        }
        """
    
    # Symulacja Agenta 4 (Syntezator)
    print("MOCK: Zwracam przykładowy raport (Agent Syntezator)")
    return "To jest finalny, zsyntezowany raport kategorii, łączący oba źródła."