from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"

def test_ingest_then_generate():
    response = client.post("/ingest/text", json={"source": "test.txt",
        "text": "Photosynthesis converts light energy into chemical energy. Chlorophyll absorbs light."})
    assert response.status_code == 200
    result = client.post("/generate", json={"topic": "photosynthesis", "count": 2})
    assert result.status_code == 200
    assert len(result.json()["questions"]) == 2
