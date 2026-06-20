FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects the app to listen on port 7860.
ENV PORT=7860
ENV PYTHONUNBUFFERED=1
# Free-tier CPU can be slow; index a smaller subset so first startup finishes
# in a reasonable time. Override in Space settings if you want the full 300.
ENV MAX_DOCS=120
EXPOSE 7860

# Start immediately so platform health checks pass right away; the vector index
# (storage is ephemeral on the free tier, so this rebuilds on every restart) is
# built in a background thread on FastAPI startup — see backend/main.py.
CMD uvicorn backend.main:app --host 0.0.0.0 --port 7860
