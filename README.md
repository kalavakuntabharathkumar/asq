# AssessIQ — RAG-Based Assessment Question Generator

FastAPI starter for curriculum-grounded MCQ generation with ChromaDB, OpenAI embeddings/chat completion, Pydantic validation, PDF ingestion, pytest, and Docker.

## Run
```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
uvicorn app.main:app --reload
```
Visit http://127.0.0.1:8000/docs. Default `DEMO_MODE=true` works without API keys. For real generation, set `DEMO_MODE=false` and `OPENAI_API_KEY` in `.env`.

## Demo
POST `/ingest/text` with `{"source":"biology.txt","text":"Photosynthesis converts light energy into chemical energy. Chlorophyll absorbs light."}` then POST `/generate` with `{"topic":"photosynthesis","count":2}`.

Scanned PDFs need OCR. The demo embedding is a deterministic offline placeholder, not a semantic model. Use live OpenAI embeddings for actual semantic retrieval. Sample metrics in a resume should be independently validated before claiming them.
