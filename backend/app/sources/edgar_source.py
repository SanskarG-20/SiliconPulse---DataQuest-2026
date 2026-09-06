"""SEC EDGAR full-text 8-K ingestion (Phase 3.3). Free efts.sec.gov JSON, no API key.

Complements the Finnhub metadata path with filing-level text context
(form + items + description) for tracked semiconductor companies.
"""
import logging
import time
from datetime import datetime, timedelta
from typing import Optional

import httpx

from ..services.sec_filings import TICKER_COMPANY_MAP
from ..settings import settings
from ..utils import (
    classify_event_type,
    clean_url,
    deduplicate_and_append,
    get_primary_company,
    sanitize_content,
    sanitize_title,
)

logger = logging.getLogger(__name__)

EDGAR_SEARCH_URL = "https://efts.sec.gov/LATEST/search-index"
UA = "SiliconPulse research contact@example.com"

# Core semiconductor tickers to keep the daily pull bounded (~8 requests)
EDGAR_TICKERS = ["NVDA", "TSM", "INTC", "AMD", "AAPL", "ASML", "MU", "AVGO"]


def _filing_url(cik: str, adsh: str, doc_id: str) -> str:
    try:
        cik_num = str(int(cik))
    except Exception:
        cik_num = (cik or "").lstrip("0") or "0"
    filename = (doc_id.split(":", 1)[1] if ":" in (doc_id or "") else "").strip()
    if not adsh or not filename:
        return ""
    return f"https://www.sec.gov/Archives/edgar/data/{cik_num}/{adsh.replace('-', '')}/{filename}"


def _ticker_from_display(display_names: list) -> Optional[str]:
    import re

    for name in display_names or []:
        m = re.search(r"\(([A-Z]{1,6})\)", str(name))
        if m and m.group(1) in TICKER_COMPANY_MAP:
            return m.group(1)
    return None


def pull_edgar_signals(days_back: int = 7) -> int:
    """Fetch recent 8-K filings via EDGAR full-text search. Returns new events added."""
    end = datetime.utcnow().date()
    start = end - timedelta(days=max(1, min(days_back, 30)))
    params_base = {"dateRange": "custom", "startdt": start.isoformat(), "enddt": end.isoformat(), "forms": "8-K"}
    events = []
    try:
        with httpx.Client(timeout=20, headers={"User-Agent": UA, "Accept": "application/json"}) as client:
            for ticker in EDGAR_TICKERS:
                company = TICKER_COMPANY_MAP.get(ticker, ticker)
                try:
                    params = {"q": f'"{company}"', **params_base}
                    resp = client.get(EDGAR_SEARCH_URL, params=params)
                    resp.raise_for_status()
                    hits = resp.json().get("hits", {}).get("hits", [])[:10]
                except Exception as e:
                    logger.warning(f"EDGAR search failed for {company}: {e}")
                    continue
                for hit in hits:
                    try:
                        src = hit.get("_source", {}) if isinstance(hit, dict) else {}
                        form = src.get("form", "8-K")
                        file_date = src.get("file_date", "")
                        timestamp = f"{file_date}T12:00:00Z" if file_date else ""
                        display = src.get("display_names", []) or []
                        filer = display[0] if display else company
                        items = ", ".join(src.get("items", []) or [])
                        desc = src.get("file_description", "") or ""
                        title = sanitize_title(f"{filer} files {form}" + (f" (Items {items})" if items else "") + (f" — {desc}" if desc and desc != form else ""))
                        if not title:
                            continue
                        url = clean_url(_filing_url((src.get("ciks") or [""])[0], src.get("adsh", ""), hit.get("_id", "")))
                        content = sanitize_content(
                            f"{filer} filed {form} on {file_date or 'recent date'}" + (f" covering Items {items}." if items else ".") + (f" {desc}." if desc else ""),
                            max_len=500,
                        )
                        text = f"{title} {content}"
                        found_ticker = _ticker_from_display(display)
                        events.append(
                            {
                                "title": title,
                                "content": content,
                                "timestamp": timestamp,
                                "source": "EDGAR",
                                "url": url,
                                "company": TICKER_COMPANY_MAP.get(found_ticker, None) or get_primary_company(text) or "Unknown",
                                "event_type": classify_event_type(title, content),
                            }
                        )
                    except Exception as e:
                        logger.debug(f"Skipping malformed EDGAR hit: {e}")
                        continue
                time.sleep(0.5)  # respect SEC rate limits (10 req/s max)
    except Exception as e:
        logger.error(f"EDGAR fetch failed: {e}")
        return 0

    if not events:
        return 0
    added = deduplicate_and_append(events, settings.resolved_data_path)
    logger.info(f"{added} new EDGAR signals added (from {len(events)} fetched)")
    return added
