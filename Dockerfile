FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects the app to listen on port 7860.
ENV PORT=7860
EXPOSE 7860

# Start immediately so platform health checks pass right away; the vector index
# (storage is ephemeral on the free tier, so this rebuilds on every restart) is
# built in a background thread on FastAPI startup — see backend/main.py.
CMD uvicorn backend.main:app --host 0.0.0.0 --port 7860
