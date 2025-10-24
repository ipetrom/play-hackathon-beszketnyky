"""
Stany dla LangGraph - definicje typów stanów dla różnych agentów
"""

from typing import Dict, List, Any, Optional, Literal
from typing_extensions import TypedDict
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from dataclasses import dataclass

# ====== GŁÓWNY STAN SYSTEMU ======

class SystemState(TypedDict):
    """
    Główny stan systemu zawierający wszystkie informacje
    o konwersacji i kontekście
    """
    # Wiadomości w konwersacji
    messages: List[AnyMessage]
    
    # Identyfikatory
    thread_id: str
    user_id: Optional[str]
    
    # Typ aktualnie używanego agenta
    agent_type: Literal["workforce", "strategist", "supervisor"]
    
    # Kontekst i metadata
    context: Dict[str, Any]
    metadata: Dict[str, Any]
    
    # Stan orkiestracji
    next_agent: Optional[str]
    requires_handoff: bool
    
    # Dane specyficzne dla agentów
    workforce_context: Optional[Dict[str, Any]]
    strategist_context: Optional[Dict[str, Any]]

# ====== STANY SPECYFICZNE DLA AGENTÓW ======

class WorkforceState(TypedDict):
    """
    Stan dla Workforce Agent (Scaleway Mistral)
    Odpowiedzialny za tagowanie, streszczanie, podstawowe operacje
    """
    messages: List[AnyMessage]
    thread_id: str
    
    # Zadanie do wykonania
    task_type: Literal["tagging", "summarization", "basic_qa", "data_processing"]
    
    # Dane wejściowe
    input_data: Any
    
    # Wyniki przetwarzania
    tags: List[str]
    summary: Optional[str]
    processed_data: Optional[Any]
    
    # Kontekst Scaleway
    scaleway_model: str
    scaleway_params: Dict[str, Any]

class StrategistState(TypedDict):
    """
    Stan dla Strategist Agent (OpenAI GPT-4o)
    Odpowiedzialny za analizę ryzyka, Q&A, strategiczne decyzje
    """
    messages: List[AnyMessage]
    thread_id: str
    
    # Typ analizy
    analysis_type: Literal["risk_analysis", "strategic_qa", "decision_support", "complex_reasoning"]
    
    # Dane wejściowe
    context_data: Dict[str, Any]
    user_query: str
    
    # Wyniki analizy
    risk_assessment: Optional[Dict[str, Any]]
    recommendations: List[str]
    confidence_score: Optional[float]
    reasoning_chain: List[str]
    
    # Kontekst OpenAI
    openai_model: str
    temperature: float
    max_tokens: int

class SupervisorState(TypedDict):
    """
    Stan dla Supervisor Agent
    Decyduje o routingu między Workforce i Strategist
    """
    messages: List[AnyMessage]
    thread_id: str
    
    # Analiza intencji
    user_intent: Optional[str]
    complexity_score: float
    requires_reasoning: bool
    requires_data_processing: bool
    
    # Decyzja routingu
    target_agent: Literal["workforce", "strategist"]
    routing_reason: str
    
    # Historia routingu
    routing_history: List[Dict[str, Any]]

# ====== STANY DLA RAG ======

class RAGState(TypedDict):
    """
    Stan dla operacji Retrieval-Augmented Generation
    """
    query: str
    retrieved_documents: List[Dict[str, Any]]
    embeddings: Optional[List[float]]
    similarity_scores: List[float]
    
    # Metadata dokumentów
    document_metadata: List[Dict[str, Any]]
    
    # Konfiguracja wyszukiwania
    search_params: Dict[str, Any]

# ====== POMOCNICZE KLASY DANYCH ======

@dataclass
class AgentMetadata:
    """Metadata agenta"""
    agent_id: str
    agent_type: str
    model_name: str
    timestamp: str
    processing_time: float
    token_usage: Optional[Dict[str, int]] = None

@dataclass
class TaskResult:
    """Wynik zadania agenta"""
    success: bool
    result: Any
    error_message: Optional[str] = None
    metadata: Optional[AgentMetadata] = None

@dataclass
class RoutingDecision:
    """Decyzja routingu supervisora"""
    target_agent: str
    confidence: float
    reasoning: str
    fallback_agent: Optional[str] = None

# ====== FUNKCJE POMOCNICZE ======

def create_initial_state(
    user_message: str,
    thread_id: str,
    user_id: Optional[str] = None,
    agent_type: str = "supervisor"
) -> SystemState:
    """Tworzenie początkowego stanu systemu"""
    return SystemState(
        messages=[],
        thread_id=thread_id,
        user_id=user_id,
        agent_type=agent_type,
        context={},
        metadata={},
        next_agent=None,
        requires_handoff=False,
        workforce_context=None,
        strategist_context=None
    )

def update_state_with_message(state: SystemState, message: AnyMessage) -> SystemState:
    """Aktualizacja stanu o nową wiadomość"""
    new_state = state.copy()
    new_state["messages"] = add_messages(state["messages"], [message])
    return new_state

def extract_agent_context(state: SystemState, agent_type: str) -> Dict[str, Any]:
    """Wyciągnięcie kontekstu dla konkretnego agenta"""
    base_context = {
        "thread_id": state["thread_id"],
        "user_id": state["user_id"],
        "messages": state["messages"],
        "global_context": state["context"]
    }
    
    if agent_type == "workforce" and state["workforce_context"]:
        base_context.update(state["workforce_context"])
    elif agent_type == "strategist" and state["strategist_context"]:
        base_context.update(state["strategist_context"])
    
    return base_context