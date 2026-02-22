from sentence_transformers import SentenceTransformer
from src.config import EMBEDDING_MODEL
import numpy as np

print("Loading embedding model...")
model = SentenceTransformer(EMBEDDING_MODEL)
print("Embedding model loaded.")


def embed(text: str):

    vec = model.encode(text)

    vec = vec / np.linalg.norm(vec)

    return vec.tolist()