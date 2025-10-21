"""LLM client for Qwen/llama-server integration."""
import requests
from typing import Optional


class ModelUnavailableError(Exception):
    """Exception raised when LLM model is not available."""
    pass


class LLMClient:
    """Client for llama-server HTTP API (Qwen model).
    
    Provides two main functions:
    1. suggest_location: Suggests folder location for new notes
    2. interpret_natural_language: Converts natural language to slash commands
    """
    
    def __init__(self, endpoint: str = "http://localhost:8080", timeout: int = 10):
        """Initialize LLM client.
        
        Args:
            endpoint: Base URL for llama-server (default: localhost:8080)
            timeout: Request timeout in seconds
        """
        self.endpoint = f"{endpoint}/v1/chat/completions"
        self.timeout = timeout
    
    def suggest_location(self, title: str, content: str) -> str:
        """Suggest folder location for new note using LLM.
        
        Args:
            title: Note title
            content: Note content
        
        Returns:
            Suggested folder path (e.g., "Engineering/")
        """
        system_prompt = """You are a note organization assistant. 
Based on the note title and content, suggest the best folder location.
Respond with ONLY the folder path ending with /, like "Engineering/" or "Projects/".
If unsure, respond with "Notes/"."""
        
        user_prompt = f"Title: {title}\nContent: {content}\n\nSuggested folder:"
        
        try:
            response = self._call_model(
                system=system_prompt,
                user=user_prompt,
                temperature=0.3
            )
            
            # Clean up response
            location = response.strip()
            if not location.endswith("/"):
                location += "/"
            
            return location
            
        except ModelUnavailableError:
            # Fallback to default
            return "Notes/"
        except Exception:
            # Any other error, use default
            return "Notes/"
    
    def interpret_natural_language(self, user_input: str) -> str:
        """Convert natural language to slash command.
        
        Args:
            user_input: Natural language query
        
        Returns:
            Slash command string (e.g., "/rag testing")
        
        Raises:
            ModelUnavailableError: If LLM not available
        """
        system_prompt = """You are a command interpreter for an Obsidian vault assistant.
Convert natural language queries to slash commands:

Commands:
- /rag <query> - Search notes
- /daily <note> - Add to daily note
- /note <title> <content> - Create note
- /open <path> - Open note

Respond with ONLY the slash command, nothing else."""
        
        user_prompt = f"Query: {user_input}\n\nCommand:"
        
        return self._call_model(
            system=system_prompt,
            user=user_prompt,
            temperature=0.2
        )
    
    def _call_model(self, system: str, user: str, temperature: float) -> str:
        """Call Qwen model via llama-server HTTP API.
        
        Args:
            system: System prompt
            user: User prompt
            temperature: Sampling temperature
        
        Returns:
            Model response text
        
        Raises:
            ModelUnavailableError: If llama-server not responding
        """
        try:
            response = requests.post(
                self.endpoint,
                json={
                    "model": "qwen",
                    "messages": [
                        {"role": "system", "content": system},
                        {"role": "user", "content": user}
                    ],
                    "temperature": temperature,
                    "max_tokens": 100
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            # Extract content from OpenAI-compatible response
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except (requests.Timeout, requests.ConnectionError) as e:
            raise ModelUnavailableError(
                "Local model not responding. "
                "Start llama-server with: llama-server --model qwen --port 8080"
            )
        except Exception as e:
            raise ModelUnavailableError(f"LLM call failed: {str(e)}")
