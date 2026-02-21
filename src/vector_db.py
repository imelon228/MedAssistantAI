import psycopg2
from src.embeddings import embed

conn = psycopg2.connect(
    host="localhost",
    port=5433,
    database="medical_ai",
    user="postgres",
    password="postgres"
)

def search_protocols(symptoms):

    vector = embed(symptoms)

    cursor = conn.cursor()

    cursor.execute("""
        SELECT p.protocol_id, p.title, p.icd10_code, p.text
        FROM embeddings e
        JOIN protocols p ON e.protocol_id = p.protocol_id
        ORDER BY e.embedding <-> %s
        LIMIT 3
    """, (vector,))

    results = cursor.fetchall()

    return [
        {
            "protocol_id": r[0],
            "title": r[1],
            "icd_code": r[2],
            "text": r[3]
        }
        for r in results
    ]