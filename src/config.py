import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = str(ROOT_DIR / "chroma_db")
COLLECTION_NAME = "indian_legal_docs"

DATASET_NAME = "ninadn/indian-legal"
DATASET_SPLIT = "train"
MAX_DOCS = int(os.getenv("MAX_DOCS", "300"))

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100

EMBEDDING_MODEL = "all-MiniLM-L6-v2"

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemma-4-26b-a4b-it")

TOP_K = 4
