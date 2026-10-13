from pathlib import Path
from fastapi import FastAPI, HTTPException, UploadFile, File
from app.config import settings
from app.schemas import IngestTextRequest, IngestResponse, GenerateRequest, GenerateResponse
from app.rag import CurriculumIndex
from app.ingestion import extract_file_text
from app.generator import generate_mcqs

app = FastAPI(title="AssessIQ", version="1.0.0")
index = CurriculumIndex()

@app.get("/health")
def health():
    return {"status": "ok", "mode": "demo" if settings.demo_mode else "live",
            "indexed_chunks": index.collection.count()}

@app.post("/ingest/text", response_model=IngestResponse)
def ingest_text(request: IngestTextRequest):
    try:
        return IngestResponse(source=request.source, chunks_added=index.add_document(request.source, request.text))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@app.post("/ingest/file", response_model=IngestResponse)
async def ingest_file(file: UploadFile = File(...)):
    suffix = Path(file.filename or "").suffix.lower()
    if suffix not in {".txt", ".pdf"}:
        raise HTTPException(status_code=400, detail="Only .txt and .pdf files are supported")
    temp = Path("data") / f"upload{suffix}"
    temp.parent.mkdir(exist_ok=True)
    temp.write_bytes(await file.read())
    try:
        content = extract_file_text(str(temp))
        if len(content.strip()) < 20:
            raise HTTPException(status_code=422, detail="No usable text found; scanned PDFs require OCR")
        return IngestResponse(source=file.filename or "upload", chunks_added=index.add_document(file.filename or "upload", content))
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        temp.unlink(missing_ok=True)

@app.post("/generate", response_model=GenerateResponse)
def generate(request: GenerateRequest):
    passages = index.retrieve(request.topic)
    if not passages:
        raise HTTPException(status_code=404, detail="Ingest curriculum text or PDF first")
    try:
        questions, mode = generate_mcqs(request.topic, request.count, request.difficulty, passages)
        return GenerateResponse(topic=request.topic, questions=questions, retrieved_chunks=len(passages), mode=mode)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Generation or validation failed: {exc}")
