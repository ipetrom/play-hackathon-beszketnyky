import json
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import List

# Importowanie naszego skompilowanego grafu
from .agents.langgraph_config import agent_graph_app

# Importowanie naszych (zamockowanych) serwisów i promptów
from .services import rag_service, llm_clients
from .agents.prompts import FINAL_TIPS_ALERTS_PROMPT, PERPLEXITY_QUERIES

# Inicjalizacja aplikacji FastAPI
app = FastAPI(
    title="Project Hyperion API",
    description="Backend dla Smart Tracker (Play Hackathon)"
)

# --- Modele Danych (Pydantic) dla API ---

class IngestRequest(BaseModel):
    """
    Co scraper wysyła do naszego API, aby rozpocząć przetwarzanie.
    """
    category: str  # "prawna", "polityczna", "rynkowa"
    source_url: str
    raw_content: str

class AskRequest(BaseModel):
    """
    Co wysyła frontend, aby zadać pytanie chatbotowi RAG.
    """
    category: str  # "prawna", "polityczna", "rynkowa"
    query: str

class AskResponse(BaseModel):
    answer: str
    
class ReportResponse(BaseModel):
    """
    Finalny, skonsolidowany raport dla frontendu.
    """
    alerts: str
    tips: str
    report_prawny: str
    report_polityczny: str
    report_rynkowy: str

# --- Endpointy API ---

@app.post("/api/v1/ingest", status_code=202)
async def ingest_article(request: IngestRequest, background_tasks: BackgroundTasks):
    """
    Endpoint dla Scrapera (Agent 1).
    Przyjmuje dane i uruchamia graf agentów W TLE.
    Natychmiast zwraca 202 Accepted.
    """
    print(f"Otrzymano zlecenie 'ingest' dla kategorii: {request.category}")
    
    # Sprawdzenie, czy kategoria jest poprawna
    if request.category not in rag_service.RAG_COLLECTIONS:
        raise HTTPException(status_code=400, detail="Nieznana kategoria. Użyj 'prawna', 'polityczna' lub 'rynkowa'.")

    # Uruchamiamy graf w tle (kluczowe dla hackathonu!)
    # Scraper nie musi czekać na zakończenie analizy (30+ sekund)
    background_tasks.add_task(
    agent_graph_app.ainvoke, # <--- POPRAWKA
    {
        "category": request.category,
        "source_url": request.source_url,
        "raw_content": request.raw_content
    }
    )       
    
    return {"message": "Zlecenie przyjęte do przetwarzania."}


@app.post("/api/v1/ask", response_model=AskResponse)
async def ask_rag_chatbot(request: AskRequest):
    """
    Endpoint dla Chatbota (Frontend).
    Pyta *konkretną* kolekcję RAG.
    """
    print(f"Otrzymano zapytanie RAG dla kategorii: {request.category}")
    
    # Sprawdzenie, czy kategoria jest poprawna
    if request.category not in rag_service.RAG_COLLECTIONS:
        raise HTTPException(status_code=400, detail="Nieznana kategoria.")
        
    collection_name = rag_service.RAG_COLLECTIONS[request.category]
    
    # Wywołujemy serwis RAG (na razie mock)
    answer = rag_service.query_rag_collection(
        query=request.query,
        collection_name=collection_name
    )
    
    return AskResponse(answer=answer)


@app.get("/api/v1/full_report", response_model=ReportResponse)
async def get_full_report():
    """
    Endpoint dla Głównego Raportu (Frontend).
    Implementuje "Code-Based Report" oraz "Agent 5: Tips + Alerts".
    """
    print("Generuję pełny raport...")
    
    # 1. "Code-Based Report": Zaciągamy podsumowania z każdej kategorii RAG
    print("Krok 1: Zaciągam raporty z RAG...")
    report_prawny = rag_service.query_rag_collection(
        query="Podsumuj dzisiejsze kluczowe zmiany prawne.",
        collection_name=rag_service.RAG_COLLECTIONS["prawna"]
    )
    report_polityczny = rag_service.query_rag_collection(
        query="Podsumuj dzisiejsze kluczowe decyzje polityczne.",
        collection_name=rag_service.RAG_COLLECTIONS["polityczna"]
    )
    report_rynkowy = rag_service.query_rag_collection(
        query="Podsumuj dzisiejsze kluczowe ruchy rynkowe.",
        collection_name=rag_service.RAG_COLLECTIONS["rynkowa"]
    )
    
    # 2. "Agent 5: Tips + Alerts"
    print("Krok 2: Uruchamiam Agenta 5 (Tips/Alerts)...")
    final_prompt = FINAL_TIPS_ALERTS_PROMPT.format(
        report_prawny=report_prawny,
        report_polityczny=report_polityczny,
        report_rynkowy=report_rynkowy
    )
    
    # Wywołujemy mądry model
    analysis_json_string = llm_clients.invoke_smart_model(final_prompt)
    
    try:
        # Nasz mock zwraca string JSON, musimy go sparsować
        analysis = json.loads(analysis_json_string)
        alerts = analysis.get("alerts", "Błąd generowania alertów.")
        tips = analysis.get("tips", "Błąd generowania wskazówek.")
    except json.JSONDecodeError:
        print("BŁĄD: Agent 5 nie zwrócił poprawnego JSONa.")
        alerts = "Błąd serwera podczas generowania alertów."
        tips = "Błąd serwera podczas generowania wskazówek."

    # 3. Zwracamy finalny, połączony raport
    return ReportResponse(
        alerts=alerts,
        tips=tips,
        report_prawny=report_prawny,
        report_polityczny=report_polityczny,
        report_rynkowy=report_rynkowy
    )

@app.get("/")
async def root():
    return {"status": "Project Hyperion API Running"}