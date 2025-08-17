import os
import requests
from dotenv import load_dotenv
#  CHECKPOINT WORKING
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")


def ask_gemini(prompt: str) -> str:
    """
    Calls Gemini with a raw text prompt and returns text.
    """
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent?key={GEMINI_API_KEY}"
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.2,
            "maxOutputTokens": 400
        }
    }
    headers = {"Content-Type": "application/json"}

    resp = requests.post(url, json=payload, headers=headers, timeout=60)
    if resp.status_code != 200:
        return f"Error: {resp.text}"
    data = resp.json()
    try:
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception:
        return str(data)


def generate_clarification(query: str, context: str) -> str:
    """
    Generates a clarifying question for ambiguous queries.
    """
    prompt = f"""
    The user asked a possibly ambiguous question: "{query}"
    Based on the following context:
    "{context}"
    Generate a concise clarifying question to ask the user.
    """
    return ask_gemini(prompt)


def check_ambiguity(query: str, context: str) -> bool:
    """
    Checks if a query is ambiguous. Returns True if likely ambiguous.
    """
    prompt = f"""
    Question: "{query}"
    Context: "{context}"
    Does this question seem ambiguous or vague based on the context? 
    Answer only Yes or No.
    """
    response = ask_gemini(prompt).strip().lower()
    return "yes" in response
