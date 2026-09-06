"""Custom RSS/Atom feeds per user (Phase 3.3)."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.limiter import limiter
from ..supabase_client import (
    add_rss_feed,
    delete_rss_feed,
    ensure_user,
    is_supabase_enabled,
    list_rss_feeds,
    toggle_rss_feed,
)

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


class RssAdd(BaseModel):
    url: str = Field(..., min_length=10, max_length=500)
    label: str = Field(default="", max_length=120)


class RssToggle(BaseModel):
    enabled: bool


@router.get("/rss")
async def list_feeds(user=Depends(get_current_user)):
    return {"feeds": list_rss_feeds(user.get("user_id", "")), "persisted": is_supabase_enabled()}


@router.post("/rss")
@limiter.limit("10/minute")
async def add_feed(request: Request, body: RssAdd, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    url = body.url.strip()
    if not url.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="Feed URL must start with http(s)://")
    if not is_supabase_enabled():
        raise HTTPException(status_code=503, detail="Custom feeds unavailable (persistence not configured)")
    ensure_user(user_id, user.get("email"))
    row = add_rss_feed(user_id, url, body.label.strip() or url.split("/")[2][:60])
    if not row:
        raise HTTPException(status_code=500, detail="Failed to save feed (URL may already be added)")
    return {"feeds": list_rss_feeds(user_id), "persisted": True}


@router.delete("/rss/{feed_id}")
async def delete_feed(feed_id: str, user=Depends(get_current_user)):
    delete_rss_feed(user.get("user_id", ""), feed_id)
    return {"feeds": list_rss_feeds(user.get("user_id", "")), "persisted": is_supabase_enabled()}


@router.post("/rss/{feed_id}/toggle")
async def toggle_feed(feed_id: str, body: RssToggle, user=Depends(get_current_user)):
    toggle_rss_feed(user.get("user_id", ""), feed_id, body.enabled)
    return {"feeds": list_rss_feeds(user.get("user_id", "")), "persisted": is_supabase_enabled()}


@router.post("/rss/pull-now")
@limiter.limit("3/minute")
async def pull_now(request: Request, user=Depends(get_current_user)):
    from ..sources.rss_source import pull_rss_feeds

    result = pull_rss_feeds()
    return result
