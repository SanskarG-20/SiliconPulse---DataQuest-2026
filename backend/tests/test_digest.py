from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app

app.dependency_overrides[get_current_user] = lambda: {"user_id": "test_user", "email": "test@example.com"}

client = TestClient(app)


def test_digest_prefs_get_empty():
    with patch("app.routes.digest.get_digest_prefs", return_value=None):
        resp = client.get("/api/digest/prefs")
        assert resp.status_code == 200
        assert resp.json()["enabled"] is False


def test_digest_prefs_requires_destination_when_enabling():
    resp = client.post("/api/digest/prefs", json={"enabled": True, "hour_utc": 11, "email": "", "webhook_url": ""})
    assert resp.status_code == 400


def test_digest_prefs_save():
    with patch("app.routes.digest.ensure_user", return_value=True), patch(
        "app.routes.digest.upsert_digest_prefs",
        return_value={"enabled": True, "hour_utc": 11, "email": "a@b.c", "webhook_url": "", "last_sent_at": None},
    ):
        resp = client.post("/api/digest/prefs", json={"enabled": True, "hour_utc": 11, "email": "a@b.c", "webhook_url": ""})
        assert resp.status_code == 200
        assert resp.json()["persisted"] is True


def test_digest_send_now_builds():
    fake_digest = {"query": "q", "insight": '{"sections": []}', "evidence": []}
    with patch("app.routes.digest.build_digest", new_callable=AsyncMock) as mock_build:
        mock_build.return_value = fake_digest
        resp = client.post("/api/digest/send-now", json={"deliver": False})
        assert resp.status_code == 200
        assert resp.json()["insight"] == '{"sections": []}'
        assert resp.json()["delivered"] == {"email": False, "slack": False}


def test_digest_service_no_key_no_crash():
    import asyncio

    from app.services import digest_service as ds

    async def fake_retrieve(q, k=5):
        return []

    with patch.object(ds, "retrieve_evidence", side_effect=fake_retrieve):
        with patch.object(ds.settings, "gemini_api_key", ""):
            digest = asyncio.run(ds.build_digest())
            assert "insight" in digest
            assert ds.insight_to_text(digest["insight"])
