from pydantic import BaseModel
from typing import List, Optional

from config import TOP_K

class QueryRequest(BaseModel):
    query: str
    url: Optional[str] = None
    file_path: Optional[str] = None
    top_k: Optional[int] = TOP_K
    use_cache: Optional[bool] = True
    cache_key: Optional[str] = None

class DocumentResponse(BaseModel):
    content: str
    metadata: dict
    score: Optional[float] = None

class RAGResponse(BaseModel):
    query: str
    answer: str
    sources: List[DocumentResponse]
    processing_time_ms: int
    memory_usage_mb: float
    cache_hit: bool
    cache_key: Optional[str]