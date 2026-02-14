# memory/session_store.py
import time
from typing import Dict, List

class SessionStore:
    

    def __init__(self, max_messages: int = 20, session_timeout: int = 3600):
        
        self.max_messages = max_messages
        self.session_timeout = session_timeout
        self.sessions: Dict[str, Dict] = {}  

    def add_message(self, user_id: str, role: str, message: str):
        
        now = time.time()
        if user_id not in self.sessions:
            self.sessions[user_id] = {"messages": [], "last_active": now}

        
        self.sessions[user_id]["last_active"] = now

        # Add message
        self.sessions[user_id]["messages"].append({"role": role, "message": message})

        # Keep only last N messages
        self.sessions[user_id]["messages"] = self.sessions[user_id]["messages"][-self.max_messages:]

    def get_messages(self, user_id: str) -> List[Dict]:
        
        self.expire_sessions()
        if user_id in self.sessions:
            return self.sessions[user_id]["messages"]
        return []

    def expire_sessions(self):
        
        now = time.time()
        expired_users = [
            user_id for user_id, session in self.sessions.items()
            if now - session["last_active"] > self.session_timeout
        ]
        for user_id in expired_users:
            del self.sessions[user_id]

