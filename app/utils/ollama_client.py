"""Ollama client integration for CarFinder."""
import requests
from typing import Dict, Any, List, Optional

class OllamaClient:
    """Client for interacting with Ollama API."""
    
    def __init__(self, host: str = "http://localhost:11434", model: str = "llama3.1"):
        self.host = host.rstrip('/')
        self.model = model
    
    def is_available(self) -> bool:
        """Check if Ollama is available."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False
    
    def list_models(self) -> List[str]:
        """List available models."""
        try:
            response = requests.get(f"{self.host}/api/tags", timeout=10)
            if response.status_code == 200:
                data = response.json()
                return [model['name'] for model in data.get('models', [])]
            return []
        except requests.RequestException:
            return []
    
    def generate(self, prompt: str, system_prompt: str = "", **kwargs) -> str:
        """Generate text using Ollama."""
        
        # Prepare the full prompt
        if system_prompt:
            full_prompt = f"System: {system_prompt}\n\nHuman: {prompt}\n\nAssistant:"
        else:
            full_prompt = prompt
        
        # Default generation options
        options = {
            'temperature': kwargs.get('temperature', 0.7),
            'top_p': kwargs.get('top_p', 0.9),
            'max_tokens': kwargs.get('max_tokens', 500)
        }
        
        try:
            response = requests.post(
                f"{self.host}/api/generate",
                json={
                    'model': self.model,
                    'prompt': full_prompt,
                    'stream': False,
                    'options': options
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get('response', '')
            else:
                raise Exception(f"Ollama API error: {response.status_code} - {response.text}")
                
        except requests.RequestException as e:
            raise Exception(f"Failed to connect to Ollama: {e}")
    
    def chat(self, messages: List[Dict[str, str]], **kwargs) -> str:
        """Chat interface for conversation."""
        
        # Convert chat messages to a single prompt
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
        
        prompt_parts.append("Assistant:")
        full_prompt = "\n\n".join(prompt_parts)
        
        return self.generate(full_prompt, **kwargs)
    
    def embed(self, text: str) -> List[float]:
        """Generate embeddings (if Ollama supports it)."""
        try:
            response = requests.post(
                f"{self.host}/api/embeddings",
                json={
                    'model': 'nomic-embed-text',  # Default embedding model
                    'prompt': text
                },
                timeout=15
            )
            
            if response.status_code == 200:
                return response.json().get('embedding', [])
            else:
                # Fallback: use sentence transformers
                return []
                
        except requests.RequestException:
            # Fallback: use sentence transformers
            return []

def get_ollama_client(config: Dict[str, Any]) -> OllamaClient:
    """Get configured Ollama client."""
    return OllamaClient(
        host=config.get('ollama_host', 'http://localhost:11434'),
        model=config.get('ollama_model', 'llama3.1')
    )