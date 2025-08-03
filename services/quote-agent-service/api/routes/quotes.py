from fastapi import APIRouter, Query
from app.core.retrieval import keyword_search
from app.models.schemas import Quote
from typing import List

router = APIRouter()

@router.get("/search", response_model=List[Quote])
def search_quotes(keyword: str = Query(..., min_length=2)):
    return keyword_search(keyword)
