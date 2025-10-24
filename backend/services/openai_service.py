"""
Serwis do komunikacji z OpenAI API (GPT-4o dla Strategist Agent)
"""

import asyncio
from typing import Dict, List, Any, Optional
import openai
import structlog
from datetime import datetime

from utils.config import get_settings

logger = structlog.get_logger(__name__)

class OpenAIService:
    """Serwis do komunikacji z OpenAI API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.OPENAI_API_KEY
        self.model = self.settings.OPENAI_MODEL
        
        # Inicjalizacja klienta OpenAI
        self.client = openai.AsyncOpenAI(api_key=self.api_key)
    
    async def check_connection(self) -> bool:
        """Sprawdzenie połączenia z OpenAI API"""
        try:
            await self.client.models.list()
            return True
        except Exception as e:
            logger.error("Błąd połączenia z OpenAI", error=str(e))
            return False
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 2048,
        temperature: float = 0.7,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generowanie tekstu przez GPT-4o
        
        Args:
            prompt: Prompt użytkownika
            system_prompt: Systemowy prompt
            max_tokens: Maksymalna liczba tokenów
            temperature: Temperatura
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict z odpowiedzią modelu
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            logger.info("Wysyłanie requestu do OpenAI",
                       model=self.model,
                       prompt_length=len(prompt),
                       max_tokens=max_tokens)
            
            start_time = datetime.now()
            
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature,
                **kwargs
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info("Otrzymano odpowiedź z OpenAI",
                       processing_time=processing_time,
                       tokens_used=response.usage.total_tokens if response.usage else 0)
            
            return {
                "text": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                    "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                    "total_tokens": response.usage.total_tokens if response.usage else 0
                },
                "model": self.model,
                "processing_time": processing_time,
                "raw_response": response
            }
            
        except Exception as e:
            logger.error("Błąd generowania tekstu przez OpenAI", error=str(e))
            raise
    
    async def risk_analysis(
        self,
        situation_description: str,
        business_context: str = ""
    ) -> Dict[str, Any]:
        """
        Analiza ryzyka - specjalizacja Strategist Agent
        
        Args:
            situation_description: Opis sytuacji/projektu
            business_context: Kontekst biznesowy
            
        Returns:
            Dict z analizą ryzyka
        """
        from agents.prompts import STRATEGIST_SYSTEM_PROMPT, RISK_ANALYSIS_PROMPT
        
        user_prompt = RISK_ANALYSIS_PROMPT.format(
            situation_description=situation_description,
            business_context=business_context
        )
        
        try:
            result = await self.generate_text(
                prompt=user_prompt,
                system_prompt=STRATEGIST_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.6  # Średnia temperatura dla analizy
            )
            
            return {
                "risk_analysis": result["text"],
                "situation": situation_description,
                "context": business_context,
                "analysis_type": "risk_analysis",
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd analizy ryzyka", error=str(e))
            raise
    
    async def strategic_qa(
        self,
        question: str,
        business_context: str = "",
        analysis_type: str = "strategic_qa"
    ) -> Dict[str, Any]:
        """
        Strategiczne Q&A - specjalizacja Strategist Agent
        
        Args:
            question: Pytanie strategiczne
            business_context: Kontekst biznesowy
            analysis_type: Typ analizy
            
        Returns:
            Dict z odpowiedzią strategiczną
        """
        from agents.prompts import STRATEGIST_SYSTEM_PROMPT, STRATEGIST_USER_PROMPT
        
        user_prompt = STRATEGIST_USER_PROMPT.format(
            analysis_type=analysis_type,
            business_context=business_context,
            user_query=question,
            additional_data=""
        )
        
        try:
            result = await self.generate_text(
                prompt=user_prompt,
                system_prompt=STRATEGIST_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.7
            )
            
            return {
                "strategic_answer": result["text"],
                "question": question,
                "context": business_context,
                "analysis_type": analysis_type,
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd strategicznego Q&A", error=str(e))
            raise
    
    async def decision_support(
        self,
        decision_context: str,
        options: List[str],
        criteria: List[str] = None
    ) -> Dict[str, Any]:
        """
        Wsparcie decyzyjne - analiza opcji i rekomendacje
        
        Args:
            decision_context: Kontekst decyzji
            options: Lista opcji do rozważenia
            criteria: Kryteria oceny
            
        Returns:
            Dict z analizą decyzyjną
        """
        from agents.prompts import STRATEGIST_SYSTEM_PROMPT
        
        criteria_text = ""
        if criteria:
            criteria_text = f"\nKryteria oceny: {', '.join(criteria)}"
        
        user_prompt = f"""
        Przeprowadź analizę decyzyjną dla następującej sytuacji:

        Kontekst decyzji:
        {decision_context}

        Opcje do rozważenia:
        {chr(10).join([f"{i+1}. {option}" for i, option in enumerate(options)])}
        {criteria_text}

        Wykonaj pełną analizę decyzyjną według metodologii strategicznej:
        1. Analiza każdej opcji
        2. Macierz decyzyjna (jeśli są kryteria)
        3. Analiza ryzyk i korzyści
        4. Rekomendacja z uzasadnieniem
        5. Plan implementacji
        """
        
        try:
            result = await self.generate_text(
                prompt=user_prompt,
                system_prompt=STRATEGIST_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.6
            )
            
            return {
                "decision_analysis": result["text"],
                "context": decision_context,
                "options": options,
                "criteria": criteria,
                "analysis_type": "decision_support",
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd wsparcia decyzyjnego", error=str(e))
            raise
    
    async def complex_reasoning(
        self,
        problem_description: str,
        context: Dict[str, Any] = None
    ) -> Dict[str, Any]:
        """
        Złożone rozumowanie i rozwiązywanie problemów
        
        Args:
            problem_description: Opis problemu
            context: Dodatkowy kontekst
            
        Returns:
            Dict z analizą i rozwiązaniem
        """
        from agents.prompts import STRATEGIST_SYSTEM_PROMPT
        
        context_text = ""
        if context:
            context_text = f"\nDodatkowy kontekst: {context}"
        
        user_prompt = f"""
        Problem do rozwiązania:
        {problem_description}
        {context_text}

        Przeprowadź głęboką analizę problemu wykorzystując:
        1. Dekompozycję problemu na części składowe
        2. Analizę przyczynowo-skutkową
        3. Myślenie systemowe
        4. Różne perspektywy i podejścia
        5. Syntezę rozwiązań
        6. Plan działania z priorytetami

        Zastosuj metodologię strategicznego rozwiązywania problemów.
        """
        
        try:
            result = await self.generate_text(
                prompt=user_prompt,
                system_prompt=STRATEGIST_SYSTEM_PROMPT,
                max_tokens=2048,
                temperature=0.7
            )
            
            return {
                "reasoning_analysis": result["text"],
                "problem": problem_description,
                "context": context,
                "analysis_type": "complex_reasoning",
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd złożonego rozumowania", error=str(e))
            raise