# llm/openai_client.py
import os
from typing import Optional
from llm.llm_interface import LLMInterface
from groq import Groq
from dotenv import load_dotenv

class OpenAIClient(LLMInterface):
    

    def __init__(self, model_name: str = "openai/gpt-oss-120b"):
        # Load environment variables (optional .env)
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError(
                "❗️ GROQ_API_KEY not set. "
                "Set it in your environment or in a .env file."
            )

        self.client = Groq(api_key=api_key)
        self.model_name = model_name

    def generate_response(self, prompt: str, max_tokens: Optional[int] = 8192) -> str:
        
        # Prepare chat completion messages
        messages = [{"role": "user", "content": prompt}]

        # Create completion (streaming)
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            temperature=1,
            max_completion_tokens=max_tokens,
            top_p=1,
            reasoning_effort="medium",
            stream=True,
            stop=None,
        )

        # Collect response text
        full_response = ""
        for chunk in completion:
            delta = chunk.choices[0].delta.content
            if delta:
                full_response += delta

        # Return cleaned response
        return full_response.strip()


