# app/main.py
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional

app = FastAPI()

# -------------------------------
# Pydantic models
# -------------------------------
class Source(BaseModel):
    source: str
    page: Optional[int] = None

class Chunk(BaseModel):
    text: str
    source: str
    page: Optional[int] = None
    similarity: Optional[float] = None

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    question: str
    answer: Optional[str] = None
    clarification_required: Optional[bool] = False
    clarification_question: Optional[str] = None
    sources: List[Source] = []
    chunks_used: List[Chunk] = []

# -------------------------------
# Dummy knowledge base
# Replace this with your actual PDF retrieval/vector search logic
# -------------------------------
DOCUMENTS = {
    "docs/campus_rules.pdf": "There are three campuses of PESU: HN, RR, EC...",
    "docs/student_handbook.pdf": "Course objectives, IoT, Robotics, etc..."
}

# -------------------------------
# Helper functions
# -------------------------------
def retrieve_chunks(question: str):
    # Simulate retrieving relevant chunks
    chunks = []
    for src, text in DOCUMENTS.items():
        if any(word.lower() in text.lower() for word in question.lower().split()):
            chunks.append(
                Chunk(text=text, source=src, similarity=0.9)
            )
    return chunks

def check_ambiguity(question: str):
    # Dummy ambiguity detection
    ambiguous_keywords = ["location", "where", "find", "address"]
    return any(word.lower() in question.lower() for word in ambiguous_keywords)

# -------------------------------
# Ask endpoint
# -------------------------------
@app.post("/ask", response_model=AskResponse)
async def ask_question(request: AskRequest):
    question = request.question
    chunks = retrieve_chunks(question)
    
    if check_ambiguity(question):
        return AskResponse(
            question=question,
            clarification_required=True,
            clarification_question="Your question is ambiguous. Are you asking for the exact address of the campus, or general location info?",
            sources=[],
            chunks_used=[]
        )
    
    # Dummy answer generation
    answer = "Based on the provided text, PESU has three campuses: HN, RR, EC."
    
    sources = [Source(source=chunk.source, page=chunk.page) for chunk in chunks]
    
    return AskResponse(
        question=question,
        answer=answer,
        clarification_required=False,
        sources=sources,
        chunks_used=chunks
    )
