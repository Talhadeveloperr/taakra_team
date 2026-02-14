#core/prompt_builder.py
import os
from typing import List, Optional, Dict

class PromptBuilder:
    def __init__(self, system_prompt_path: str, style_prompt_path: str):
        print(f" Initializing PromptBuilder...")
        if not os.path.exists(system_prompt_path):
            raise FileNotFoundError(f"System prompt not found at {system_prompt_path}")
        if not os.path.exists(style_prompt_path):
            raise FileNotFoundError(f"Style prompt not found at {style_prompt_path}")

        self.system_prompt = self._load_file(system_prompt_path)
        self.style_prompt = self._load_file(style_prompt_path)
        
        # Warning if files are empty
        if not self.system_prompt:
            print(" Warning: system_prompt.txt is empty!")
        if not self.style_prompt:
            print(" Warning: whatsapp_style.txt is empty!")

    def _load_file(self, path: str) -> str:
        with open(path, "r", encoding="utf-8") as f:
            content = f.read().strip()
            return content

    def build_prompt(
        self,
        user_message: str,
        retrieved_chunks: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        context_text = ""
        if retrieved_chunks:
            context_text = "\n".join(
                f"- {chunk.get('question', '')}: {chunk.get('source', '')}"
                for chunk in retrieved_chunks
            )

        history_text = ""
        if conversation_history:
            history_lines = []
            for entry in conversation_history:
                role = entry.get("role", "user")
                msg = entry.get("message", "")
                history_lines.append(f"{role.title()}: {msg}")
            history_text = "\n".join(history_lines)

        prompt = (
            f"=== SYSTEM ===\n{self.system_prompt}\n\n"
            f"=== STYLE ===\n{self.style_prompt}\n\n"
            f"=== CONTEXT ===\n{context_text}\n\n"
            f"=== HISTORY ===\n{history_text}\n\n"
            f"=== USER ===\n{user_message}\n\n"
            f"=== RESPONSE ==="
        )
        return prompt

