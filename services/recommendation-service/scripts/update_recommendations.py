import os
import sys
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
COMMON_DIR = os.path.join(PROJECT_DIR, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)
import pandas as pd
from sqlalchemy import create_engine, text
from scipy.sparse import coo_matrix
from python_common.config.db import book_engine, rating_engine, recommendation_engine
import numpy as np
import pandas as pd
import sklearn
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
from sklearn.neighbors import NearestNeighbors
from scipy.sparse import csr_matrix
import json

books = pd.read_sql("SELECT * FROM books", book_engine)
ratings = pd.read_sql("SELECT * FROM ratings", rating_engine)

isbns = ratings["isbn"].unique()[10:12]
user_ids = ratings["user_id"].unique()[101:103]

conn = recommendation_engine.connect()
conn.execute(text("DELETE FROM user_recommendations"))
conn.execute(text("DELETE FROM book_similarities"))

print("Connected do databases")

def create_matrix(df):
    N = len(df['user_id'].unique())
    M = len(df['isbn'].unique())

    user_mapper = dict(zip(np.unique(df["user_id"]), list(range(N))))
    book_mapper = dict(zip(np.unique(df["isbn"]), list(range(M))))

    user_inv_mapper = dict(zip(list(range(N)), np.unique(df["user_id"])))
    book_inv_mapper = dict(zip(list(range(M)), np.unique(df["isbn"])))

    user_index = [user_mapper[i] for i in df['user_id']]
    book_index = [book_mapper[i] for i in df['isbn']]

    X = csr_matrix((df["rating"], (book_index, user_index)), shape=(M, N))

    return X, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper

X, user_mapper, book_mapper, user_inv_mapper, book_inv_mapper = create_matrix(ratings)

def find_similar_books(isbn, X, k, metric='cosine', show_distance=False):
    neighbour_ids = []

    if isbn not in book_mapper:
        print(f"Movie ID {isbn} not found in book_mapper!")
        return []

    book_ind = book_mapper[isbn]
    book_vec = X[book_ind]
    k += 1 
    kNN = NearestNeighbors(n_neighbors=k, algorithm="brute", metric=metric)
    kNN.fit(X)
    book_vec = book_vec.reshape(1, -1)
    neighbour = kNN.kneighbors(book_vec, return_distance=show_distance)

    for i in range(0, k):
        n = neighbour.item(i)
        neighbour_ids.append(book_inv_mapper[n])

    neighbour_ids.pop(0)
    return neighbour_ids

def recommend_books_for_user(user_id, X, user_mapper, book_mapper, book_inv_mapper, k=10):
    df1 = ratings[ratings['user_id'] == user_id]
    isbn = df1[df1['rating'] == max(df1['rating'])]['isbn'].iloc[0]
    recommended_isbns= find_similar_books(isbn, X, k)

    return recommended_isbns

def recommend_books_for_user_v2(user_id, X, user_mapper, book_mapper, book_inv_mapper, k=10, top_n=10):
    """Improved user recommendation based on weighted aggregation of multiple liked books."""
    if user_id not in user_mapper:
        print(f"User {user_id} not found!")
        return []

    # Get this user's ratings
    user_ratings = ratings[ratings['user_id'] == user_id]
    if user_ratings.empty:
        return []

    # Focus on books rated above a threshold
    high_rated = user_ratings[user_ratings['rating'] >= 4]
    if high_rated.empty:
        high_rated = user_ratings.nlargest(3, 'rating')  # fallback to top 3

    scores = {}
    kNN = NearestNeighbors(n_neighbors=k+1, algorithm="brute", metric='cosine')
    kNN.fit(X)

    for _, row in high_rated.iterrows():
        isbn = row['isbn']
        rating = row['rating']

        if isbn not in book_mapper:
            continue

        book_ind = book_mapper[isbn]
        book_vec = X[book_ind].reshape(1, -1)

        distances, neighbours = kNN.kneighbors(book_vec, return_distance=True)

        for dist, neighbour_idx in zip(distances[0], neighbours[0]):
            sim_isbn = book_inv_mapper[neighbour_idx]
            if sim_isbn == isbn:
                continue  # skip the same book

            # Weighted score: higher rating + closer similarity = higher score
            similarity_score = 1 - dist
            weight = rating * similarity_score
            scores[sim_isbn] = scores.get(sim_isbn, 0) + weight

    # Remove books the user has already rated
    read_books = set(user_ratings['isbn'])
    scores = {isbn: score for isbn, score in scores.items() if isbn not in read_books}

    # Sort by aggregated score
    recommended_isbns = sorted(scores, key=scores.get, reverse=True)[:top_n]

    return recommended_isbns


for isbn in isbns:
    similar_isbns = find_similar_books(isbn, X, 10)
    conn.execute(
        text("INSERT INTO book_similarities (isbn, similar_isbns) VALUES (:isbn, :similar_isbns)"),
        {
            "isbn": isbn,
            "similar_isbns": similar_isbns
        }
    )
    
for user_id in user_ids:
    recommended_isbns = recommend_books_for_user_v2(user_id, X, user_mapper, book_mapper, book_inv_mapper, k=10)
    conn.execute(
        text("INSERT INTO user_recommendations (user_id, recommended_isbns) VALUES (:user_id, :recommended_isbns)"),
        {
            "user_id": int(user_id),
            "recommended_isbns": recommended_isbns
        }
    )
    
conn.commit()

print("TEST:")
recommendations = pd.read_sql("SELECT * FROM user_recommendations", recommendation_engine)
similarities = pd.read_sql("SELECT * FROM book_similarities", recommendation_engine)
print(recommendations.head())
print(similarities.head())
