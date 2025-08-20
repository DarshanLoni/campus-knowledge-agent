# app/prompt.py
#  CHECKPOINT WORKING Fully functional
from typing import List, Dict

SYSTEM_INSTRUCTION = (
    "You are a campus knowledge assistant. "
    "Answer ONLY using the provided CONTEXT. "
    "If the answer is not present in the context, reply: "
    "\"I don't know based on the provided documents.\" "
    "Cite sources as [S1], [S2], etc. where S# corresponds to the numbered sources."
)

def build_context_block(chunks: List[Dict]) -> str:
    """
    chunks: list of dicts with keys: text, source, page, similarity
    returns formatted context string with numbered sources
    """
    lines = []
    for i, ch in enumerate(chunks, start=1):
        label = f"S{i}"
        src = ch.get("source") or "unknown"
        page = ch.get("page")
        head = f"[{label}] {src}" + (f" p.{page}" if page is not None else "")
        body = ch["text"].strip()
        lines.append(f"{head}\n{body}")
    return "\n\n".join(lines)

def build_user_prompt(question: str, context_block: str) -> str:
    return (
        f"{SYSTEM_INSTRUCTION}\n\n"
        f"CONTEXT:\n{context_block}\n\n"
        f"QUESTION:\n{question}\n\n"
        f"INSTRUCTIONS:\n"
        f"- Be concise and factually correct.\n"
        f"- Include citations [S#] after each claim you take from context.\n"
    )
