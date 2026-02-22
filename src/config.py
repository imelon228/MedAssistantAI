import os
from dotenv import load_dotenv

# load .env if exists
load_dotenv()

# ======================
# LLM CONFIG
# ======================

LLM_API_KEY = os.getenv("LLM_API_KEY", "")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "")
LLM_MODEL = os.getenv("LLM_MODEL", "")

# ======================
# DATABASE CONFIG
# ======================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5433"))
DB_NAME = os.getenv("DB_NAME", "medical_ai")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "postgres")

# ======================
# RETRIEVAL CONFIG
# ======================

TOP_K = int(os.getenv("TOP_K", "10"))

# CRITICAL: must match ingest.py EXACTLY
EMBEDDING_MODEL = os.getenv(
    "EMBEDDING_MODEL",
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# ======================
# WARNINGS
# ======================

if not LLM_API_KEY:
    print("WARNING: LLM_API_KEY not set")

if not LLM_BASE_URL:
    print("WARNING: LLM_BASE_URL not set")

if not LLM_MODEL:
    print("WARNING: LLM_MODEL not set")