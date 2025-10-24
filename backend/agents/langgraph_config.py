"""
Konfiguracja LangGraph - orchestracja agentów AI
"""

import json
from typing import Dict, Any, Literal
from langchain_core.messages import HumanMessage, AIMessage
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.postgres import PostgresSaver
import structlog

from agents.states import SystemState, create_initial_state, update_state_with_message
from agents.prompts import SUPERVISOR_SYSTEM_PROMPT, SUPERVISOR_USER_PROMPT
from services.scaleway_service import ScalewayService
from services.openai_service import OpenAIService
from utils.config import get_settings

logger = structlog.get_logger(__name__)

# ====== FUNKCJE AGENTÓW ======

async def supervisor_agent(state: SystemState) -> SystemState:
    """
    Supervisor Agent - decyduje o routingu między Workforce i Strategist
    """
    try:
        logger.info("Supervisor Agent - analiza requestu", thread_id=state["thread_id"])
        
        # Pobierz ostatnią wiadomość użytkownika
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            raise ValueError("Brak wiadomości użytkownika do analizy")
        
        latest_message = user_messages[-1].content
        
        # Przygotuj kontekst konwersacji
        conversation_context = "\n".join([
            f"{'User' if isinstance(msg, HumanMessage) else 'AI'}: {msg.content}"
            for msg in state["messages"][-5:]  # Ostatnie 5 wiadomości
        ])
        
        # Prompt dla supervisora
        user_prompt = SUPERVISOR_USER_PROMPT.format(
            user_message=latest_message,
            conversation_context=conversation_context
        )
        
        # Użyj Scaleway Mistral dla routingu (szybsze i tańsze)
        scaleway_service = ScalewayService()
        result = await scaleway_service.generate_text(
            prompt=f"{SUPERVISOR_SYSTEM_PROMPT}\n\n{user_prompt}",
            max_tokens=512,
            temperature=0.3
        )
        
        # Parsowanie decyzji routingu
        try:
            routing_decision = json.loads(result["text"])
        except json.JSONDecodeError:
            # Fallback - domyślnie workforce
            routing_decision = {
                "target_agent": "workforce",
                "confidence": 0.5,
                "reasoning": "Błąd parsowania JSON, domyślny routing",
                "context_for_agent": {}
            }
        
        # Aktualizacja stanu
        new_state = state.copy()
        new_state["next_agent"] = routing_decision["target_agent"]
        new_state["metadata"]["routing_decision"] = routing_decision
        new_state["metadata"]["supervisor_result"] = result
        
        logger.info("Supervisor - decyzja routingu",
                   target_agent=routing_decision["target_agent"],
                   confidence=routing_decision["confidence"],
                   thread_id=state["thread_id"])
        
        await scaleway_service.close()
        return new_state
        
    except Exception as e:
        logger.error("Błąd Supervisor Agent", error=str(e), thread_id=state["thread_id"])
        # Fallback do workforce
        new_state = state.copy()
        new_state["next_agent"] = "workforce"
        new_state["metadata"]["error"] = str(e)
        return new_state

async def workforce_agent(state: SystemState) -> SystemState:
    """
    Workforce Agent - Scaleway Mistral dla podstawowych zadań
    """
    try:
        logger.info("Workforce Agent - przetwarzanie", thread_id=state["thread_id"])
        
        # Pobierz ostatnią wiadomość użytkownika
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            raise ValueError("Brak wiadomości użytkownika")
        
        latest_message = user_messages[-1].content
        
        # Określ typ zadania na podstawie kontekstu
        routing_decision = state["metadata"].get("routing_decision", {})
        context_for_agent = routing_decision.get("context_for_agent", {})
        
        scaleway_service = ScalewayService()
        
        # Analiza typu zadania
        if "tag" in latest_message.lower() or "category" in latest_message.lower():
            # Zadanie tagowania
            result = await scaleway_service.tag_content(latest_message)
            response_text = f"🏷️ **Analiza tagów:**\n\n{json.dumps(result['tags'], indent=2, ensure_ascii=False)}"
            
        elif "summar" in latest_message.lower() or "streszcz" in latest_message.lower():
            # Zadanie streszczania
            result = await scaleway_service.summarize_text(latest_message)
            response_text = f"📄 **Streszczenie:**\n\n{result['summary']}"
            
        else:
            # Podstawowe Q&A
            context = "\n".join([msg.content for msg in state["messages"][-3:] if isinstance(msg, HumanMessage)])
            result = await scaleway_service.basic_qa(latest_message, context)
            response_text = result["answer"]
        
        # Aktualizacja stanu
        ai_message = AIMessage(content=response_text)
        new_state = update_state_with_message(state, ai_message)
        new_state["agent_type"] = "workforce"
        new_state["metadata"]["workforce_result"] = result
        new_state["next_agent"] = None
        
        logger.info("Workforce Agent - zakończone",
                   response_length=len(response_text),
                   thread_id=state["thread_id"])
        
        await scaleway_service.close()
        return new_state
        
    except Exception as e:
        logger.error("Błąd Workforce Agent", error=str(e), thread_id=state["thread_id"])
        error_message = AIMessage(content="Przepraszam, wystąpił błąd podczas przetwarzania Twojego żądania.")
        new_state = update_state_with_message(state, error_message)
        new_state["metadata"]["error"] = str(e)
        return new_state

