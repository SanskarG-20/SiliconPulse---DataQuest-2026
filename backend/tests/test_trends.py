from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app

app.dependency_overrides[get_current_user] = lambda: {"user_id": "test_user", "email": "test@example.com"}

client = TestClient(app)


def test_trends_returns_series():
    resp = client.get("/api/trends?days=30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["days"] == 30
    assert len(data["daily"]) == 31  # inclusive window
    assert data["total"] >= 0
    assert "mean" in data and "std" in data
    assert isinstance(data["spikes"], list)
    assert isinstance(data["by_company"], list)


def test_trends_company_filter():
    resp = client.get("/api/trends?company=TSMC&days=30")
    assert resp.status_code == 200
    data = resp.json()
    assert data["company"] == "TSMC"
    assert data["total"] >= 0


def test_trends_spike_shape():
    resp = client.get("/api/trends?days=7")
    assert resp.status_code == 200
    for s in resp.json()["spikes"]:
        assert {"date", "count", "z"} <= set(s.keys())
        assert s["count"] >= 3
