# llm/llm_interface.py
from abc import ABC, abstractmethod
from typing import Optional

class LLMInterface(ABC):
    

    @abstractmethod
    def generate_response(self, prompt: str, max_tokens: Optional[int] = 150) -> str:
        
        pass


