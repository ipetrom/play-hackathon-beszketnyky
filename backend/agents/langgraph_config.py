"""
Konfiguracja LangGraph z agentami Supervisor, Workforce i Strategist
"""

import json
from typing import Dict, Any, List, Optional, Literal
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, BaseMessage
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
import structlog

from agents.states import AgentState
from agents.prompts import (
    SUPERVISOR_PROMPT,
    WORKFORCE_PROMPT, 
    STRATEGIST_PROMPT
)
from services.scaleway_genai_service import ScalewayGenAIService
from services.openai_service import OpenAIService
from services.rag_service import RAGService
from utils.config import get_settings

logger = structlog.get_logger(__name__)

class LangGraphOrchestrator:
    """Orkiestrator LangGraph z wieloma agentami"""
    
    def __init__(self):
        self.settings = get_settings()
        self.memory = MemorySaver()
        
        # Inicjalizuj serwisy
        self.scaleway_service = ScalewayGenAIService()
        self.openai_service = OpenAIService()
        self.rag_service = RAGService()
        
        # Zbuduj graf
        self.app = self._create_graph()
    
    def _create_graph(self) -> StateGraph:
        """Tworzenie grafu LangGraph z agentami"""
        
        # Definicja workflow
        workflow = StateGraph(AgentState)
        
        # Dodaj węzły
        workflow.add_node("supervisor", self.supervisor_agent)
        workflow.add_node("workforce", self.workforce_agent)  
        workflow.add_node("strategist", self.strategist_agent)
        
        # Dodaj routing
        workflow.set_entry_point("supervisor")
        
        workflow.add_conditional_edges(
            "supervisor",
            self.should_continue,
            {
                "workforce": "workforce",
                "strategist": "strategist", 
                "FINISH": END
            }
        )
        
        workflow.add_edge("workforce", "supervisor")
        workflow.add_edge("strategist", "supervisor")
        
        # Skompiluj z checkpointer
        return workflow.compile(checkpointer=self.memory)
    
    async def supervisor_agent(self, state: AgentState) -> AgentState:
        """
        Agent nadzorujący - routuje zadania do odpowiednich agentów
        """
        try:
            logger.info("Supervisor agent processing", 
                       messages_count=len(state["messages"]),
                       current_agent=state.get("current_agent"))
            
            # Pobierz ostatnią wiadomość użytkownika
            last_message = state["messages"][-1] if state["messages"] else None
            
            if not last_message:
                return {
                    **state,
                    "current_agent": "supervisor",
                    "next_action": "FINISH",
                    "messages": state["messages"] + [
                        AIMessage(content="Brak wiadomości do przetworzenia.")
                    ]
                }
            
            # Przeanalizuj treść aby zdecydować o routingu
            content = last_message.content if hasattr(last_message, 'content') else str(last_message)
            
            # Logika routingu
            routing_decision = await self._analyze_routing(content, state)
            
            # Dodaj wiadomość supervisora z decyzją
            supervisor_message = AIMessage(
                content=f"[SUPERVISOR] Przekierowuję zadanie do: {routing_decision['agent']}. "
                       f"Powód: {routing_decision['reason']}"
            )
            
            return {
                **state,
                "current_agent": "supervisor",
                "next_action": routing_decision["agent"],
                "routing_reason": routing_decision["reason"],
                "messages": state["messages"] + [supervisor_message]
            }
            
        except Exception as e:
            logger.error("Błąd w supervisor agent", error=str(e))
            return {
                **state,
                "current_agent": "supervisor",
                "next_action": "FINISH",
                "error": str(e),
                "messages": state["messages"] + [
                    AIMessage(content=f"Błąd supervisora: {str(e)}")
                ]
            }
    
    async def _analyze_routing(self, content: str, state: AgentState) -> Dict[str, str]:
        """Analiza treści dla routingu"""
        
        # Słowa kluczowe dla różnych agentów
        strategic_keywords = [
            "strategia", "plan", "analiza", "prognoza", "wizja", "długoterminowy",
            "strategy", "analysis", "forecast", "planning", "vision", "roadmap"
        ]
        
        operational_keywords = [
            "zadanie", "wykonaj", "zrób", "napisz", "stwórz", "wygeneruj",
            "task", "do", "create", "generate", "write", "make", "execute"
        ]
        
        content_lower = content.lower()
        
        # Sprawdź czy to zadanie strategiczne
        if any(keyword in content_lower for keyword in strategic_keywords):
            return {
                "agent": "strategist",
                "reason": "Wykryto zapytanie strategiczne wymagające głębokiej analizy"
            }
        
        # Sprawdź czy to zadanie operacyjne
        if any(keyword in content_lower for keyword in operational_keywords):
            return {
                "agent": "workforce", 
                "reason": "Wykryto zadanie operacyjne do szybkiego wykonania"
            }
        
        # Sprawdź długość - długie zapytania do strategista
        if len(content) > 500:
            return {
                "agent": "strategist",
                "reason": "Długie zapytanie wymagające szczegółowej analizy"
            }
        
        # Domyślnie workforce dla prostych zadań
        return {
            "agent": "workforce",
            "reason": "Standardowe zadanie operacyjne"
        }
    
    async def workforce_agent(self, state: AgentState) -> AgentState:
        """
        Agent siły roboczej - szybkie wykonywanie zadań przez Scaleway Mistral
        """
        try:
            logger.info("Workforce agent processing",
                       messages_count=len(state["messages"]))
            
            # Pobierz kontekst z RAG jeśli potrzebny
            last_user_message = None
            for msg in reversed(state["messages"]):
                if hasattr(msg, 'content') and not msg.content.startswith('['):
                    last_user_message = msg.content
                    break
            
            rag_context = ""
            if last_user_message:
                rag_context = await self.rag_service.get_context_for_query(
                    query=last_user_message,
                    max_chunks=2,
                    similarity_threshold=0.6
                )
            
            # Przygotuj prompt
            system_prompt = WORKFORCE_PROMPT
            if rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.":
                system_prompt += f"\n\nKONTEKST Z BAZY WIEDZY:\n{rag_context}"
            
            # Przygotuj wiadomości dla Scaleway
            messages = []
            for msg in state["messages"]:
                if hasattr(msg, 'content') and not msg.content.startswith('['):
                    if isinstance(msg, HumanMessage):
                        messages.append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Dodaj system prompt
            messages.insert(0, {"role": "system", "content": system_prompt})
            
            # Wywołaj Scaleway GenAI
            async with self.scaleway_service as service:
                result = await service.chat_completion(
                    messages=messages,
                    max_tokens=1500,
                    temperature=0.7
                )
            
            if result['success']:
                response_content = result['message']['content']
                
                # Dodaj informację o źródle
                if rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.":
                    response_content += "\n\n[Odpowiedź oparta na dokumentach z bazy wiedzy]"
                
                response_message = AIMessage(content=response_content)
                
                logger.info("Workforce agent completed successfully",
                           response_length=len(response_content))
                
                return {
                    **state,
                    "current_agent": "workforce", 
                    "next_action": "supervisor",
                    "messages": state["messages"] + [response_message],
                    "rag_used": bool(rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.")
                }
            else:
                error_msg = f"Błąd Scaleway GenAI: {result.get('error', 'Unknown error')}"
                logger.error("Workforce agent failed", error=error_msg)
                
                return {
                    **state,
                    "current_agent": "workforce",
                    "next_action": "FINISH", 
                    "error": error_msg,
                    "messages": state["messages"] + [
                        AIMessage(content=f"Przepraszam, wystąpił błąd: {error_msg}")
                    ]
                }
                
        except Exception as e:
            logger.error("Błąd w workforce agent", error=str(e))
            return {
                **state,
                "current_agent": "workforce",
                "next_action": "FINISH",
                "error": str(e),
                "messages": state["messages"] + [
                    AIMessage(content=f"Błąd workforce agent: {str(e)}")
                ]
            }
    
    async def strategist_agent(self, state: AgentState) -> AgentState:
        """
        Agent strategiczny - głęboka analiza przez OpenAI GPT-4o
        """
        try:
            logger.info("Strategist agent processing",
                       messages_count=len(state["messages"]))
            
            # Pobierz rozszerzony kontekst z RAG
            last_user_message = None
            for msg in reversed(state["messages"]):
                if hasattr(msg, 'content') and not msg.content.startswith('['):
                    last_user_message = msg.content
                    break
            
            rag_context = ""
            if last_user_message:
                rag_context = await self.rag_service.get_context_for_query(
                    query=last_user_message,
                    max_chunks=5,  # Więcej kontekstu dla strategista
                    similarity_threshold=0.5
                )
            
            # Przygotuj prompt
            system_prompt = STRATEGIST_PROMPT
            if rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.":
                system_prompt += f"\n\nKONTEKST Z BAZY WIEDZY:\n{rag_context}"
            
            # Przygotuj wiadomości dla OpenAI
            messages = [
                {"role": "system", "content": system_prompt}
            ]
            
            for msg in state["messages"]:
                if hasattr(msg, 'content') and not msg.content.startswith('['):
                    if isinstance(msg, HumanMessage):
                        messages.append({"role": "user", "content": msg.content})
                    elif isinstance(msg, AIMessage):
                        messages.append({"role": "assistant", "content": msg.content})
            
            # Wywołaj OpenAI
            result = await self.openai_service.chat_completion(
                messages=messages,
                model="gpt-4o",
                max_tokens=2000,
                temperature=0.3  # Niższa temperatura dla strategicznych analiz
            )
            
            if result['success']:
                response_content = result['message']['content']
                
                # Dodaj informację o źródle
                if rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.":
                    response_content += "\n\n[Strategiczna analiza oparta na dokumentach z bazy wiedzy]"
                
                response_message = AIMessage(content=response_content)
                
                logger.info("Strategist agent completed successfully",
                           response_length=len(response_content))
                
                return {
                    **state,
                    "current_agent": "strategist",
                    "next_action": "supervisor", 
                    "messages": state["messages"] + [response_message],
                    "rag_used": bool(rag_context and rag_context != "Brak relevantnych dokumentów w bazie wiedzy.")
                }
            else:
                error_msg = f"Błąd OpenAI: {result.get('error', 'Unknown error')}"
                logger.error("Strategist agent failed", error=error_msg)
                
                return {
                    **state,
                    "current_agent": "strategist",
                    "next_action": "FINISH",
                    "error": error_msg, 
                    "messages": state["messages"] + [
                        AIMessage(content=f"Przepraszam, wystąpił błąd strategiczny: {error_msg}")
                    ]
                }
                
        except Exception as e:
            logger.error("Błąd w strategist agent", error=str(e))
            return {
                **state,
                "current_agent": "strategist",
                "next_action": "FINISH",
                "error": str(e),
                "messages": state["messages"] + [
                    AIMessage(content=f"Błąd strategist agent: {str(e)}")
                ]
            }
    
    def should_continue(self, state: AgentState) -> Literal["workforce", "strategist", "FINISH"]:
        """
        Funkcja decyzyjna dla routingu
        """
        try:
            next_action = state.get("next_action", "FINISH")
            
            logger.info("Routing decision", 
                       next_action=next_action,
                       current_agent=state.get("current_agent"))
            
            # Sprawdź czy jest błąd
            if state.get("error"):
                return "FINISH"
            
            # Sprawdź czy supervisor podjął decyzję
            if next_action in ["workforce", "strategist"]:
                return next_action
            
            # Sprawdź czy agenci wykonali zadanie
            if state.get("current_agent") in ["workforce", "strategist"]:
                # Po wykonaniu zadania przez agenta, wróć do supervisora
                # który może zdecydować o zakończeniu lub dalszym procesowaniu
                return "FINISH"  # Tymczasowo kończymy po jednej iteracji
            
            return "FINISH"
            
        except Exception as e:
            logger.error("Błąd w should_continue", error=str(e))
            return "FINISH"
    
    async def invoke_async(
        self, 
        message: str, 
        thread_id: str = "default"
    ) -> Dict[str, Any]:
        """
        Asynchroniczne wywołanie grafu LangGraph
        
        Args:
            message: Wiadomość użytkownika
            thread_id: ID wątku konwersacji
            
        Returns:
            Dict z wynikiem przetwarzania
        """
        try:
            logger.info("Starting LangGraph invocation",
                       message_length=len(message),
                       thread_id=thread_id)
            
            # Przygotuj stan początkowy
            initial_state = {
                "messages": [HumanMessage(content=message)],
                "current_agent": None,
                "next_action": None,
                "thread_id": thread_id,
                "rag_used": False
            }
            
            # Konfiguracja
            config = {
                "configurable": {"thread_id": thread_id}
            }
            
            # Wywołaj graf
            final_state = await self.app.ainvoke(initial_state, config)
            
            # Pobierz ostatnią odpowiedź
            last_message = final_state["messages"][-1] if final_state["messages"] else None
            response_content = last_message.content if last_message else "Brak odpowiedzi"
            
            logger.info("LangGraph invocation completed", 
                       final_agent=final_state.get("current_agent"),
                       messages_count=len(final_state["messages"]),
                       rag_used=final_state.get("rag_used", False))
            
            return {
                'success': True,
                'response': response_content,
                'agent_used': final_state.get("current_agent"),
                'routing_reason': final_state.get("routing_reason"),
                'rag_used': final_state.get("rag_used", False),
                'thread_id': thread_id,
                'message_count': len(final_state["messages"])
            }
            
        except Exception as e:
            logger.error("Błąd w LangGraph invocation", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'response': f"Przepraszam, wystąpił błąd: {str(e)}",
                'thread_id': thread_id
            }

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