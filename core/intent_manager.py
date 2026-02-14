# core/intent_manager.py

from typing import Literal
import re

class IntentManager:
    
    def __init__(self):
        # Basic regex patterns
        self.greeting_pattern = re.compile(r"\b(hi|hello|hey|good morning|good afternoon|good evening)\b", re.I)
        self.cloudpos_keywords = [
            "who made", "what is", "features", "user management",
            "dashboard"
        ]
        self.follow_up_pattern = re.compile(r"\b(okay|thanks|thank you|got it|👍|ok)\b", re.I)

    def classify_intent(self, message: str) -> Literal["greeting", "query", "follow_up", "unknown"]:
        message = message.strip().lower()

        if not message:
            return "unknown"

        # Greeting check
        if self.greeting_pattern.search(message):
            return "greeting"

        # Follow-up check
        if self.follow_up_pattern.search(message):
            return "follow_up"

        # CloudPOS query check (simple keyword match)
        if any(keyword in message for keyword in self.cloudpos_keywords):
            return "query"

        return "unknown"

    def should_use_rag(self, message: str) -> bool:
        """
        FORCE ALWAYS TRUE: This ensures FAISS / RAG is always triggered
        regardless of the message content.
        """
        return True


