# app/schemas.py (or wherever your models are defined)
from typing import List, Optional
from pydantic import BaseModel

class Source(BaseModel):
    source: str
    page: Optional[int] = None

class ChunkUsed(BaseModel):
    text: str
    source: str
    page: Optional[int] = None
    similarity: Optional[float] = None

class AskResponse(BaseModel):
    question: str
    answer: Optional[str] = None  # Made optional
    clarification_required: Optional[bool] = False
    clarification_question: Optional[str] = None
    sources: List[Source] = []
    chunks_used: List[ChunkUsed] = []
