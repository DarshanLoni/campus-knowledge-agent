#!/bin/bash
# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Run FastAPI
python -m uvicorn app.main:app --host 0.0.0.0 --port 10000
