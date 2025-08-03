from fastapi import APIRouter, HTTPException
from sqlalchemy import text
import pandas as pd
from python_common.config.db import recommendation_engine

router = APIRouter()

@router.get("/user/{user_id}")
def recommend_for_user(user_id: int):
    query = text("SELECT recommended_isbns FROM user_recommendations WHERE user_id = :user_id")
    result = recommendation_engine.execute(query, {"user_id": user_id}).fetchone()

    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="Recommendations not found for user")

    recommended_isbns = result[0]  # This is already a list because of TEXT[]

    placeholders = ','.join(['%s'] * len(recommended_isbns))
    books_query = text(f"SELECT * FROM books WHERE isbn IN ({placeholders})")
    books = pd.read_sql(books_query, recommendation_engine, params=recommended_isbns)

    return books.to_dict(orient="records")


@router.get("/book/{isbn}")
def recommend_similar_books(isbn: str):
    query = text("SELECT similar_isbns FROM book_similarities WHERE isbn = :isbn")
    result = recommendation_engine.execute(query, {"isbn": isbn}).fetchone()

    if not result or not result[0]:
        raise HTTPException(status_code=404, detail="Similar books not found")

    similar_isbns = result[0]  # Already a list

    placeholders = ','.join(['%s'] * len(similar_isbns))
    books_query = text(f"SELECT * FROM books WHERE isbn IN ({placeholders})")
    books = pd.read_sql(books_query, recommendation_engine, params=similar_isbns)

    return books.to_dict(orient="records")
