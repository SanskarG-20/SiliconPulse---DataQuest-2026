"""Signal timeline + trend spikes (Phase 2.1). Aggregates stream.jsonl by day."""
import logging
import math
from collections import Counter
from datetime import datetime, timedelta
from typing import Optional

from fastapi import APIRouter, Depends, Query

from ..core.auth import get_current_user
from ..settings import settings
from ..utils import parse_timestamp, safe_read_jsonl

logger = logging.getLogger(__name__)

router = APIRouter(dependencies=[Depends(get_current_user)])


def _day_key(dt: datetime) -> str:
    return dt.date().isoformat()


@router.get("/trends")
async def get_trends(
    company: Optional[str] = Query(default=None, description="Filter to company (case-insensitive)"),
    days: int = Query(default=30, ge=1, le=90, description="Window in days"),
    user=Depends(get_current_user),
):
    """Daily signal counts + per-company/type breakdown + spike days (> mean + 2σ)."""
    try:
        # Read enough history to cover the window (stream is append-only)
        events = safe_read_jsonl(settings.resolved_data_path, limit=max(500, days * 100), freshness_hours=None)
    except Exception as e:
        logger.warning(f"trends read failed: {e}")
        events = []

    now = datetime.utcnow()
    start = now - timedelta(days=days)
    wanted = (company or "").strip().lower() or None

    daily: Counter = Counter()
    by_company: Counter = Counter()
    by_type: Counter = Counter()
    total = 0

    for ev in events:
        try:
            ts = parse_timestamp(ev.get("timestamp", ""))
        except Exception:
            continue
        if ts < start:
            continue
        ev_company = str(ev.get("company") or "Unknown")
        if wanted and wanted not in ev_company.lower() and wanted not in str(ev.get("title") or "").lower():
            continue
        daily[_day_key(ts)] += 1
        by_company[ev_company] += 1
        by_type[str(ev.get("event_type") or "general")] += 1
        total += 1

    # Fill full window with zeros for stable baseline
    series = []
    cursor = start.date()
    end = now.date()
    while cursor <= end:
        key = cursor.isoformat()
        series.append({"date": key, "count": daily.get(key, 0)})
        cursor += timedelta(days=1)

    counts = [p["count"] for p in series]
    mean = sum(counts) / len(counts) if counts else 0
    var = sum((c - mean) ** 2 for c in counts) / len(counts) if counts else 0
    std = math.sqrt(var)

    spikes = [
        {"date": p["date"], "count": p["count"], "z": round((p["count"] - mean) / std, 2) if std > 0 else 0}
        for p in series
        if std > 0 and p["count"] >= 3 and p["count"] > mean + 2 * std
    ]
    # Most recent spikes first
    spikes.sort(key=lambda s: s["date"], reverse=True)

    top_companies = [{"company": k, "count": v} for k, v in by_company.most_common(8)]
    top_types = [{"event_type": k, "count": v} for k, v in by_type.most_common(8)]

    return {
        "company": company,
        "days": days,
        "total": total,
        "daily": series,
        "spikes": spikes[:5],
        "by_company": top_companies,
        "by_type": top_types,
        "mean": round(mean, 2),
        "std": round(std, 2),
    }
