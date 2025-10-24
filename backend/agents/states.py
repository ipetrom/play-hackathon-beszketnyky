from pydantic import BaseModel
from typing import Optional, Dict, Any

class AgentState(BaseModel):
    """
    Centralny, współdzielony stan dla całego przepływu agentów (LangGraph).
    Każdy agent odczytuje ten stan i dodaje/modyfikuje pola.
    """
    
    # === Dane wejściowe (od Scrapera) ===
    # Kategoria decyduje, które prompty zostaną użyte w przepływie.
    category: str  # Oczekiwane wartości: "prawna", "polityczna", "rynkowa"
    source_url: str
    raw_content: str

    # === Dane od Agenta 1 (Bramkarza) ===
    is_duplicate: bool = False
    is_relevant: bool = False

    # === Dane od Agenta 2 (Zbieraczy) ===
    # Wstępne oczyszczenie tekstu (opcjonalne, ale zalecane)
    clean_text: Optional[str] = None 
    # Podsumowanie z naszego LLM (Agent 3 - Writer)
    writer_summary: Optional[str] = None
    # Podsumowanie z zewnętrznego źródła (Agent X - Perplexity)
    perplexity_summary: Optional[str] = None

    # === Dane od Agenta 3 (Syntezatora Kategorii) ===
    # Finalny, połączony raport dla *jednej* kategorii
    final_category_report: Optional[str] = None
    
    # === Dane systemowe ===
    error_message: Optional[str] = None

    class Config:
        # Pozwala na elastyczne zarządzanie typami w LangGraph
        arbitrary_types_allowed = True