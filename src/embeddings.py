from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Embedding model loaded.")

def embed(text: str):
    return model.encode(text).tolist()