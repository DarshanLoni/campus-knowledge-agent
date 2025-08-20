# app/auth.py
#  CHECKPOINT WORKING Fully functional
import os, time, json, base64, hashlib, hmac, secrets
import requests
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .db import supabase
from fastapi.responses import RedirectResponse
from fastapi import Cookie, Header

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

async def get_current_user(
    authorization: Optional[str] = Header(None),
    jwt_token: Optional[str] = Cookie(None)
) -> Dict[str, Any]:
    token = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
    elif jwt_token:
        token = jwt_token
    else:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = _verify_jwt(token, JWT_SECRET)
    return {"user_id": payload["user_id"]}

@auth_router.get("/google/login")
def google_login_redirect():
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
    # Redirect user automatically to Google OAuth
    return RedirectResponse(url=auth_url)

# @auth_router.get("/google/callback")
# def google_callback(code: str = Query(...)):
#     # 1) Exchange code for tokens
#     token_resp = requests.post(
#         "https://oauth2.googleapis.com/token",
#         headers={"Content-Type": "application/x-www-form-urlencoded"},
#         data={
#             "code": code,
#             "client_id": GOOGLE_CLIENT_ID,
#             "client_secret": GOOGLE_CLIENT_SECRET,
#             "redirect_uri": GOOGLE_REDIRECT_URI,
#             "grant_type": "authorization_code",
#         },
#         timeout=30,
#     )
#     if token_resp.status_code != 200:
#         raise HTTPException(status_code=400, detail=f"Token exchange failed: {token_resp.text}")
#     tokens = token_resp.json()
#     access_token = tokens.get("access_token")

#     # 2) Fetch user info
#     ui = requests.get(
#         "https://openidconnect.googleapis.com/v1/userinfo",
#         headers={"Authorization": f"Bearer {access_token}"},
#         timeout=30,
#     )
#     if ui.status_code != 200:
#         raise HTTPException(status_code=400, detail=f"Userinfo failed: {ui.text}")
#     info = ui.json()
#     user_id = info.get("sub")
#     email = info.get("email")
#     name = info.get("name")
#     picture = info.get("picture")

#     # 3) Upsert user in Supabase
#     supabase.table("users").upsert({
#         "user_id": user_id,
#         "email": email,
#         "name": name,
#         "picture": picture,
#     }, on_conflict="user_id").execute()

#     # 4) Issue JWT
#     jwt_token = create_jwt(user_id)

#     # 5) Set JWT in HttpOnly cookie & redirect
#     # redirect_url = os.getenv("FRONTEND_URL", "http://localhost:3000/home")
#     # response = RedirectResponse(url=redirect_url)
#     # response.set_cookie(
#     #     key="jwt_token",
#     #     value=jwt_token,
#     #     httponly=True,
#     #     secure=False,  # set False if testing in localhost without HTTPS
#     #     samesite="lax",
#     #     max_age=60*60*24*7  # 7 days
#     # )
#     # return response

#       # 5) Redirect with token in URL query (for Streamlit or SPA)
#     redirect_url = os.getenv("FRONTEND_URL", "http://localhost:8501/home")
#     redirect_url_with_token = f"{redirect_url}?token={jwt_token}"
#     response = RedirectResponse(url=redirect_url_with_token)
#     return response
@auth_router.get("/google/callback")
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

    # 2) Fetch user info
    ui = requests.get(
        "https://openidconnect.googleapis.com/v1/userinfo",
        headers={"Authorization": f"Bearer {access_token}"},
        timeout=30,
    )
    if ui.status_code != 200:
        raise HTTPException(status_code=400, detail=f"Userinfo failed: {ui.text}")
    info = ui.json()
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

    # 4) Issue JWT
    jwt_token = create_jwt(user_id)

    # 5) Redirect to frontend (Streamlit) with token in query param
   # Redirect to Streamlit main page with token as query param
    redirect_url = os.getenv("FRONTEND_URL", "http://localhost:8501")
    redirect_url_with_token = f"{redirect_url}?token={jwt_token}"
    response = RedirectResponse(url=redirect_url_with_token)
    return response
