#scraping/model.py
import os
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

class GroqModel:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set in .env file.")
        self.client = Groq(api_key=api_key)

    def get_response(self, prompt: str) -> str:
        """Sends prompt to model and returns the full response string."""
        completion = self.client.chat.completions.create(
            model="openai/gpt-oss-120b",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7, # Lower temperature for more consistent formatting
            max_completion_tokens=1024,
            stream=True,
        )

        full_response = ""
        for chunk in completion:
            content = chunk.choices[0].delta.content or ""
            full_response += content
        
        return full_response

    def extract_content(self, text: str) -> str:
        """Uses regex to find content between ` ` symbols."""
        # This matches anything inside ` {content} `
        match = re.search(r'`\s*\{(.*?)\}\s*`', text, re.DOTALL)
        if match:
            return match.group(1).strip()
        # Fallback if the model forgot the curly braces but kept the backticks
        match_simple = re.search(r'`(.*?)`', text, re.DOTALL)
        return match_simple.group(1).strip() if match_simple else text.strip()