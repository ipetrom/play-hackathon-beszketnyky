"""
LLM service for Scaleway Qwen3 integration
"""

import openai
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from .config import settings

logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM operations using Scaleway Qwen3"""
    
    def __init__(self):
        self.api_key = settings.scaleway_api_key
        self.project_id = settings.scaleway_project_id
        self.base_url = settings.scaleway_base_url
        self.model = settings.scaleway_model
        self.temperature = settings.scaleway_temperature
        
        # Initialize OpenAI client with Scaleway endpoint
        self.client = openai.OpenAI(
            base_url=self.base_url,
            api_key=self.api_key
        )
    
    async def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """Generate response using Scaleway Qwen3"""
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            # Use OpenAI client with Scaleway endpoint
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=4000,
                temperature=self.temperature,
                top_p=0.8,
                presence_penalty=0,
                stream=False
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"Scaleway LLM generation failed: {e}")
            raise
    
    async def generate_structured_response(self, prompt: str, system_prompt: str, schema: Dict[str, Any]) -> Dict[str, Any]:
        """Generate structured response with JSON schema using Scaleway Qwen3"""
        try:
            structured_prompt = f"""{prompt}

Please respond with a valid JSON object following this schema:
{json.dumps(schema, indent=2)}

Ensure your response is valid JSON and follows the schema exactly."""
            
            response = await self.generate_response(structured_prompt, system_prompt)
            
            # Try to parse JSON response
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                # If JSON parsing fails, return the raw response
                logger.warning("Failed to parse JSON response from Scaleway Qwen3, returning raw text")
                return {"raw_response": response}
                
        except Exception as e:
            logger.error(f"Structured Scaleway LLM generation failed: {e}")
            raise

# Global LLM service instance
llm_service = LLMService()
