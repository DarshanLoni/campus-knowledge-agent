# app/memory.py
#  CHECKPOINT WORKING Fully functional
from typing import Dict, List
from .schemas import AskRequest, AskResponse

# Temporary in-memory store for conversation sessions
# session_id -> List[AskResponse]
conversation_memory: Dict[str, List[AskResponse]] = {}


def get_history(session_id: str) -> List[AskResponse]:
    """Retrieve conversation history for a session"""
    return conversation_memory.get(session_id, [])


def add_to_history(session_id: str, response: AskResponse):
    """Append a new response to session memory"""
    if session_id not in conversation_memory:
        conversation_memory[session_id] = []
    conversation_memory[session_id].append(response)
