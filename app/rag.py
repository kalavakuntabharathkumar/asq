import hashlib, re
from pathlib import Path
import chromadb
from app.config import settings

def chunk_text(text: str, size=None, overlap=None) -> list[str]:
    size = size or settings.chunk_size
    overlap = settings.chunk_overlap if overlap is None else overlap
    text = re.sub(r"\\s+", " ", text).strip()
    if not text:
        return []
    if overlap >= size:
        raise ValueError("overlap must be smaller than chunk size")
    chunks, start = [], 0
    while start < len(text):
        end = min(start + size, len(text))
        if end < len(text):
            boundary = text.rfind(". ", start + size // 2, end)
            if boundary > start:
                end = boundary + 1
        if text[start:end].strip():
            chunks.append(text[start:end].strip())
        if end >= len(text):
            break
        start = max(end - overlap, start + 1)
    return chunks

class CurriculumIndex:
    def __init__(self):
        Path(settings.chroma_path).mkdir(parents=True, exist_ok=True)
        self.client = chromadb.PersistentClient(path=settings.chroma_path)
        self.collection = self.client.get_or_create_collection(
            name=settings.collection_name, metadata={"hnsw:space": "cosine"})
        self._openai = None

    def _client(self):
        if self._openai is None:
            from openai import OpenAI
            self._openai = OpenAI(api_key=settings.openai_api_key)
        return self._openai

    def _embeddings(self, texts):
        if settings.demo_mode:
            # Offline placeholder embeddings; use OpenAI embeddings for real semantic retrieval.
            vectors = []
            for value in texts:
                raw = hashlib.sha256(value.lower().encode()).digest()
                vectors.append([raw[i % len(raw)] / 127.5 - 1 for i in range(96)])
            return vectors
        response = self._client().embeddings.create(model=settings.openai_embedding_model, input=texts)
        return [item.embedding for item in response.data]

    def add_document(self, source, text):
        chunks = chunk_text(text)
        if not chunks:
            return 0
        ids = [hashlib.sha1(f"{source}:{i}:{c}".encode()).hexdigest() for i, c in enumerate(chunks)]
        self.collection.upsert(ids=ids, documents=chunks,
            metadatas=[{"source": source, "chunk": i} for i in range(len(chunks))],
            embeddings=self._embeddings(chunks))
        return len(chunks)

    def retrieve(self, query, k=5):
        total = self.collection.count()
        if not total:
            return []
        result = self.collection.query(query_embeddings=self._embeddings([query]),
            n_results=min(k, total), include=["documents", "metadatas", "distances"])
        docs, metas = result["documents"][0], result["metadatas"][0]
        distances = result["distances"][0]
        return [{"text": d, "source": m.get("source", "unknown"), "distance": distances[i]}
                for i, (d, m) in enumerate(zip(docs, metas))]
