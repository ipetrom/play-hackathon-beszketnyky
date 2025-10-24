"""
Serwis do komunikacji z Scaleway GenAI API (Mistral)
"""

import json
import asyncio
from typing import Dict, List, Any, Optional
import httpx
import structlog
from datetime import datetime

from utils.config import get_settings

logger = structlog.get_logger(__name__)

class ScalewayService:
    """Serwis do komunikacji z Scaleway GenAI API"""
    
    def __init__(self):
        self.settings = get_settings()
        self.base_url = self.settings.SCALEWAY_GENAI_ENDPOINT
        self.api_key = self.settings.SCALEWAY_API_KEY
        self.project_id = self.settings.SCALEWAY_PROJECT_ID
        self.model = self.settings.SCALEWAY_MODEL
        
        # Konfiguracja HTTP klienta
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(60.0),
            headers={
                "X-Auth-Token": self.api_key,
                "Content-Type": "application/json"
            }
        )
    
    async def check_connection(self) -> bool:
        """Sprawdzenie połączenia z Scaleway GenAI API"""
        try:
            response = await self.client.get(f"{self.base_url}/models")
            return response.status_code == 200
        except Exception as e:
            logger.error("Błąd połączenia z Scaleway", error=str(e))
            return False
    
    async def generate_text(
        self,
        prompt: str,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        top_p: float = 0.9,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Generowanie tekstu przez Mistral model
        
        Args:
            prompt: Tekst promptu
            max_tokens: Maksymalna liczba tokenów
            temperature: Temperatura (kreatywność)
            top_p: Top-p sampling
            **kwargs: Dodatkowe parametry
            
        Returns:
            Dict z odpowiedzią modelu
        """
        try:
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                **kwargs
            }
            
            logger.info("Wysyłanie requestu do Scaleway GenAI",
                       model=self.model,
                       prompt_length=len(prompt),
                       max_tokens=max_tokens)
            
            start_time = datetime.now()
            
            response = await self.client.post(
                f"{self.base_url}/chat/completions",
                json=payload
            )
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            if response.status_code != 200:
                error_msg = f"Błąd API Scaleway: {response.status_code} - {response.text}"
                logger.error("Błąd API Scaleway", 
                           status_code=response.status_code,
                           error=response.text)
                raise Exception(error_msg)
            
            result = response.json()
            
            logger.info("Otrzymano odpowiedź z Scaleway GenAI",
                       processing_time=processing_time,
                       tokens_used=result.get("usage", {}).get("total_tokens", 0))
            
            return {
                "text": result["choices"][0]["message"]["content"],
                "usage": result.get("usage", {}),
                "model": self.model,
                "processing_time": processing_time,
                "raw_response": result
            }
            
        except Exception as e:
            logger.error("Błąd generowania tekstu przez Scaleway", error=str(e))
            raise
    
    async def tag_content(self, content: str) -> Dict[str, Any]:
        """
        Tagowanie treści - specjalizacja Workforce Agent
        
        Args:
            content: Treść do otagowania
            
        Returns:
            Dict z tagami i metadata
        """
        from agents.prompts import TAGGING_PROMPT
        
        prompt = TAGGING_PROMPT.format(content=content)
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                max_tokens=512,
                temperature=0.3  # Niska temperatura dla consistency
            )
            
            # Próba parsowania JSON odpowiedzi
            try:
                tags_data = json.loads(result["text"])
            except json.JSONDecodeError:
                # Fallback jeśli nie ma JSON
                tags_data = {
                    "main_topics": [],
                    "industry": [],
                    "content_type": "unknown",
                    "complexity": "medium",
                    "target_audience": [],
                    "confidence": 0.5,
                    "raw_text": result["text"]
                }
            
            return {
                "tags": tags_data,
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd tagowania treści", error=str(e))
            raise
    
    async def summarize_text(
        self,
        content: str,
        summary_type: str = "quick_overview"
    ) -> Dict[str, Any]:
        """
        Streszczanie tekstu - specjalizacja Workforce Agent
        
        Args:
            content: Tekst do streszczenia
            summary_type: Typ streszczenia (executive_summary, technical_summary, quick_overview)
            
        Returns:
            Dict ze streszczeniem i metadata
        """
        from agents.prompts import SUMMARIZATION_PROMPT
        
        prompt = SUMMARIZATION_PROMPT.format(
            content=content,
            summary_type=summary_type
        )
        
        try:
            # Dostosuj parametry do typu streszczenia
            max_tokens = {
                "executive_summary": 300,
                "technical_summary": 400,
                "quick_overview": 200
            }.get(summary_type, 300)
            
            result = await self.generate_text(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=0.4
            )
            
            return {
                "summary": result["text"],
                "summary_type": summary_type,
                "original_length": len(content),
                "summary_length": len(result["text"]),
                "compression_ratio": len(result["text"]) / len(content),
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd streszczania tekstu", error=str(e))
            raise
    
    async def basic_qa(self, question: str, context: str = "") -> Dict[str, Any]:
        """
        Podstawowe Q&A - specjalizacja Workforce Agent
        
        Args:
            question: Pytanie użytkownika
            context: Dodatkowy kontekst
            
        Returns:
            Dict z odpowiedzią i metadata
        """
        prompt = f"""Odpowiedz na następujące pytanie zwięźle i precyzyjnie.

{"Kontekst: " + context if context else ""}

Pytanie: {question}

Odpowiedź:"""
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                max_tokens=512,
                temperature=0.5
            )
            
            return {
                "answer": result["text"],
                "question": question,
                "context_provided": bool(context),
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd basic Q&A", error=str(e))
            raise
    
    async def process_data(self, data: Any, operation: str) -> Dict[str, Any]:
        """
        Przetwarzanie danych strukturalnych
        
        Args:
            data: Dane do przetworzenia
            operation: Typ operacji (format_conversion, analysis, extraction)
            
        Returns:
            Dict z przetworzonymi danymi
        """
        prompt = f"""Wykonaj operację "{operation}" na następujących danych:

Dane:
{str(data)}

Operacja: {operation}

Wynik:"""
        
        try:
            result = await self.generate_text(
                prompt=prompt,
                max_tokens=1024,
                temperature=0.3
            )
            
            return {
                "processed_data": result["text"],
                "operation": operation,
                "input_data": data,
                "metadata": {
                    "model": result["model"],
                    "processing_time": result["processing_time"],
                    "tokens_used": result["usage"].get("total_tokens", 0)
                }
            }
            
        except Exception as e:
            logger.error("Błąd przetwarzania danych", error=str(e))
            raise
    
    async def close(self):
        """Zamknięcie klienta HTTP"""
        await self.client.aclose()
    
    def __del__(self):
        """Destruktor - zamknięcie klienta"""
        try:
            asyncio.create_task(self.close())
        except Exception:
            pass