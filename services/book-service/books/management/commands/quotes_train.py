from fastapi import FastAPI, Query
from sentence_transformers import SentenceTransformer, util
import json
import torch

# Load dataset
with open("quotes.json", "r", encoding="utf-8") as f:
    quotes = json.load(f)

# Precompute embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
quote_texts = [q["quote"] for q in quotes]
quote_embeddings = model.encode(quote_texts, convert_to_tensor=True)

# Create FastAPI app
app = FastAPI(title="Quote Agent API")

@app.get("/quote")
async def get_quote(query: str = Query(..., description="Search prompt")):
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.pytorch_cos_sim(query_embedding, quote_embeddings)[0]
    best_idx = torch.argmax(similarities).item()
    best_quote = quotes[best_idx]

    return {
        "query": query,
        "best_match": best_quote,
        "similarity": float(similarities[best_idx])
    }
