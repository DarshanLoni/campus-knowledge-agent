# app/main.py
from fastapi import FastAPI, Request
from .ingest import process_document
from .retrieval import retrieve_chunks
from .query_llm import ask_gemini, generate_clarification
from .schemas import AskRequest, AskResponse, ChunkUsed, Source
from .utils import unique_sources

SIMILARITY_THRESHOLD = 0.25  # Minimum similarity to consider chunk relevant

app = FastAPI(title="Campus Knowledge Agent API")

# Simple in-memory session memory: stores last question + chunks per user
session_memory = {}

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, request: Request):
    user_id = request.client.host  # for simplicity, using IP; can use auth ID
    previous_context = session_memory.get(user_id, {})

    # Retrieve top chunks from DB
    chunks, raw_context = retrieve_chunks(req.question, top_k=req.top_k)

    # Combine with previous context if follow-up
    if previous_context:
        combined_context = previous_context.get("raw_context", "") + "\n\n" + raw_context
    else:
        combined_context = raw_context

    if not chunks and not previous_context:
        return AskResponse(
            question=req.question,
            answer="I don't know based on the provided documents.",
            sources=[],
            chunks_used=[]
        )

    # Check ambiguity based on similarity
    top_similarity = max([c.get("similarity", 0) for c in chunks], default=0)
    if top_similarity < SIMILARITY_THRESHOLD and not previous_context:
        clarification = generate_clarification(req.question, combined_context)
        return AskResponse(
            question=req.question,
            answer=None,
            sources=[],
            chunks_used=[],
            clarification_required=True,
            clarification_question=clarification
        )

    # Ask Gemini LLM using combined context
    answer = ask_gemini(combined_context + "\n\nQuestion: " + req.question)

    # Save current context to session memory
    session_memory[user_id] = {
        "question": req.question,
        "chunks": chunks,
        "raw_context": combined_context
    }

    # Prepare sources and chunks_used
    sources = [Source(**s) for s in unique_sources(chunks)]
    used = [ChunkUsed(
        text=c["content"],
        source=c.get("source"),
        page=c.get("page"),
        similarity=c.get("similarity")
    ) for c in chunks]

    return AskResponse(
        question=req.question,
        answer=answer.strip(),
        sources=sources,
        chunks_used=used
    )
