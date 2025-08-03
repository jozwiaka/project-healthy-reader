from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "postgresql://user:password@quote-db:5432/quotes"

engine = create_engine(DATABASE_URL)
from python_common.config.db import recommendation_engine

SessionLocal = sessionmaker(bind=recommendation_engine, autoflush=False, autocommit=False)
Base = declarative_base()
