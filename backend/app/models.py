from pydantic import BaseModel
from typing import List, Optional, Dict, Any

class SearchQuery(BaseModel):
    query: str
    max_results: Optional[int] = 15
    use_semantic: Optional[bool] = True
    use_sentiment: Optional[bool] = True
    source: Optional[str] = "auto"

class SearchResult(BaseModel):
    title: str
    link: str
    snippet: str
    relevance_score: Optional[float] = None
    sentiment: Optional[Dict[str, Any]] = None
    vector: Optional[List[float]] = None
    source: Optional[str] = None
    domain: Optional[str] = None
    icon: Optional[str] = None

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResult]
    total_results: int
    processing_time: float
    semantic_used: bool
    sentiment_used: bool
    source_used: Optional[str] = None
    ai_response: Optional[Dict[str, Any]] = None