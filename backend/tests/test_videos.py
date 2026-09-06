from unittest.mock import AsyncMock, patch

from fastapi.testclient import TestClient

from app.core.auth import get_current_user
from app.main import app

app.dependency_overrides[get_current_user] = lambda: {"user_id": "test_user", "email": "test@example.com"}

client = TestClient(app)


def test_videos_returns_empty_without_key():
    with patch("app.services.youtube_service.settings") as mock_settings:
        mock_settings.youtube_api_key = ""
        resp = client.get("/api/videos")
        assert resp.status_code == 200
        assert resp.json() == {"videos": []}


def test_videos_returns_normalized_items():
    fake_videos = [
        {
            "video_id": "abc123",
            "title": "NVIDIA keynote",
            "description": "desc",
            "thumbnail": "https://img/h.jpg",
            "channel": "NVIDIA",
            "published_at": "2026-08-20T12:00:00Z",
            "url": "https://www.youtube.com/watch?v=abc123",
            "category": "gpu",
        }
    ]
    with patch("app.routes.videos.fetch_youtube_videos", new_callable=AsyncMock) as mock_fetch:
        mock_fetch.return_value = fake_videos
        resp = client.get("/api/videos?category=gpu&limit=3")
        assert resp.status_code == 200
        data = resp.json()
        assert len(data["videos"]) == 1
        assert data["videos"][0]["video_id"] == "abc123"
        assert data["videos"][0]["url"] == "https://www.youtube.com/watch?v=abc123"


def test_youtube_service_normalizes_api_response():
    import asyncio

    from app.services import youtube_service as ys

    fake_api_item = {
        "id": {"videoId": "abc123"},
        "snippet": {
            "title": "NVIDIA keynote",
            "description": "desc",
            "thumbnails": {"high": {"url": "https://img/h.jpg"}},
            "channelTitle": "NVIDIA",
            "publishedAt": "2026-08-20T12:00:00Z",
        },
    }

    class FakeResp:
        status_code = 200

        def json(self):
            return {"items": [fake_api_item]}

        text = "{}"

    class FakeClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def get(self, *a, **k):
            return FakeResp()

    with patch.object(ys.settings, "youtube_api_key", "fake-key"):
        with patch("app.services.youtube_service.httpx.AsyncClient", return_value=FakeClient()):
            vids = asyncio.run(ys.fetch_youtube_videos(query="NVIDIA", category="gpu", limit=3))
            assert len(vids) == 1
            assert vids[0]["video_id"] == "abc123"


def test_videos_handles_api_failure_gracefully():
    with patch("app.services.youtube_service.settings") as mock_settings:
        mock_settings.youtube_api_key = "fake-key"
        with patch("app.services.youtube_service.httpx.AsyncClient", side_effect=Exception("boom")):
            resp = client.get("/api/videos")
            assert resp.status_code == 200
            assert resp.json() == {"videos": []}
