from sqlalchemy import create_engine, text
from config.settings import recommendation_db_url

engine = create_engine(recommendation_db_url)

with engine.connect() as conn:
    for user_id in range(10):
        user_id += 1
        result = conn.execute(
            text("SELECT recommended_isbns FROM user_recommendations WHERE user_id = :user_id"),
            {"user_id": user_id}
        ).fetchone()
        
        if result:
            recommended_isbns = result[0]  # This will be a Python list (TEXT[] in Postgres)
            print(f"Recommendations for user {user_id}: {recommended_isbns}")
        else:
            print(f"No recommendations found for user {user_id}")

with engine.connect() as conn:
    isbn = "1234567890"
    result = conn.execute(
        text("SELECT similar_isbns FROM book_similarities WHERE isbn = :isbn"),
        {"isbn": isbn}
    ).fetchone()
    
    if result:
        similar_isbns = result[0]  # Python list
        print(f"Books similar to {isbn}: {similar_isbns}")
    else:
        print(f"No similar books found for {isbn}")
