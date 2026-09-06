"""Tests for the bounded Gemini fallback chain (insight timeout fix)."""
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from app.services import gemini_client as gc


def _client_with_models(models):
    client = gc.GeminiClient.__new__(gc.GeminiClient)
    client.available_models = list(models)
    client.client = None
    return client


def test_is_text_model_filters_non_text():
    assert gc._is_text_model("models/gemini-2.5-flash")
    assert gc._is_text_model("gemini-1.5-pro")
    for bad in [
        "models/gemini-2.5-flash-preview-tts",
        "models/gemini-2.5-flash-image",
        "models/gemini-embedding-001",
        "models/gemini-robotics-er-1.6-preview",
        "models/gemini-2.5-computer-use-preview-10-2025",
        "models/deep-research-pro-preview-12-2025",
        "models/lyria-3-pro-preview",
        "models/gemini-3.5-transcribe",
        "models/nano-banana-pro-preview",
        "models/veo-3.0-generate-preview",
    ]:
        assert not gc._is_text_model(bad), bad


def test_fallback_chain_capped_at_three_models():
    """Even with 10 failing models, at most MAX_FALLBACK_MODELS are attempted."""
    client = _client_with_models([f"gemini-model-{i}" for i in range(10)])
    calls = []

    async def always_fail(model_name, prompt, timeout=10, response_schema=None):
        calls.append(model_name)
        raise Exception("429 Quota exceeded")

    client._generate_with_timeout = always_fail
    result = asyncio.run(client.generate_content_with_fallback("hello"))
    assert result == "Insight generation unavailable. Please try again later."
    assert len(calls) == gc.MAX_FALLBACK_MODELS
    assert calls == [f"gemini-model-{i}" for i in range(gc.MAX_FALLBACK_MODELS)]


def test_fallback_returns_first_success():
    client = _client_with_models(["m1", "m2", "m3"])

    async def fail_then_succeed(model_name, prompt, timeout=10, response_schema=None):
        if model_name == "m1":
            raise Exception("429 Quota exceeded")
        return '{"sections": []}'

    client._generate_with_timeout = fail_then_succeed
    assert asyncio.run(client.generate_content_with_fallback("hi")) == '{"sections": []}'


def test_legacy_fallback_only_on_not_found():
    """Quota/auth errors must NOT burn a second full retry cycle on legacy."""
    client = _client_with_models(["gemini-1.5-flash"])

    fake_aio_models = MagicMock()

    async def raise_429(*a, **k):
        raise Exception("429 Quota exceeded")

    async def raise_404(*a, **k):
        raise Exception("404 Model not found")

    fake_aio_models.generate_content = raise_429
    fake_client = MagicMock()
    fake_client.aio.models = fake_aio_models
    client.client = fake_client

    fake_legacy = MagicMock()
    with patch.object(gc, "NEW_SDK", True), patch.object(gc, "genai_new", MagicMock()), patch.object(
        gc, "LEGACY_AVAILABLE", True
    ), patch.object(gc, "genai_legacy", fake_legacy):
        # 429 -> legacy must NOT be attempted (tenacity retries new SDK twice, then raises)
        try:
            asyncio.run(client._generate_with_timeout("gemini-1.5-flash", "hi", timeout=5))
            raise AssertionError("should have raised")
        except Exception as e:
            assert "429" in str(e)
        fake_legacy.GenerativeModel.assert_not_called()

        # 404 -> legacy IS attempted
        fake_aio_models.generate_content = raise_404
        fake_model = MagicMock()
        fake_resp = MagicMock()
        fake_resp.text = "legacy-ok"
        fake_model.generate_content_async = AsyncMock(return_value=fake_resp)
        fake_legacy.GenerativeModel.return_value = fake_model
        assert asyncio.run(client._generate_with_timeout("gemini-1.5-flash", "hi", timeout=5)) == "legacy-ok"
