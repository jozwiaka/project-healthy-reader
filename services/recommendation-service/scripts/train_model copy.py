import os
import pickle
import pandas as pd
from sqlalchemy import create_engine, text
from scipy.sparse import coo_matrix
import implicit
from config.settings import user_db_url, book_db_url, rating_db_url, recommendation_db_url

os.environ["OPENBLAS_NUM_THREADS"] = "1"

# Load data
users = pd.read_sql("SELECT * FROM users", create_engine(user_db_url))
books = pd.read_sql("SELECT * FROM books", create_engine(book_db_url))
ratings = pd.read_sql("SELECT * FROM ratings", create_engine(rating_db_url))
print("Connected do databases")

dataset = ratings.merge(users, left_on='user_id', right_on='id') \
                 .merge(books, on='isbn')

user_ids = {int(u): int(i) for i, u in enumerate(dataset['user_id'].unique())}
book_ids = {str(b): int(i) for i, b in enumerate(dataset['isbn'].unique())}
inv_user_ids = {i: u for u, i in user_ids.items()}
inv_book_ids = {i: b for b, i in book_ids.items()}

dataset['user_index'] = dataset['user_id'].map(user_ids)
dataset['book_index'] = dataset['isbn'].map(book_ids)

ratings_matrix = coo_matrix(
    (dataset['rating'], (dataset['user_index'], dataset['book_index']))
)

implicit_matrix = (ratings_matrix >= 6).astype(float).tocsr()

model = implicit.als.AlternatingLeastSquares(
    factors=50, regularization=0.01, iterations=20, use_gpu=False
)
model.fit(implicit_matrix)

# Store top recommendations in database
engine = create_engine(recommendation_db_url)
conn = engine.connect()

conn.execute(text("DELETE FROM user_recommendations"))
conn.execute(text("DELETE FROM book_similarities"))

# Insert user recommendations as arrays
for uid, uidx in user_ids.items():
    user_vector = implicit_matrix.getrow(uidx)
    recommended = model.recommend(uidx, user_vector, N=10)
    recommended_isbns = [
        str(inv_book_ids[rec[0]])
        for rec in recommended
        if rec[0] in inv_book_ids
    ]
    
    conn.execute(
        text("INSERT INTO user_recommendations (user_id, recommended_isbns) VALUES (:user_id, :recommended_isbns)"),
        {
            "user_id": int(uid),
            "recommended_isbns": recommended_isbns  # SQLAlchemy will map this to a PostgreSQL TEXT[]
        }
    )
    
    print(f"user-{int(uid)}: {recommended_isbns}")

# Insert similar books as arrays
for bidx, bid in inv_book_ids.items():
    similar_ids, similar_scores = model.similar_items(bidx, N=10)
    similar_isbns = [
        str(inv_book_ids[sid])
        for sid in similar_ids
        if sid != bidx
    ]
    
    conn.execute(
        text("INSERT INTO book_similarities (isbn, similar_isbns) VALUES (:isbn, :similar_isbns)"),
        {
            "isbn": str(bid),
            "similar_isbns": similar_isbns
        }
    )
    
    print(f"isbn-{int(uid)}: {similar_isbns}")
    

print("✅ Recommendations saved to database")

os.makedirs("models", exist_ok=True)
with open("models/model.pkl", "wb") as f:
    pickle.dump({"model": model, "user_ids": user_ids, "book_ids": book_ids}, f)

print("💾 Model saved to models/model.pkl")