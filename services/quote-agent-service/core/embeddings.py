from sentence_transformers import SentenceTransformer
import numpy as np

# Load embedding model once at startup
model = SentenceTransformer("all-MiniLM-L6-v2")

def encode_text(text: str) -> list[float]:
    """Convert text into a dense vector embedding"""
    return model.encode(text).tolist()

def cosine_similarity(vec1, vec2):
    """Fallback cosine similarity if needed"""
    v1, v2 = np.array(vec1), np.array(vec2)
    return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
