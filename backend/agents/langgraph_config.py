import asyncio
import time
from trafilatura import extract

from langgraph.graph import StateGraph, END
from typing import Literal

# Importowanie stanów i promptów (z Fazy 1)
from .states import AgentState
from .prompts import (
    GATEKEEPER_PROMPT,
    WRITER_PROMPTS,
    PERPLEXITY_QUERIES,
    SYNTHESIZER_PROMPTS,
    normalize_category
)

# Importowanie (zamockowanych) serwisów
from ..services import llm_clients, perplexity_service, rag_service

# Placeholder dla sesji DB (powinna być wstrzykiwana)
db_session_mock = None 

# --- DEFINICJE WĘZŁÓW (AGENTÓW) ---

def gatekeeper_node(state: AgentState) -> dict:
    """
    Agent 1: Bramkarz. (Wersja 2.0 - Odporna na błędy)
    Sprawdza duplikaty i filtruje szum (relewantność).
    """
    print("--- WĘZEŁ: Agent 1 (Bramkarz) ---")

    # 1. Sprawdzenie duplikatów
    if rag_service.check_if_url_exists(state.source_url, db_session_mock):
        print(f"WYNIK: Odrzucono (Duplikat): {state.source_url}")
        return {"is_duplicate": True, "is_relevant": False}

    # 2. Sprawdzenie relewantności
    prompt = GATEKEEPER_PROMPT.format(raw_content=state.raw_content)
    response = llm_clients.invoke_fast_model(prompt)

    # --- NOWA, POPRAWIONA LOGIKA ---
    # A. Sprawdź, czy w ogóle mamy błąd z API
    if "Błąd serwera" in response or "BŁĄD KRYTYCZNY" in response:
        print(f"WYNIK: Odrzucono (Błąd LLM): {state.source_url}")
        # Zwracamy błąd i oznaczamy jako nieistotny
        return {"is_relevant": False, "error_message": response}

    # B. Dopiero teraz sprawdzamy treść merytoryczną
    processed_response = response.strip().upper()
    is_relevant = ("TAK" in processed_response) or ("YES" in processed_response)    

    if not is_relevant:
        print(f"WYNIK: Odrzucono (Nieistotny): {state.source_url}")
        return {"is_relevant": False}

    print(f"WYNIK: Zaakceptowano: {state.source_url}")
    # is_duplicate jest już False (sprawdzone na górze)
    return {"is_relevant": True}


def extractor_node(state: AgentState) -> dict:
    """
    Węzeł pomocniczy: Ekstraktor.
    Czyści HTML/content przed przekazaniem do agentów analitycznych.
    """
    print("--- WĘZEŁ: Ekstraktor ---")
    # Używamy trafilatura do wyciągnięcia czystego tekstu z HTML/surowego contentu
    clean_text = extract(state.raw_content, include_comments=False, include_tables=False)
    
    if not clean_text:
        print("OSTRZEŻENIE: Trafilatura nie wyciągnęła tekstu, używam raw_content")
        clean_text = state.raw_content # Fallback
        
    return {"clean_text": clean_text}

def parallel_summarizer_node(state: AgentState) -> dict:
    """
    Agent 2 (Równoległy): Zbieracze.
    Uruchamia Agenta 3 (Writer) i Agenta X (Perplexity) sekwencyjnie.
    """
    print("--- WĘZEŁ: Agent 2 (Zbieracze Równolegli) ---")
    
    # Pobranie odpowiednich promptów/zapytań dla danej kategorii
    category = normalize_category(state.category)
    writer_prompt = WRITER_PROMPTS[category].format(clean_text=state.clean_text)
    perplexity_query = PERPLEXITY_QUERIES[category]

    # Uruchamiamy Writer
    print("ROZPOCZYNAM: Agent 3 (Writer)")
    writer_summary = llm_clients.invoke_fast_model(writer_prompt)
    print("ZAKOŃCZONO: Agent 3 (Writer)")

    # Uruchamiamy Perplexity
    print("ROZPOCZYNAM: Agent X (Perplexity)")
    perplexity_summary = perplexity_service.search_perplexity(perplexity_query)
    print("ZAKOŃCZONO: Agent X (Perplexity)")

    return {
        "writer_summary": writer_summary,
        "perplexity_summary": perplexity_summary
    }

