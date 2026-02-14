# user/model/llm.py

import os
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLM:

    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set.")

        self.client = Groq(api_key=api_key)
        self.model_name = "openai/gpt-oss-120b"

    def generate(self, user_message: str, previous_messages: list, system_prompt: str = None):

        try:
            messages = []

            # System first
            if system_prompt:
                messages.append({
                    "role": "system",
                    "content": system_prompt
                })

            # Previous chat
            for msg in previous_messages:
                messages.append({
                    "role": "user",
                    "content": msg["user_message"]
                })

                if msg.get("model_response"):
                    messages.append({
                        "role": "assistant",
                        "content": msg["model_response"]
                    })

            # Current message
            messages.append({
                "role": "user",
                "content": user_message
            })

            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                temperature=0.3,
                max_completion_tokens=1024,
                stream=True
            )

            full_response = ""

            for chunk in completion:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta.content
                    if delta:
                        full_response += delta

            return full_response.strip(), self.model_name

        except Exception as e:
            raise RuntimeError(f"LLM generation failed: {str(e)}")