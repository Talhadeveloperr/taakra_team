# user/conversation_manag.py

from user.session_manager import SessionManager
from user.model.llm import LLM
from user.database.main import DatabaseManager
from rag.retriever import Retriever
import os
import json


class ConversationManag:

    def __init__(self):
        self.session_manager = SessionManager()
        self.llm = LLM()
        self.db_manager = DatabaseManager()

        # 🔥 Load embeddings once
        vector_path = os.path.join("scriptsmsg", "embeddings", "faiss_index.bin")
        metadata_path = os.path.join("scriptsmsg", "processed", "chunks.json")

        self.retriever = Retriever(
            vector_index_path=vector_path,
            metadata_path=metadata_path
        )

    def handle_message(self, user_id, user_message, user_uuid):

        if not user_uuid:
            raise ValueError("UUID is required")

        print("UUID:", user_uuid)
        print("User Message:", user_message)

        # Session (unchanged)
        self.session_manager.create_if_not_exists(user_uuid)
        last_messages = self.session_manager.get_last_messages(user_uuid, limit=5)

        # 🔥 Fetch user-specific database data
        db_context = self.db_manager.build_database_context(user_uuid)
        db_context_text = json.dumps(db_context, indent=2)

        # 🔥 Retrieve relevant embeddings
        retrieved_chunks = self.retriever.retrieve(user_message, top_k=3)

        rag_context = []
        for chunk in retrieved_chunks:
            rag_context.append({
                "question": chunk.get("question"),
                "source": chunk.get("source"),
                "score": chunk.get("score")
            })

        rag_context_text = json.dumps(rag_context, indent=2)

        # 🔥 Combined system prompt
        system_prompt = f"""
You are an intelligent competition assistant.

You have access to:

1️⃣ USER DATA (STRICTLY THIS USER ONLY):
{db_context_text}

2️⃣ KNOWLEDGE BASE (Relevant Retrieved Info):
{rag_context_text}

Rules:
- Use USER DATA for personal questions.
- Use KNOWLEDGE BASE for system/competition info.
- If data missing, say so clearly.
- Never fabricate information.
"""

        response_text, model_used = self.llm.generate(
            user_message=user_message,
            previous_messages=last_messages,
            system_prompt=system_prompt
        )

        # Save session (unchanged)
        self.session_manager.append_entry(
            uuid=user_uuid,
            user_message=user_message,
            model_response=response_text,
            model_used=model_used
        )

        return response_text