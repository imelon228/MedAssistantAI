import psycopg2
from src.config import DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD, TOP_K
from src.embeddings import embed

print("Connecting to PostgreSQL...")

conn = psycopg2.connect(
    host=DB_HOST,
    port=DB_PORT,
    database=DB_NAME,
    user=DB_USER,
    password=DB_PASSWORD
)

conn.autocommit = True

print("Connected to PostgreSQL.")

def search_protocols(symptoms: str):

    vector = embed(symptoms)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.protocol_id, p.title, p.icd10_code, p.text
        FROM embeddings e
        JOIN protocols p ON e.protocol_id = p.protocol_id
        ORDER BY e.embedding <-> %s
        LIMIT %s
    """, (vector, TOP_K))

    rows = cursor.fetchall()

    results = []

    for row in rows:
        results.append({
            "protocol_id": row[0],
            "title": row[1],
            "icd_code": row[2],
            "text": row[3],
        })

    return results