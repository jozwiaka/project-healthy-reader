from app.core.embeddings import encode_text
from app.core.retrieval import search_quotes

class QuoteAgent:
    def answer(self, user_message: str):
        query_embedding = encode_text(user_message)
        results = search_quotes(query_embedding, top_k=3)

        if not results:
            return {"response": "❌ Sorry, I couldn't find a matching quote."}

        best = results[0]
        return {
            "response": f"💡 {best['text']} — {best['author'] or 'Unknown'}",
            "metadata": {
                "tags": best.get("tags"),
                "source": best.get("source")
            }
        }

agent = QuoteAgent()
