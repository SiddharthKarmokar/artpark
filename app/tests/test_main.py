from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health() -> None:
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_version() -> None:
    r = client.get("/version")
    assert r.status_code == 200
    assert "version" in r.json()


def test_query_returns_200() -> None:
    r = client.post("/query", json={"question": "what is the average?"})
    assert r.status_code == 200