async def strategist_agent(state: SystemState) -> SystemState:
    """
    Strategist Agent - OpenAI GPT-4o dla strategicznej analizy
    """
    try:
        logger.info("Strategist Agent - analiza strategiczna", thread_id=state["thread_id"])
        
        # Pobierz ostatnią wiadomość użytkownika
        user_messages = [msg for msg in state["messages"] if isinstance(msg, HumanMessage)]
        if not user_messages:
            raise ValueError("Brak wiadomości użytkownika")
        
        latest_message = user_messages[-1].content
        
        # Kontekst biznesowy z poprzednich wiadomości
        business_context = "\n".join([
            msg.content for msg in state["messages"][-5:] 
            if isinstance(msg, (HumanMessage, AIMessage))
        ])
        
        openai_service = OpenAIService()
        
        # Określ typ analizy strategicznej
        if "risk" in latest_message.lower() or "ryzyko" in latest_message.lower():
            # Analiza ryzyka
            result = await openai_service.risk_analysis(latest_message, business_context)
            response_text = result["risk_analysis"]
            
        elif "decision" in latest_message.lower() or "decyzja" in latest_message.lower():
            # Wsparcie decyzyjne - próba wyciągnięcia opcji z tekstu
            options = ["Opcja A", "Opcja B"]  # Placeholder - można zaimplementować parsing
            result = await openai_service.decision_support(latest_message, options)
            response_text = result["decision_analysis"]
            
        elif any(word in latest_message.lower() for word in ["complex", "problem", "solve", "złożony"]):
            # Złożone rozumowanie
            result = await openai_service.complex_reasoning(latest_message)
            response_text = result["reasoning_analysis"]
            
        else:
            # Strategiczne Q&A
            result = await openai_service.strategic_qa(latest_message, business_context)
            response_text = result["strategic_answer"]
        
        # Aktualizacja stanu
        ai_message = AIMessage(content=response_text)
        new_state = update_state_with_message(state, ai_message)
        new_state["agent_type"] = "strategist"
        new_state["metadata"]["strategist_result"] = result
        new_state["next_agent"] = None
        
        logger.info("Strategist Agent - zakończone",
                   response_length=len(response_text),
                   thread_id=state["thread_id"])
        
        return new_state
        
    except Exception as e:
        logger.error("Błąd Strategist Agent", error=str(e), thread_id=state["thread_id"])
        error_message = AIMessage(content="Przepraszam, wystąpił błąd podczas analizy strategicznej.")
        new_state = update_state_with_message(state, error_message)
        new_state["metadata"]["error"] = str(e)
        return new_state

# ====== FUNKCJE ROUTINGU ======

def should_continue(state: SystemState) -> Literal["workforce", "strategist", "__end__"]:
    """Decyzja o kontynuacji na podstawie decyzji supervisora"""
    next_agent = state.get("next_agent")
    
    if next_agent == "workforce":
        return "workforce"
    elif next_agent == "strategist":
        return "strategist"
    else:
        return "__end__"

# ====== BUDOWANIE GRAFU ======

def create_agent_graph():
    """Tworzenie grafu LangGraph z agentami"""
    
    # Budowanie grafu
    workflow = StateGraph(SystemState)
    
    # Dodanie węzłów (agentów)
    workflow.add_node("supervisor", supervisor_agent)
    workflow.add_node("workforce", workforce_agent)
    workflow.add_node("strategist", strategist_agent)
    
    # Punkt wejścia
    workflow.set_entry_point("supervisor")
    
    # Routing z supervisora
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "workforce": "workforce",
            "strategist": "strategist",
            "__end__": END
        }
    )
    
    # Końcowe edge'y
    workflow.add_edge("workforce", END)
    workflow.add_edge("strategist", END)
    
    # Konfiguracja checkpointera (PostgreSQL)
    settings = get_settings()
    
    try:
        checkpointer = PostgresSaver.from_conn_string(settings.database_url)
        graph = workflow.compile(checkpointer=checkpointer)
        logger.info("Graf LangGraph skompilowany z PostgreSQL checkpointer")
    except Exception as e:
        logger.warning("Nie można skonfigurować PostgreSQL checkpointer, używam pamięci", error=str(e))
        graph = workflow.compile()
    
    return graph

# Export głównego grafu
agent_graph = create_agent_graph()