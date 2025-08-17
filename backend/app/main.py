# app/main.py
#  CHECKPOINT WORKING
import warnings
warnings.filterwarnings("ignore", category=FutureWarning)
from fastapi import FastAPI, Request, File, UploadFile, HTTPException, Depends
from typing import List, Set
from pydantic import BaseModel

from .db import supabase
from .ingest import process_document
from .retrieval import retrieve_chunks
from .query_llm import ask_gemini, generate_clarification
from .schemas import AskRequest, AskResponse, ChunkUsed, Source
from .utils import unique_sources
from .auth import auth_router, get_current_user

SIMILARITY_THRESHOLD = 0.25

app = FastAPI(title="Campus Knowledge Agent API")
app.include_router(auth_router)

# per-user in-memory follow-up context
session_memory = {}

@app.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest, user=Depends(get_current_user)):
    user_id = user["user_id"]
    previous_context = session_memory.get(user_id, {})

    chunks, raw_context = retrieve_chunks(req.question, user_id=user_id, top_k=req.top_k)

    combined_context = (previous_context.get("raw_context", "") + "\n\n" + raw_context).strip() if previous_context else raw_context

    if not chunks and not previous_context:
        return AskResponse(
            question=req.question,
            answer="I don't know based on the provided documents.",
            sources=[],
            chunks_used=[]
        )

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

    answer = ask_gemini(combined_context + "\n\nQuestion: " + req.question)

    # Save session context per user
    session_memory[user_id] = {
        "question": req.question,
        "chunks": chunks,
        "raw_context": combined_context
    }

    sources = [Source(**s) for s in unique_sources(chunks)]
    used = [ChunkUsed(
        text=c["content"], source=c.get("source"), page=c.get("page"), similarity=c.get("similarity")
    ) for c in chunks]

    return AskResponse(
        question=req.question,
        answer=answer.strip(),
        sources=sources,
        chunks_used=used
    )

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), user=Depends(get_current_user)):
    user_id = user["user_id"]

    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        f.write(await file.read())

    # Insert into files table first
    resp = supabase.table("files").insert({
        "user_id": user_id,
        "filename": file.filename,
        "storage_path": temp_path
    }).execute()

    if not resp.data:
        raise HTTPException(status_code=500, detail="Could not create file record.")
    file_id = resp.data[0]["file_id"]

    try:
        process_document(temp_path, user_id=user_id, file_id=file_id)
    except Exception as e:
        # cleanup if chunks fail
        supabase.table("files").delete().eq("file_id", file_id).execute()
        raise HTTPException(status_code=500, detail=f"Error processing document: {str(e)}")

    return {"file_id": file_id, "filename": file.filename, "status": "Processed and stored successfully."}

@app.get("/files")
def list_uploaded_files(user=Depends(get_current_user)):
    user_id = user["user_id"]
    resp = supabase.table("files").select("*").eq("user_id", user_id).execute()
    return {"files": resp.data or []}


class DeleteRequest(BaseModel):
    file_ids: List[str]

@app.delete("/files")
def delete_files(req: DeleteRequest, user=Depends(get_current_user)):
    user_id = user["user_id"]

    deleted, errors = [], []
    for fid in req.file_ids:
        resp = supabase.table("files").delete().eq("file_id", fid).eq("user_id", user_id).execute()
        if resp.data:
            deleted.append(fid)
        else:
            errors.append({"file_id": fid, "error": "Not found or not owned by user"})

    return {"deleted": deleted, "errors": errors}

