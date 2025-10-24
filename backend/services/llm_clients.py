# Importujemy nasze nowe, prawdziwe serwisy
from . import scaleway_genai_service

"""
Zunifikowany klient LLM. 
Podmienia mocki na prawdziwe wywołania API.
"""

def invoke_fast_model(prompt: str) -> str:
    """
    Wywołuje szybki model (Scaleway/Mistral) do zadań
    takich jak filtrowanie i proste podsumowania.
    
    Używa prawdziwego API Scaleway.
    """
    # Wywołujemy prawdziwą funkcję z serwisu Scaleway
    return scaleway_genai_service.call_scaleway_api(prompt)


def invoke_smart_model(prompt: str) -> str:
    """
    Wywołuje inteligentny model (Scaleway/Mistral) do bardziej skomplikowanych zadań
    takich jak synteza, analiza i generowanie raportów.
    
    Używa prawdziwego API Scaleway.
    """
    # Dla teraz używamy tego samego modelu co szybki model
    # W przyszłości może być inny model lub konfiguracja
    return scaleway_genai_service.call_scaleway_api(prompt)

