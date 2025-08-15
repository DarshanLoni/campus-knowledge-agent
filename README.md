# Campus Knowledge Agent

A monorepo for a campus knowledge agent platform with FastAPI backend and optional Streamlit frontend.

## Structure

- `backend/`: FastAPI app
- `frontend/`: Streamlit app (optional)
- `.github/workflows/`: CI/CD configs
- `docker-compose.yml`: Multi-container setup

## Quick Start

1. **Backend**
   - `cd backend`
   - `pip install -r requirements.txt`
   - `uvicorn app.main:app --reload`

2. **Frontend**
   - `cd frontend`
   - `pip install -r requirements.txt`
   - `streamlit run app.py`

3. **Docker Compose**
   - `docker-compose up --build`
