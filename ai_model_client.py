"""
AI Model Client for Mock API Generator

This module provides a base class for interacting with AI models to generate code.
It includes two concrete implementations:
1. GroqModelClient - for interacting with Groq API

"""

from abc import ABC, abstractmethod
import os
from typing import Optional
import dotenv
from groq import Groq


class AiModelClient(ABC):
    """Abstract base class for AI model clients"""
    
    @abstractmethod
    def generate_code(self, prompt: str, model: str = "default", max_tokens: int = 2000, temperature: float = 0.7) -> str:
        """
        Generate code using an AI model
        
        Args:
            prompt: The prompt to send to the AI model
            model: The AI model to use
            max_tokens: Maximum number of tokens in the response
            temperature: Controls randomness (0-1)
            
        Returns:
            Generated code as a string
        """
        pass

class GroqAiModelClient(AiModelClient):
    """Client for interacting with Groq API to generate code"""
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize the OpenAI model client"""
        self.api_key = api_key or os.getenv("GROQ_API_KEY") or dotenv.get_key(".env", "GROQ_API_KEY")
        if not self.api_key:
            raise ValueError("API key is required for OpenAI API access")
        self.client = Groq(api_key=self.api_key)
    
    def generate_code(self, prompt: str, model: str = "llama3-70b-8192", max_tokens: int = 4096, temperature: float = 0.6) -> str:
        """Generate code using the OpenAI API
        
        Args:
            prompt: The prompt to send to the AI model
            model: The OpenAI model to use (e.g., gpt-3.5-turbo, gpt-4)
            max_tokens: Maximum number of tokens in the response
            temperature: Controls randomness (0-1)
            
        Returns:
            Generated code as a string
        """
        try:
            system_prompt = "Generate code only, no explanations or markdown formatting."
            completion = self.client.chat.completions.create(
                model=model,
                messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.95,
                stop=None,
            )            
            
            return completion.choices[0].message.content
        
        except Exception as e:
            raise RuntimeError(f"Groq code generation failed: {str(e)}")
