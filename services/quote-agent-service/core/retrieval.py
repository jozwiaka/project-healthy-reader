from sqlalchemy import text
from app.db import SessionLocal

def search_quotes(query_embedding, top_k: int = 3):
    sql = text("""
        SELECT id, text, author, tags, source,
               embedding <-> :embedding AS distance
        FROM quotes
        ORDER BY distance ASC
        LIMIT :top_k
    """)
    with SessionLocal() as db:
        rows = db.execute(sql, {"embedding": query_embedding, "top_k": top_k}).fetchall()
    return [dict(r._mapping) for r in rows]

def keyword_search(keyword: str, top_k: int = 5):
    sql = text("""
        SELECT id, text, author, tags, source
        FROM quotes
        WHERE text ILIKE :kw OR :kw = ANY(tags)
        LIMIT :top_k
    """)
    with SessionLocal() as db:
        rows = db.execute(sql, {"kw": f"%{keyword}%", "top_k": top_k}).fetchall()
    return [dict(r._mapping) for r in rows]
