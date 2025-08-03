from dotenv import load_dotenv
from sqlalchemy import create_engine
import os

RUNNING_IN_DOCKER = os.getenv("RUNNING_IN_DOCKER") == "true"

if not RUNNING_IN_DOCKER:
    from dotenv import load_dotenv
    env_dev_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), 'config/.env.dev')
    load_dotenv(dotenv_path=env_dev_path)

def make_db_url(prefix: str) -> str:
    host = os.getenv(f"{prefix}_DB_HOST") if RUNNING_IN_DOCKER else "localhost"
    port = os.getenv(f"{prefix}_DB_PORT") if RUNNING_IN_DOCKER else os.getenv(f"{prefix}_DB_LOCAL_PORT")
    user = os.getenv(f"{prefix}_DB_USER")
    password = os.getenv(f"{prefix}_DB_PASSWORD")
    name = os.getenv(f"{prefix}_DB_NAME")

    return f"postgresql://{user}:{password}@{host}:{port}/{name}"

user_db_url = make_db_url("USER")
book_db_url = make_db_url("BOOK")
rating_db_url = make_db_url("RATING")
recommendation_db_url = make_db_url("RECOMMENDATION")

# For debug:
# print(user_db_url)
# print(book_db_url)
# print(rating_db_url)
# print(recommendation_db_url)

recommendation_engine = create_engine(recommendation_db_url)
user_engine = create_engine(user_db_url)
book_engine = create_engine(book_db_url)
rating_engine = create_engine(rating_db_url)