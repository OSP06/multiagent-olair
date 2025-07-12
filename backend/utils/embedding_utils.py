# utils/embedding_utils.py
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")

def get_embedding(text: str):
    return model.encode(text, convert_to_numpy=True).tolist()

def get_embeddings(texts):
    return [get_embedding(t) for t in texts]
