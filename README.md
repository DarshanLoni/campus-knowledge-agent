# Campus Knowledge Agent

A monorepo for a campus knowledge agent platform with FastAPI backend and optional Streamlit frontend.

## Structure


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
# Campus Knowledge Agent

Campus Knowledge Agent is an AI-powered platform designed to ingest, retrieve, and answer queries about campus-related documents and knowledge bases. It features a robust backend API and an interactive frontend for seamless user experience.

## Features
- **Document Ingestion:** Upload and process campus documents (PDFs, etc.) for knowledge extraction.
- **Semantic Search:** Retrieve relevant information using advanced retrieval and embedding techniques.
- **LLM-Powered Q&A:** Ask questions and get answers using integrated Large Language Models (LLMs).
- **Authentication:** Secure access to backend APIs.
- **Frontend Interface:** User-friendly web app for querying and exploring campus knowledge.

---

## Project Structure
```
campus-knowledge-agent/
│
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── auth.py         # Authentication logic
│   │   ├── db.py           # Database connection and models
│   │   ├── ingest.py       # Document ingestion and processing
│   │   ├── main.py         # FastAPI app entrypoint
│   │   ├── memory.py       # In-memory storage utilities
│   │   ├── prompt.py       # Prompt templates for LLMs
│   │   ├── query_llm.py    # LLM query logic
│   │   ├── retrieval.py    # Semantic search and retrieval
│   │   ├── schemas.py      # Pydantic schemas
│   │   └── utils.py        # Utility functions
│   ├── requirements.txt    # Backend dependencies
│   └── ...
│
├── frontend/
│   ├── app.py              # Streamlit app entrypoint
│   ├── config.py           # Frontend configuration
│   ├── requirements.txt    # Frontend dependencies
│   └── utils.py            # Frontend utilities
│
├── requirements.txt        # Top-level requirements
├── service_account.json    # Service account credentials (if needed)
└── README.md               # Project documentation
```

---

## Getting Started

### Backend (FastAPI)
1. **Install dependencies:**
   ```bash
   pip install -r backend/requirements.txt
   ```
2. **Run the backend server:**
   ```bash
   cd backend
   uvicorn app.main:app --reload
   ```

### Frontend (Streamlit)
1. **Install dependencies:**
   ```bash
   pip install -r frontend/requirements.txt
   ```
2. **Run the frontend app:**
   ```bash
   cd frontend
   streamlit run app.py
   ```

---

## Usage
- **Ingest Documents:** Use the frontend or API to upload campus documents.
- **Ask Questions:** Enter queries in the frontend to get instant, context-aware answers.
- **Authentication:** Secure endpoints require authentication (see `backend/app/auth.py`).

---

## Technologies Used
- **Backend:** FastAPI, Pydantic, Uvicorn
- **Frontend:** Streamlit
- **LLM Integration:** OpenAI or similar (see `backend/app/query_llm.py`)
- **Database:** (Configurable, see `backend/app/db.py`)

---

## Contributing
1. Fork the repository
2. Create a new branch (`git checkout -b feature/your-feature`)
3. Commit your changes
4. Push to the branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---




