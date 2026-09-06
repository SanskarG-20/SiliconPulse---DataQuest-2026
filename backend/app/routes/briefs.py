"""Shareable brief links (Phase 1). Public read for is_public briefs."""
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from ..core.auth import get_current_user
from ..core.limiter import limiter
from ..supabase_client import create_brief, ensure_user, get_brief, is_supabase_enabled, list_briefs

logger = logging.getLogger(__name__)

# No global auth dep: POST/mine require auth per-route, public GET is open.
router = APIRouter()


class BriefShareRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500)
    insight: str = Field(..., min_length=1, max_length=50000)
    evidence: list[dict] = Field(default_factory=list, max_length=20)


@router.post("/briefs/share")
@limiter.limit("15/minute")
async def share_brief(request: Request, body: BriefShareRequest, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if not is_supabase_enabled():
        raise HTTPException(status_code=503, detail="Sharing unavailable (persistence not configured)")
    ensure_user(user_id, user.get("email"))
    brief_id = create_brief(user_id, body.query, body.insight, body.evidence)
    if not brief_id:
        raise HTTPException(status_code=500, detail="Failed to create brief")
    return {"id": brief_id, "path": f"/b/{brief_id}"}


@router.get("/briefs/mine")
async def my_briefs(limit: int = 10, user=Depends(get_current_user)):
    user_id = user.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return {"briefs": list_briefs(user_id, limit=limit), "persisted": is_supabase_enabled()}


@router.get("/briefs/public/{brief_id}")
async def public_brief(brief_id: str):
    brief = get_brief(brief_id)
    if not brief:
        raise HTTPException(status_code=404, detail="Brief not found")
    if not brief.get("is_public", True):
        raise HTTPException(status_code=403, detail="Brief is private")
    return {
        "id": brief.get("id", brief_id),
        "query": brief.get("query_text", ""),
        "insight": brief.get("insight", ""),
        "evidence": brief.get("evidence", []),
        "created_at": brief.get("created_at", ""),
    }
