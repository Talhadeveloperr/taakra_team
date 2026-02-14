# core/conversation_manager.py
import os
from core.intent_manager import IntentManager
from core.prompt_builder import PromptBuilder
from rag.retriever import Retriever
from llm.openai_client import OpenAIClient
from memory.session_store import SessionStore
from memory.message_store import MessageStore

class ConversationManager:
    def __init__(self):
        # 1. Core components
        self.intent_manager = IntentManager()
        BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

        # 2. Define Absolute Paths
        index_path = r"D:\projects\taakra hackathon\chatbot\flask_server\scriptsmsg\embeddings\faiss_index.bin"
        meta_path = r"D:\projects\taakra hackathon\chatbot\flask_server\scriptsmsg\processed\chunks.json"

        # --- DEBUG PRINTS ---
        print("\n" + "="*50)
        print("RETRIEVER INITIALIZATION")
        print(f"Loading Index from: {index_path}")
        print(f"Loading Metadata from: {meta_path}")
        print(f"Index File Exists: {os.path.exists(index_path)}")
        print(f"Metadata File Exists: {os.path.exists(meta_path)}")
        print("="*50 + "\n")

        # 3. Initialize Retriever with absolute paths
        self.retriever = Retriever(
            vector_index_path=index_path,
            metadata_path=meta_path
        )

        self.prompt_builder = PromptBuilder(
            system_prompt_path=os.path.join(BASE_DIR, "prompts", "system_prompt.txt"),
            style_prompt_path=os.path.join(BASE_DIR, "prompts", "whatsapp_style.txt")
        )

        self.llm = OpenAIClient()
        self.session_store = SessionStore()
        self.message_store = MessageStore()

    def handle_message(self, user_id: str, user_message: str) -> str:
        history = self.session_store.get_messages(user_id)

        # Detect intent
        
        use_rag = self.intent_manager.should_use_rag(user_message)
        
        # --- DEBUG PRINT ---
        print(f"User Message: {user_message}")
        print(f"Should use RAG: {use_rag}")

        retrieved_chunks = []
        if use_rag:
            retrieved_chunks = self.retriever.retrieve(user_message, top_k=3)
            # --- DEBUG PRINT ---
            print(f"Chunks retrieved: {len(retrieved_chunks)}")

        prompt = self.prompt_builder.build_prompt(
            user_message=user_message,
            retrieved_chunks=retrieved_chunks,
            conversation_history=history
        )

        response = self.llm.generate_response(prompt)

        self.session_store.add_message(user_id, "user", user_message)
        self.session_store.add_message(user_id, "assistant", response)

        chunk_ids = [c.get("chunk_id") for c in retrieved_chunks]
        self.message_store.add_message(
            user_id=user_id,
            user_message=user_message,
            retrieved_chunk_ids=chunk_ids,
            model_response=response,
            model_used="gpt-oss-120b"
        )

        return response