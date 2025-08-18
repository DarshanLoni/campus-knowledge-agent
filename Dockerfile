# Dockerfile
FROM python:3.11-slim

# Set work directory
WORKDIR /app

# Copy frontend files
COPY frontend/ ./frontend

# Copy utils if needed
COPY frontend/utils.py ./frontend/

# Copy requirements
COPY requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Set environment variable for Streamlit
ENV STREAMLIT_SERVER_PORT=8501
ENV STREAMLIT_SERVER_HEADLESS=true
ENV STREAMLIT_SERVER_ENABLECORS=false

# Expose Streamlit port
EXPOSE 8501

# Start Streamlit
CMD ["streamlit", "run", "frontend/app.py"]
