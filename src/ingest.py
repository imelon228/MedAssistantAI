import json
import psycopg2
from sentence_transformers import SentenceTransformer
from tqdm import tqdm
import re
import numpy as np


# ======================
# CHUNKING
# ======================

def chunk_text(text, chunk_size=1200, overlap=200):
    chunks = []
    start = 0

    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        chunks.append(chunk)
        start += chunk_size - overlap

    return chunks


# ======================
# DATABASE CONNECTION
# ======================

print("Connecting to database...")

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="medical_ai",
    user="postgres",
    password="postgres"
)

cursor = conn.cursor()

print("Connected to PostgreSQL.")


# ======================
# LOAD EMBEDDING MODEL
# ======================

print("Loading embedding model...")
model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("Embedding model loaded.")


# ======================
# SAFE TEXT CLEANING
# ======================

def safe_clean(text):

    if not text:
        return ""

    text = str(text)
    text = text.replace("\x00", " ")
    text = text.encode("utf-8", "ignore").decode("utf-8", "ignore")

    garbage_patterns = [
        r"Одобрено.*?Протокол №\d+",
        r"Рекомендовано.*?протокол №\d+",
        r"Министерство здравоохранения.*",
        r"Республики Казахстан.*",
        r"Экспертным советом.*",
    ]

    for pattern in garbage_patterns:
        text = re.sub(pattern, " ", text, flags=re.IGNORECASE | re.DOTALL)

    text = re.sub(r"\s+", " ", text).strip()

    return text


# ======================
# LOAD CORPUS
# ======================

CORPUS_FILE = "data/corpus/protocols_corpus.jsonl"

protocols = []

with open(CORPUS_FILE, "r", encoding="utf-8") as f:
    for line in f:
        protocols.append(json.loads(line))

print(f"Found {len(protocols)} corpus protocols.")


# ======================
# CLEAR OLD DATA
# ======================

print("Clearing old embeddings...")

cursor.execute("DELETE FROM embeddings")
cursor.execute("DELETE FROM protocols")

conn.commit()

print("Old data cleared.")


# ======================
# INGEST LOOP (CHUNKED)
# ======================

for protocol in tqdm(protocols):

    try:
        protocol_id = safe_clean(protocol.get("protocol_id", ""))
        title = safe_clean(protocol.get("title", ""))
        text = safe_clean(protocol.get("text", ""))
        icd_code = safe_clean(protocol.get("icd_codes", ""))

        # сохраняем сам протокол (1 раз)
        cursor.execute(
            """
            INSERT INTO protocols (protocol_id, title, icd10_code, text)
            VALUES (%s, %s, %s, %s)
            """,
            (protocol_id, title, str(icd_code), text)
        )

        # делаем chunking
        chunks = chunk_text(text)

        for chunk in chunks:

            # добавляем контекст диагноза в каждый chunk
            embedding_input = f"""
            Diagnosis: {title}
            ICD10: {icd_code}
            {chunk}
            """

            embedding = model.encode(embedding_input)
            embedding = embedding / np.linalg.norm(embedding)
            embedding = embedding.tolist()

            cursor.execute(
                """
                INSERT INTO embeddings (protocol_id, chunk_text, embedding)
                VALUES (%s, %s, %s)
                """,
                (protocol_id, chunk, embedding)
            )

    except Exception as e:
        print(f"Error processing protocol {protocol.get('protocol_id')}: {e}")


# ======================
# FINALIZE
# ======================

conn.commit()
cursor.close()
conn.close()

print("Embeddings successfully rebuilt with chunking.")