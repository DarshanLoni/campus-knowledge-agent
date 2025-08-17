# app/auth.py
#  CHECKPOINT WORKING
import os, time, json, base64, hashlib, hmac, secrets
import requests
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .db import supabase

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")
GOOGLE_CLIENT_SECRET = os.getenv("GOOGLE_CLIENT_SECRET")
GOOGLE_REDIRECT_URI = os.getenv("GOOGLE_REDIRECT_URI")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-secret-change-me")
JWT_ISSUER = os.getenv("JWT_ISSUER", "campus-agent")
JWT_AUDIENCE = os.getenv("JWT_AUDIENCE", "campus-agent-users")

auth_router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=True)

class AuthURLResponse(BaseModel):
    auth_url: str

class User(BaseModel):
    user_id: str
    email: Optional[str] = None
    name: Optional[str] = None
    picture: Optional[str] = None

class TokenResponse(BaseModel):
    token: str
    user: User

def _b64url(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("utf-8")

def _sign_jwt(payload: Dict[str, Any], secret: str) -> str:
    header = {"alg": "HS256", "typ": "JWT"}
    h_b64 = _b64url(json.dumps(header, separators=(",", ":")).encode())
    p_b64 = _b64url(json.dumps(payload, separators=(",", ":")).encode())
    signing_input = f"{h_b64}.{p_b64}".encode()
    sig = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
    s_b64 = _b64url(sig)
    return f"{h_b64}.{p_b64}.{s_b64}"

def _verify_jwt(token: str, secret: str) -> Dict[str, Any]:
    try:
        parts = token.split(".")
        if len(parts) != 3:
            raise ValueError("Invalid token")
        h_b64, p_b64, s_b64 = parts
        signing_input = f"{h_b64}.{p_b64}".encode()
        sig = base64.urlsafe_b64decode(s_b64 + "==")
        expected = hmac.new(secret.encode(), signing_input, hashlib.sha256).digest()
        if not hmac.compare_digest(sig, expected):
            raise ValueError("Signature mismatch")
        payload = json.loads(base64.urlsafe_b64decode(p_b64 + "=="))
        now = int(time.time())
        if payload.get("exp") and now > payload["exp"]:
            raise ValueError("Token expired")
        if payload.get("iss") != JWT_ISSUER or payload.get("aud") != JWT_AUDIENCE:
            raise ValueError("Bad iss/aud")
        return payload
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Invalid token: {e}")

def create_jwt(user_id: str) -> str:
    now = int(time.time())
    payload = {
        "sub": user_id,
        "user_id": user_id,
        "iss": JWT_ISSUER,
        "aud": JWT_AUDIENCE,
        "iat": now,
        "exp": now + 60*60*24*7  # 7 days
    }
    return _sign_jwt(payload, JWT_SECRET)

async def get_current_user(token: HTTPAuthorizationCredentials = Depends(bearer_scheme)) -> Dict[str, Any]:
    payload = _verify_jwt(token.credentials, JWT_SECRET)
    return {"user_id": payload["user_id"]}

@auth_router.get("/google/login", response_model=AuthURLResponse)
def google_login():
    state = secrets.token_urlsafe(16)
    scope = "openid email profile"
    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth"
        f"?client_id={GOOGLE_CLIENT_ID}"
        f"&redirect_uri={GOOGLE_REDIRECT_URI}"
        f"&response_type=code"
        f"&scope={scope}"
        f"&access_type=offline"
        f"&include_granted_scopes=true"
        f"&state={state}"
        f"&prompt=consent"
    )
    return {"auth_url": auth_url}

@auth_router.get("/google/callback", response_model=TokenResponse)
def google_callback(code: str = Query(...)):
    # 1) Exchange code for tokens
    token_resp = requests.post(
        "https://oauth2.googleapis.com/token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "code": code,
            "client_id": GOOGLE_CLIENT_ID,
            "client_secret": GOOGLE_CLIENT_SECRET,
            "redirect_uri": GOOGLE_REDIRECT_URI,
            "grant_type": "authorization_code",
        },
        timeout=30,
    )
    if token_resp.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")
    tokens = token_resp.json()
    access_token = tokens.get("access_token")

    # 2) Fetch user info (OpenID userinfo)
    ui = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if ui.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Userinfo failed: {ui.text}")
    info = ui.json()
    # Google 'sub' is stable unique id for the user
    user_id = info.get("sub")
    email = info.get("email")
    name = info.get("name")
    picture = info.get("picture")

    # 3) Upsert user in Supabase
    supabase.table("users").upsert({
        "user_id": user_id,
        "email": email,
        "name": name,
        "picture": picture,
    }, on_conflict="user_id").execute()

    # 4) Issue our JWT
    jwt_token = create_jwt(user_id)

    return {"token": jwt_token, "user": {"user_id": user_id, "email": email, "name": name, "picture": picture}}
