from pydantic import BaseModel, Field
from typing import List, Optional, Any

class AskRequest(BaseModel):
    question: str = Field(..., min_length=1)
    top_k: int = 4
    debug: bool = False
    hybrid: bool = False

class Source(BaseModel):
    source: Optional[str] = None
    page: Optional[int] = None
    chunk_id: Optional[str] = None
    metadata: Optional[Any] = None

class ChunkUsed(BaseModel):
    text: str
    source: Optional[str] = None
    page: Optional[int] = None
    similarity: Optional[float] = None

# app/schemas.py (modified)

class AskResponse(BaseModel):
    question: str
    answer: str
    sources: List[Source]
    chunks_used: List[ChunkUsed]
    clarification_required: Optional[bool] = False
    clarification_question: Optional[str] = None
    debug_context: Optional[str] = None

