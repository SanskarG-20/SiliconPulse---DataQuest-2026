"""Server-persisted watchlist + in-app alerts (Phase 1)."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.limiter import limiter
from ..settings import settings
from ..supabase_client import (
    add_watchlist_company,
    ensure_user,
    is_supabase_enabled,
    list_watchlist,
    remove_watchlist_company,
)
from ..utils import safe_read_jsonl

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


class WatchlistAdd(BaseModel):
    company: str = Field(..., min_length=1, max_length=100)


@router.get("/watchlist")
async def get_watchlist(user=Depends(get_current_user)):
    user_id = user.get("user_id")
    companies = list_watchlist(user_id) if user_id else []
    return {"companies": companies, "persisted": is_supabase_enabled()}


@router.post("/watchlist")
async def add_watchlist(body: WatchlistAdd, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    company = body.company.strip()
    if not company:
        raise HTTPException(status_code=400, detail="Company required")
    ensure_user(user_id, user.get("email"))
    ok = add_watchlist_company(user_id, company)
    if not ok and is_supabase_enabled():
        raise HTTPException(status_code=500, detail="Failed to save watchlist")
    if not ok:
        # Supabase disabled — frontend keeps localStorage copy
        return {"companies": [company], "persisted": False}
    return {"companies": list_watchlist(user_id), "persisted": True}


@router.delete("/watchlist/{company}")
async def delete_watchlist(company: str, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    remove_watchlist_company(user_id, company)
    return {"companies": list_watchlist(user_id), "persisted": is_supabase_enabled()}


@router.get("/watchlist/alerts")
async def watchlist_alerts(limit: int = 10, user=Depends(get_current_user)):
    """Recent stream signals matching the user's watchlist (in-app alerts, no email yet)."""
    user_id = user.get("user_id")
    companies = list_watchlist(user_id) if user_id else []
    if not companies:
        return {"alerts": [], "companies": []}
    lowered = [c.lower() for c in companies]
    try:
        events = safe_read_jsonl(settings.resolved_data_path, limit=100, freshness_hours=None)
        hits = []
        for ev in reversed(events):
            company = str(ev.get("company") or "")
            title = str(ev.get("title") or "")
            content = str(ev.get("content") or ev.get("snippet") or "")
            hay = f"{company} {title} {content}".lower()
            matched = next((c for c, cl in zip(companies, lowered) if cl and cl in hay), None)
            if matched:
                hits.append({**ev, "matched_company": matched})
                if len(hits) >= max(1, min(limit, 25)):
                    break
        return {"alerts": hits, "companies": companies}
    except Exception as e:
        logger.warning(f"watchlist alerts failed: {e}")
        return {"alerts": [], "companies": companies}
