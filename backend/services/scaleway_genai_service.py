"""
Serwis do integracji z Scaleway GenAI API
"""

import asyncio
from typing import Dict, Any, Optional, List, AsyncGenerator
import httpx
import structlog
from datetime import datetime

from utils.config import get_settings

logger = structlog.get_logger(__name__)

class ScalewayGenAIService:
    """Serwis do integracji z Scaleway GenAI API (Mistral)"""
    
    def __init__(self):
        self.settings = get_settings()
        self.api_key = self.settings.SCALEWAY_SECRET_KEY
        self.project_id = self.settings.SCALEWAY_PROJECT_ID
        self.region = self.settings.SCALEWAY_REGION
        
        # Domyślne ustawienia dla Mistral
        self.model_name = "mistral-7b-instruct"
        self.base_url = f"https://api.scaleway.com/v1alpha1/regions/{self.region}/ai-models"
        
        # HTTP client z timeout i retry
        self.client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0, read=60.0),
            limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def _get_headers(self) -> Dict[str, str]:
        """Przygotowanie nagłówków dla Scaleway API"""
        return {
            "X-Auth-Token": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": "LangGraph-Agent/1.0"
        }
    
    async def list_available_models(self) -> List[Dict[str, Any]]:
        """
        Pobieranie listy dostępnych modeli w Scaleway GenAI
        
        Returns:
            Lista dostępnych modeli
        """
        try:
            logger.info("Pobieranie listy modeli Scaleway GenAI")
            
            response = await self.client.get(
                f"{self.base_url}/models",
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                models = response.json().get('models', [])
                logger.info("Modele pobrane pomyślnie", count=len(models))
                return models
            else:
                logger.error("Błąd pobierania modeli", 
                           status_code=response.status_code,
                           response=response.text)
                return []
                
        except Exception as e:
            logger.error("Błąd połączenia z Scaleway GenAI", error=str(e))
            return []
    
    async def generate_completion(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        model: str = None
    ) -> Dict[str, Any]:
        """
        Generowanie tekstu przez Scaleway GenAI (Mistral)
        
        Args:
            prompt: Prompt do wygenerowania
            max_tokens: Maksymalna liczba tokenów
            temperature: Temperatura generowania (0.0-1.0)
            top_p: Top-p sampling (0.0-1.0)
            model: Nazwa modelu (domyślnie mistral-7b-instruct)
            
        Returns:
            Dict z wygenerowanym tekstem i metadanymi
        """
        try:
            model_name = model or self.model_name
            
            logger.info("Generowanie tekstu przez Scaleway GenAI",
                       model=model_name,
                       prompt_length=len(prompt),
                       max_tokens=max_tokens,
                       temperature=temperature)
            
            # Payload dla Scaleway GenAI API
            payload = {
                "model": model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stop": ["Human:", "Assistant:", "\n\n---"],
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/generate",
                headers=self._get_headers(),
                json=payload
            )
            
            if response.status_code == 200:
                result = response.json()
                
                generated_text = result.get('choices', [{}])[0].get('text', '').strip()
                
                logger.info("Tekst wygenerowany pomyślnie",
                           model=model_name,
                           generated_length=len(generated_text),
                           tokens_used=result.get('usage', {}).get('total_tokens', 0))
                
                return {
                    'success': True,
                    'text': generated_text,
                    'model': model_name,
                    'usage': result.get('usage', {}),
                    'finish_reason': result.get('choices', [{}])[0].get('finish_reason'),
                    'created_at': datetime.utcnow().isoformat()
                }
            else:
                error_msg = f"API Error: {response.status_code} - {response.text}"
                logger.error("Błąd API Scaleway GenAI", 
                           status_code=response.status_code,
                           error=response.text)
                
                return {
                    'success': False,
                    'error': error_msg,
                    'model': model_name
                }
                
        except asyncio.TimeoutError:
            logger.error("Timeout podczas generowania tekstu")
            return {
                'success': False,
                'error': 'Request timeout',
                'model': model_name
            }
        except Exception as e:
            logger.error("Błąd generowania tekstu", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'model': model_name
            }
    
    async def generate_streaming_completion(
        self,
        prompt: str,
        max_tokens: int = 1000,
        temperature: float = 0.7,
        top_p: float = 0.9,
        model: str = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Generowanie tekstu ze streamingiem
        
        Args:
            prompt: Prompt do wygenerowania
            max_tokens: Maksymalna liczba tokenów
            temperature: Temperatura generowania
            top_p: Top-p sampling
            model: Nazwa modelu
            
        Yields:
            Dict z chunkami wygenerowanego tekstu
        """
        try:
            model_name = model or self.model_name
            
            logger.info("Rozpoczęcie streaming generation",
                       model=model_name,
                       prompt_length=len(prompt))
            
            payload = {
                "model": model_name,
                "prompt": prompt,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "top_p": top_p,
                "stream": True
            }
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/generate",
                headers=self._get_headers(),
                json=payload
            ) as response:
                
                if response.status_code != 200:
                    yield {
                        'success': False,
                        'error': f"API Error: {response.status_code}",
                        'model': model_name
                    }
                    return
                
                buffer = ""
                async for chunk in response.aiter_text():
                    if chunk:
                        buffer += chunk
                        
                        # Sprawdź czy mamy kompletną linię SSE
                        while '\n' in buffer:
                            line, buffer = buffer.split('\n', 1)
                            line = line.strip()
                            
                            if line.startswith('data: '):
                                data = line[6:]  # Usuń "data: "
                                
                                if data == '[DONE]':
                                    yield {
                                        'success': True,
                                        'finished': True,
                                        'model': model_name
                                    }
                                    return
                                
                                try:
                                    import json
                                    chunk_data = json.loads(data)
                                    
                                    if 'choices' in chunk_data:
                                        delta = chunk_data['choices'][0].get('delta', {})
                                        if 'content' in delta:
                                            yield {
                                                'success': True,
                                                'delta': delta['content'],
                                                'model': model_name,
                                                'chunk_id': chunk_data.get('id')
                                            }
                                
                                except json.JSONDecodeError:
                                    continue
                
        except Exception as e:
            logger.error("Błąd streaming generation", error=str(e))
            yield {
                'success': False,
                'error': str(e),
                'model': model_name
            }
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        max_tokens: int = 1000,
        temperature: float = 0.7,
        model: str = None
    ) -> Dict[str, Any]:
        """
        Chat completion przez Scaleway GenAI
        
        Args:
            messages: Lista wiadomości w formacie [{"role": "user", "content": "..."}]
            max_tokens: Maksymalna liczba tokenów
            temperature: Temperatura generowania
            model: Nazwa modelu
            
        Returns:
            Dict z odpowiedzią chatbota
        """
        try:
            # Konwertuj messages na pojedynczy prompt dla Mistral
            prompt_parts = []
            
            for message in messages:
                role = message.get('role', 'user')
                content = message.get('content', '')
                
                if role == 'system':
                    prompt_parts.append(f"System: {content}")
                elif role == 'user':
                    prompt_parts.append(f"Human: {content}")
                elif role == 'assistant':
                    prompt_parts.append(f"Assistant: {content}")
            
            # Dodaj prompt dla asystenta
            prompt_parts.append("Assistant:")
            prompt = "\n\n".join(prompt_parts)
            
            logger.info("Chat completion przez Scaleway GenAI",
                       messages_count=len(messages),
                       prompt_length=len(prompt))
            
            result = await self.generate_completion(
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature,
                model=model
            )
            
            if result['success']:
                return {
                    'success': True,
                    'message': {
                        'role': 'assistant',
                        'content': result['text']
                    },
                    'model': result['model'],
                    'usage': result.get('usage', {}),
                    'created_at': result['created_at']
                }
            else:
                return result
                
        except Exception as e:
            logger.error("Błąd chat completion", error=str(e))
            return {
                'success': False,
                'error': str(e),
                'model': model or self.model_name
            }
    
    async def check_health(self) -> Dict[str, Any]:
        """
        Sprawdzenie zdrowia Scaleway GenAI API
        
        Returns:
            Dict ze statusem API
        """
        try:
            logger.info("Sprawdzanie zdrowia Scaleway GenAI API")
            
            # Prosty test z krótkim promptem
            test_result = await self.generate_completion(
                prompt="Test connection. Say 'OK'.",
                max_tokens=10,
                temperature=0.1
            )
            
            if test_result['success']:
                return {
                    'status': 'healthy',
                    'api_accessible': True,
                    'model': test_result['model'],
                    'response_time_ms': 0,  # TODO: measure actual time
                    'test_response': test_result['text'][:50]
                }
            else:
                return {
                    'status': 'unhealthy',
                    'api_accessible': False,
                    'error': test_result['error']
                }
                
        except Exception as e:
            logger.error("Błąd sprawdzania zdrowia API", error=str(e))
            return {
                'status': 'error',
                'api_accessible': False,
                'error': str(e)
            }