def category_synthesizer_node(state: AgentState) -> dict:
    """
    Agent 3 (Syntezator): Konsoliduje wyniki Writer + Perplexity w raport kategorii.
    """
    print(f"--- WĘZEŁ: Agent 3 (Syntezator Kategorii) dla kategorii: {state.category} ---")
    
    category = normalize_category(state.category)
    prompt = SYNTHESIZER_PROMPTS[category].format(
        writer_summary=state.writer_summary,
        perplexity_summary=state.perplexity_summary
    )
    
    # Używamy mądrego modelu do syntezy
    final_report = llm_clients.invoke_smart_model(prompt)
    
    return {"final_category_report": final_report}

def rag_storage_node(state: AgentState) -> dict:
    """
    Agent 4 (Archiwista RAG):
    Zapisuje finalny raport kategorii do odpowiedniej kolekcji w pgvector.
    """
    print(f"--- WĘZEŁ: Agent 4 (Archiwista RAG) dla kategorii: {state.category} ---")
    
    category = normalize_category(state.category)
    collection_name = rag_service.RAG_COLLECTIONS[category]
    metadata = {
        "source_url": state.source_url,
        "category": state.category,
        "processed_at": time.time()
    }
    
    rag_service.save_report_to_rag(
        report=state.final_category_report,
        metadata=metadata,
        collection_name=collection_name,
        db=db_session_mock
    )
    
    print("WYNIK: Zapisano do RAG.")
    return {}

# TODO: W Fazie 3 połączymy te węzły w graf LangGraph



# ... (tutaj znajdują się wszystkie nasze importy i funkcje agentów 
#      z Fazy 2: gatekeeper_node, extractor_node, itd.)

# --- KROK 1: Definicja Krawędzi Warunkowej ---

def decide_after_gate(state: AgentState) -> Literal["continue", "end"]:
    """
    Router (Krawędź Warunkowa).
    Sprawdza, czy Bramkarz przepuścił dane.
    """
    print("--- WĘZEŁ: Router (Decyzja po Bramkarzu) ---")
    if state.is_relevant and not state.is_duplicate:
        print("WYNIK: Kontynuuj przetwarzanie")
        return "continue"
    else:
        print("WYNIK: Zakończ przepływ (Duplikat lub Nieistotny)")
        return "end"

# --- KROK 2: Budowa i Kompilacja Grafu ---

def create_agent_graph() -> StateGraph:
    """
    Tworzy i kompiluje kompletny graf agentów.
    """
    print("Inicjalizuję graf agentów...")
    
    # Inicjalizujemy graf, podając mu nasz centralny stan
    graph = StateGraph(AgentState)

    # Dodajemy wszystkie nasze funkcje jako węzły do grafu
    graph.add_node("bramkarz", gatekeeper_node)
    graph.add_node("ekstraktor", extractor_node)
    graph.add_node("zbieracze", parallel_summarizer_node)
    graph.add_node("syntezator", category_synthesizer_node)
    graph.add_node("archiwista_rag", rag_storage_node)

    # --- Definiujemy przepływ (krawędzie) ---

    # 1. Zaczynamy od Bramkarza
    graph.set_entry_point("bramkarz")

    # 2. Dodajemy krawędź warunkową (feedback mentora)
    graph.add_conditional_edges(
        "bramkarz",
        decide_after_gate,
        {
            "continue": "ekstraktor",  # Jeśli relevant, idź do ekstraktora
            "end": END                  # Jeśli nie, zakończ
        }
    )

    # 3. Definiujemy resztę przepływu liniowo
    graph.add_edge("ekstraktor", "zbieracze")
    graph.add_edge("zbieracze", "syntezator")
    graph.add_edge("syntezator", "archiwista_rag")
    
    # 4. Ostatni węzeł łączy się z końcem
    graph.add_edge("archiwista_rag", END)

    # 5. Kompilujemy graf
    print("Kompilacja grafu zakończona.")
    compiled_graph = graph.compile()
    
    return compiled_graph

# Tworzymy jedną, globalną instancję naszego skompilowanego grafu
# Aplikacja FastAPI będzie ją importować i używać.
agent_graph_app = create_agent_graph()