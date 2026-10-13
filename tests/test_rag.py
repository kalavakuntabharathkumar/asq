import pytest
from app.rag import chunk_text

def test_empty_text():
    assert chunk_text("  ") == []

def test_chunks_preserve_content():
    text = "Photosynthesis converts light into energy. " * 50
    chunks = chunk_text(text, size=160, overlap=20)
    assert len(chunks) > 1
    assert "Photosynthesis" in " ".join(chunks)

def test_overlap_must_be_smaller_than_size():
    with pytest.raises(ValueError):
        chunk_text("some text", size=10, overlap=10)
