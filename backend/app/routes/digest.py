"""Scheduled morning digest prefs + on-demand send (Phase 2.3)."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.limiter import limiter
from ..services.digest_service import build_digest, deliver_to_user
from ..supabase_client import (
    ensure_user,
    get_digest_prefs,
    is_supabase_enabled,
    upsert_digest_prefs,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


class DigestPrefsRequest(BaseModel):
    enabled: bool = False
    hour_utc: int = Field(default=11, ge=0, le=23, description="UTC hour for delivery (11 ≈ 7am ET)")
    email: str = Field(default="", max_length=254)
    webhook_url: str = Field(default="", max_length=500)


@router.get("/digest/prefs")
async def get_prefs(user=Depends(get_current_user)):
    prefs = get_digest_prefs(user.get("user_id", "")) or {}
    return {
        "enabled": bool(prefs.get("enabled", False)),
        "hour_utc": prefs.get("hour_utc", 11),
        "email": prefs.get("email") or "",
        "webhook_url": prefs.get("webhook_url") or "",
        "last_sent_at": prefs.get("last_sent_at"),
        "persisted": is_supabase_enabled(),
    }


@router.post("/digest/prefs")
async def save_prefs(body: DigestPrefsRequest, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if body.enabled and not body.email and not body.webhook_url:
        raise HTTPException(status_code=400, detail="Add an email or Slack/Discord webhook to enable delivery")
    ensure_user(user_id, user.get("email"))
    saved = upsert_digest_prefs(user_id, body.enabled, body.hour_utc, body.email, body.webhook_url)
    if saved is None and is_supabase_enabled():
        raise HTTPException(status_code=500, detail="Failed to save prefs")
    if saved is None:
        return {"enabled": body.enabled, "hour_utc": body.hour_utc, "persisted": False}
    return {
        "enabled": bool(saved.get("enabled", body.enabled)),
        "hour_utc": saved.get("hour_utc", body.hour_utc),
        "email": saved.get("email") or "",
        "webhook_url": saved.get("webhook_url") or "",
        "last_sent_at": saved.get("last_sent_at"),
        "persisted": True,
    }


class DigestSendRequest(BaseModel):
    deliver: bool = Field(default=False, description="Also deliver to saved destinations")


@router.post("/digest/send-now")
@limiter.limit("5/minute")
async def send_now(request: Request, body: DigestSendRequest, user=Depends(get_current_user)):
    """Build a fresh briefing now; optionally deliver to saved email/webhook."""
    digest = await build_digest()
    delivered: dict = {"email": False, "slack": False}
    if body.deliver:
        prefs = get_digest_prefs(user.get("user_id", "")) or {}
        if prefs.get("email") or prefs.get("webhook_url"):
            delivered = await deliver_to_user(prefs.get("email"), prefs.get("webhook_url"), digest)
    return {**digest, "delivered": delivered}
