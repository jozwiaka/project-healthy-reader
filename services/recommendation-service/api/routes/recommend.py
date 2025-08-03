# routers/recommendations.py
import os
import asyncio
from fastapi import APIRouter, HTTPException
from sqlalchemy import text
from starlette.concurrency import run_in_threadpool
import httpx

from db.db import recommendation_engine

router = APIRouter()

conn = recommendation_engine.connect()

BOOK_URL = os.getenv("BOOK_SERVICE_URL") + os.getenv("BOOK_API_PREFIX")

def _get_user_recommendations_sync(user_id: int):
    query = text("SELECT recommended_isbns FROM user_recommendations WHERE user_id = :user_id")
    result = conn.execute(query, {"user_id": user_id}).fetchone()
    return result[0] if result and result[0] else None


def _get_similar_isbns_sync(isbn: str):
    query = text("SELECT similar_isbns FROM book_similarities WHERE isbn = :isbn")
    result = conn.execute(query, {"isbn": isbn}).fetchone()
    return result[0] if result and result[0] else None


async def fetch_books_from_book_service(isbns: list[str]) -> list[dict]:
    if not isbns:
        return []

    async with httpx.AsyncClient(timeout=10.0) as client:
        tasks = [client.get(f"{BOOK_URL}/{isbn}/") for isbn in isbns] 
        responses = await asyncio.gather(*tasks, return_exceptions=True)

        books = []
        for resp in responses:
            if isinstance(resp, Exception):
                continue
            if resp.status_code == 200:
                try:
                    body = resp.json()
                except Exception:
                    continue
                if isinstance(body, dict) and body.get("isbn"):
                    books.append(body)

        by_isbn = {b["isbn"]: b for b in books}
        return [by_isbn[i] for i in isbns if by_isbn.get(i)]

# --- endpoints ---
@router.get("/user/{user_id}")
async def recommend_for_user(user_id: int):
    recommended_isbns = await run_in_threadpool(_get_user_recommendations_sync, user_id)
    if not recommended_isbns:
        raise HTTPException(status_code=404, detail="Recommendations not found for user")

    books = await fetch_books_from_book_service(recommended_isbns)

    if not books:
        raise HTTPException(status_code=503, detail="Book service unavailable or returned no data")

    return books


@router.get("/book/{isbn}")
async def recommend_similar_books(isbn: str):
    similar_isbns = await run_in_threadpool(_get_similar_isbns_sync, isbn)
    if not similar_isbns:
        raise HTTPException(status_code=404, detail="Similar books not found")
    books = await fetch_books_from_book_service(similar_isbns)

    if not books:
        raise HTTPException(status_code=503, detail="Book service unavailable or returned no data")

    return books
