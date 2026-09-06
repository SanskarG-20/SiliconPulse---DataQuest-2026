"""Team webhooks for spike alerts (Phase 2.4)."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.limiter import limiter
from ..services.digest_service import send_slack
from ..services.webhook_service import ALLOWED_EVENTS, validate_webhook_url
from ..supabase_client import (
    add_team_webhook,
    delete_team_webhook,
    ensure_user,
    is_supabase_enabled,
    list_team_webhooks,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


class WebhookAdd(BaseModel):
    url: str = Field(..., min_length=10, max_length=500)
    events: list[str] = Field(default_factory=lambda: ["spike.alert"])


@router.get("/webhooks")
async def list_webhooks(user=Depends(get_current_user)):
    return {"webhooks": list_team_webhooks(user.get("user_id", "")), "persisted": is_supabase_enabled()}


@router.post("/webhooks")
@limiter.limit("10/minute")
async def add_webhook(request: Request, body: WebhookAdd, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    cleaned = validate_webhook_url(body.url)
    if not cleaned:
        raise HTTPException(status_code=400, detail="Only Slack (hooks.slack.com) or Discord (discord.com/api) webhook URLs are accepted")
    events = [e for e in (body.events or []) if e in ALLOWED_EVENTS] or ["spike.alert"]
    ensure_user(user_id, user.get("email"))
    row = add_team_webhook(user_id, cleaned, events)
    if row is None and is_supabase_enabled():
        raise HTTPException(status_code=500, detail="Failed to save webhook")
    return {"webhooks": list_team_webhooks(user_id), "persisted": is_supabase_enabled()}


@router.delete("/webhooks/{webhook_id}")
async def delete_webhook(webhook_id: str, user=Depends(get_current_user)):
    delete_team_webhook(user.get("user_id", ""), webhook_id)
    return {"webhooks": list_team_webhooks(user.get("user_id", "")), "persisted": is_supabase_enabled()}


class WebhookTest(BaseModel):
    url: str = Field(..., min_length=10, max_length=500)


@router.post("/webhooks/test")
@limiter.limit("5/minute")
async def test_webhook(request: Request, body: WebhookTest, user=Depends(get_current_user)):
    cleaned = validate_webhook_url(body.url)
    if not cleaned:
        raise HTTPException(status_code=400, detail="Only Slack or Discord webhook URLs are accepted")
    ok = await send_slack(cleaned, "SiliconPulse test — team webhook connected. Spike alerts will arrive here.")
    if not ok:
        raise HTTPException(status_code=502, detail="Webhook test message was not accepted")
    return {"ok": True}
