
import os

ENV = os.getenv("ENV", "development")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


EMBEDDING_MODEL = "text-embedding-3-small"

CHAT_MODEL = "gpt-4o-mini"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DATA_PATH = os.path.join(BASE_DIR, "scriptsmsg/raw/messages.json")
PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "scriptsmsg/processed/chunks.json")
FAISS_INDEX_PATH = os.path.join(BASE_DIR, "scriptsmsg/embeddings/faiss_index.bin")

LOG_PATH = os.path.join(BASE_DIR, "logs/conversations.log")

CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
TOP_K_RESULTS = 5

LLM_PROVIDER = "openai"  


LOCAL_MODEL_NAME = "microsoft/phi-2"
LOCAL_MODEL_DEVICE = "cuda"  
LOCAL_MODEL_MAX_TOKENS = 512
