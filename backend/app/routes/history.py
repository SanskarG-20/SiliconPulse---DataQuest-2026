"""Saved searches + query history (Phase 1). Reads existing queries/insights tables."""
from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from ..core.auth import get_current_user
from ..supabase_client import is_supabase_enabled, list_user_history

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.get("/history/queries")
async def query_history(limit: int = 10, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    items = list_user_history(user_id, kind="queries", limit=limit) if user_id else []
    # Trim to what UI needs
    trimmed = [
        {"id": r.get("id"), "query": r.get("query_text", ""), "k": r.get("k"), "evidence_count": r.get("evidence_count"), "signal_strength": r.get("signal_strength"), "created_at": r.get("created_at")}
        for r in items
    ]
    return {"items": trimmed, "persisted": is_supabase_enabled()}


@router.get("/history/insights")
async def insight_history(limit: int = 10, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    items = list_user_history(user_id, kind="insights", limit=limit) if user_id else []
    trimmed = [
        {"id": r.get("id"), "query": r.get("query_text", ""), "status": r.get("status"), "model": r.get("model_name"), "created_at": r.get("created_at")}
        for r in items
    ]
    return {"items": trimmed, "persisted": is_supabase_enabled()}
