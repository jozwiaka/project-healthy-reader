from config.settings import recommendation_db_url
from sqlalchemy import create_engine

engine = create_engine(recommendation_db_url)
