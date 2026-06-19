FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Hugging Face Spaces expects the app to listen on port 7860.
ENV PORT=7860
EXPOSE 7860

# Build the vector index at container start (storage is ephemeral on the free tier,
# so this has to run on every restart), then start the combined backend+frontend server.
CMD python scripts/build_index.py && uvicorn backend.main:app --host 0.0.0.0 --port 7860
