import os
import sys
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
COMMON_DIR = os.path.join(PROJECT_DIR, "common")
if COMMON_DIR not in sys.path:
    sys.path.insert(0, COMMON_DIR)
from sqlalchemy import create_engine
from python_common.utils.db_urls import recommendation_db_url

recommendation_engine = create_engine(recommendation_db_url)