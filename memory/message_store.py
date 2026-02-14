# memory/message_store.py
import json
import os
from datetime import datetime
from typing import List, Dict, Optional

class MessageStore:
    

    def __init__(self, storage_path: str = "scriptsmsg/raw/messages.json"):
        self.storage_path = storage_path
        self.messages: List[Dict] = []

        # Load existing messages if file exists
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r", encoding="utf-8") as f:
                try:
                    self.messages = json.load(f)
                except json.JSONDecodeError:
                    print(f" Warning: {self.storage_path} is empty or invalid. Starting fresh.")

    def add_message(
        self,
        user_id: str,
        user_message: str,
        retrieved_chunk_ids: Optional[List[int]] = None,
        model_response: Optional[str] = None,
        model_used: Optional[str] = None
    ):
        """
        Store a new message entry
        """
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "user_id": user_id,
            "user_message": user_message,
            "retrieved_chunk_ids": retrieved_chunk_ids or [],
            "model_response": model_response or "",
            "model_used": model_used or "unknown"
        }

        self.messages.append(entry)
        self._save()

    def _save(self):
        
        os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
        with open(self.storage_path, "w", encoding="utf-8") as f:
            json.dump(self.messages, f, indent=2, ensure_ascii=False)

    def get_messages(self, user_id: Optional[str] = None) -> List[Dict]:
        
        if user_id:
            return [msg for msg in self.messages if msg["user_id"] == user_id]
        return self.messages


