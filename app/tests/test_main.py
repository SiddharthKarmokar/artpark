from fastapi.testclient import TestClient
from app.main import app


def test_health() -> None:
    with TestClient(app) as client:
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] in ["ok", "degraded"]


def test_version() -> None:
    with TestClient(app) as client:
        r = client.get("/version")
        assert r.status_code == 200
        assert "version" in r.json()


def test_query_returns_200() -> None:
    with TestClient(app) as client:
        r = client.post("/query", json={"question": "what is the average?"})
        assert r.status_code == 200
