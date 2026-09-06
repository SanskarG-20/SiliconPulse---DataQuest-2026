from __future__ import annotations

# pyright: reportMissingImports=false
import logging
from typing import Any

from .settings import settings

logger = logging.getLogger(__name__)

_supabase_client: Any | None = None
_supabase_failed = False


def is_supabase_enabled() -> bool:
    url = (settings.supabase_url or "").strip()
    key = (settings.supabase_service_role_key or "").strip()
    placeholder_tokens = ("your-", "your_", "example", "placeholder")
    if not url or not key:
        return False
    if any(token in url.lower() for token in placeholder_tokens):
        return False
    if any(token in key.lower() for token in placeholder_tokens):
        return False
    return True


def get_supabase_client() -> Any | None:
    """
    Service-role client (bypasses RLS). Used for server-side writes.
    RLS is enforced for direct client access via anon key; see migration 001_rls.sql.
    """
    global _supabase_client, _supabase_failed

    if _supabase_client is not None:
        return _supabase_client
    if _supabase_failed:
        return None

    if not is_supabase_enabled():
        return None

    try:
        from supabase import create_client
    except Exception as exc:
        logger.warning("Supabase package import failed: %s", exc)
        return None

    try:
        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_service_role_key,
        )
        return _supabase_client
    except Exception as exc:
        logger.warning("Supabase client initialization failed: %s", exc)
        _supabase_failed = True
        return None


def get_user_scoped_client(jwt: str) -> Any | None:
    """
    Per-user client that respects RLS (requires SUPABASE_ANON_KEY + valid Clerk JWT).
    Returns None if anon key not configured. Useful if you later expose Supabase
    directly to the frontend with RLS. Currently backend uses service_role for writes.
    """
    if not is_supabase_enabled():
        return None
    anon = (settings.supabase_anon_key or "").strip()
    if not anon:
        return None
    try:
        from supabase import create_client

        client = create_client(settings.supabase_url, anon)
        # Supabase-py will send Authorization: Bearer <jwt> if you set auth
        try:
            client.auth.set_session(access_token=jwt, refresh_token="")  # type: ignore
        except Exception:
            pass
        # Fallback: inject header manually for postgrest
        try:
            client.postgrest.auth(jwt)  # type: ignore
        except Exception:
            pass
        return client
    except Exception as exc:
        logger.debug(f"User-scoped Supabase client failed: {exc}")
        return None


def ensure_user(user_id: str, email: str | None = None) -> bool:
    """
    Ensure user exists in Supabase.
    Creates user if not exists, updates email if provided.
    Returns True if successful, False otherwise.
    """
    client = get_supabase_client()
    if client is None:
        logger.warning("Supabase client not initialized - skipping user creation")
        return False

    if not user_id:
        logger.warning("ensure_user called with empty user_id")
        return False

    payload: dict[str, Any] = {"id": user_id}
    if email:
        payload["email"] = email

    try:
        logger.debug(f"Upserting user {user_id} with payload {payload}")
        response = client.table("users").upsert(payload, on_conflict="id").execute()

        if response.data:
            logger.info(f"✓ User {user_id} successfully synced to Supabase (email: {email})")
            return True
        else:
            logger.warning(f"Supabase upsert for user {user_id} returned empty data")
            return False

    except Exception as exc:
        logger.error(f"✗ Supabase ensure_user failed for {user_id}: {exc}", exc_info=True)
        return False


def insert_query_record(
    user_id: str,
    query_text: str,
    k: int,
    evidence_count: int,
    signal_strength: int,
) -> str | None:
    client = get_supabase_client()
    if client is None:
        return None

    try:
        response = (
            client.table("queries")
            .insert(
                {
                    "user_id": user_id,
                    "query_text": query_text,
                    "k": k,
                    "evidence_count": evidence_count,
                    "signal_strength": signal_strength,
                }
            )
            .execute()
        )

        data = response.data or []
        if data and isinstance(data, list):
            row_id = data[0].get("id")
            if row_id:
                logger.info(f"✓ Query record {row_id} stored for user {user_id}")
                return str(row_id)

        logger.warning(f"Query insert returned empty data for user {user_id}")
        return None
    except Exception as exc:
        logger.error(f"✗ Supabase insert_query_record failed for user {user_id}: {exc}", exc_info=True)

    return None


def insert_insight_record(
    user_id: str,
    query_text: str,
    insight: str,
    model_name: str,
    status: str,
    query_id: str | None = None,
) -> str | None:
    client = get_supabase_client()
    if client is None:
        return None

    payload: dict[str, Any] = {
        "user_id": user_id,
        "query_text": query_text,
        "insight": insight,
        "model_name": model_name,
        "status": status,
    }

    if query_id:
        payload["query_id"] = query_id

    try:
        response = client.table("insights").insert(payload).execute()
        data = response.data or []
        if data and isinstance(data, list):
            row_id = data[0].get("id")
            if row_id:
                logger.info(f"✓ Insight record {row_id} stored for user {user_id} (status={status})")
                return str(row_id)

        logger.warning(f"Insight insert returned empty data for user {user_id}")
        return None
    except Exception as exc:
        logger.error(f"✗ Supabase insert_insight_record failed for user {user_id}: {exc}", exc_info=True)

    return None


def list_watchlist(user_id: str) -> list[str]:
    """Return watchlisted companies for user (empty when Supabase disabled)."""
    client = get_supabase_client()
    if client is None or not user_id:
        return []
    try:
        resp = client.table("watchlists").select("company").eq("user_id", user_id).order("created_at").execute()
        return [r.get("company") for r in (resp.data or []) if r.get("company")]
    except Exception as exc:
        logger.debug(f"list_watchlist failed for {user_id}: {exc}")
        return []


def add_watchlist_company(user_id: str, company: str) -> bool:
    client = get_supabase_client()
    if client is None or not user_id or not company:
        return False
    try:
        client.table("watchlists").upsert(
            {"user_id": user_id, "company": company.strip()[:100]}, on_conflict="user_id,company"
        ).execute()
        return True
    except Exception as exc:
        logger.debug(f"add_watchlist failed for {user_id}/{company}: {exc}")
        return False


def remove_watchlist_company(user_id: str, company: str) -> bool:
    client = get_supabase_client()
    if client is None or not user_id or not company:
        return False
    try:
        client.table("watchlists").delete().eq("user_id", user_id).eq("company", company).execute()
        return True
    except Exception as exc:
        logger.debug(f"remove_watchlist failed for {user_id}/{company}: {exc}")
        return False


def list_user_history(user_id: str, kind: str = "queries", limit: int = 10) -> list[dict]:
    """List recent queries or insights for history UI. Returns [] when disabled."""
    client = get_supabase_client()
    if client is None or not user_id:
        return []
    table = "insights" if kind == "insights" else "queries"
    try:
        resp = (
            client.table(table).select("*").eq("user_id", user_id).order("created_at", desc=True).limit(max(1, min(limit, 25))).execute()
        )
        return resp.data or []
    except Exception as exc:
        logger.debug(f"list_user_history({table}) failed for {user_id}: {exc}")
        return []


def create_brief(user_id: str, query_text: str, insight: str, evidence: list[dict] | None = None) -> str | None:
    client = get_supabase_client()
    if client is None or not user_id:
        return None
    try:
        resp = (
            client.table("briefs")
            .insert({"user_id": user_id, "query_text": query_text[:500], "insight": insight[:50000], "evidence": evidence or [], "is_public": True})
            .execute()
        )
        data = resp.data or []
        if data and isinstance(data, list):
            return str(data[0].get("id")) if data[0].get("id") else None
        return None
    except Exception as exc:
        logger.debug(f"create_brief failed for {user_id}: {exc}")
        return None


def get_brief(brief_id: str) -> dict | None:
    client = get_supabase_client()
    if client is None or not brief_id:
        return None
    try:
        resp = client.table("briefs").select("*").eq("id", brief_id).single().execute()
        return resp.data if resp.data else None
    except Exception as exc:
        logger.debug(f"get_brief failed for {brief_id}: {exc}")
        return None


def list_briefs(user_id: str, limit: int = 10) -> list[dict]:
    client = get_supabase_client()
    if client is None or not user_id:
        return []
    try:
        resp = client.table("briefs").select("id,query_text,created_at").eq("user_id", user_id).order("created_at", desc=True).limit(max(1, min(limit, 25))).execute()
        return resp.data or []
    except Exception as exc:
        logger.debug(f"list_briefs failed for {user_id}: {exc}")
        return []


def insert_signal_record(
    user_id: str,
    source: str,
    title: str,
    content: str,
    timestamp: str,
    company: str | None = None,
    event_type: str | None = None,
    url: str | None = None,
) -> str | None:
    client = get_supabase_client()
    if client is None:
        return None

    payload: dict[str, Any] = {
        "user_id": user_id,
        "source": source,
        "title": title,
        "content": content,
        "event_timestamp": timestamp,
        "company": company,
        "event_type": event_type,
        "url": url,
    }

    try:
        response = client.table("signals").insert(payload).execute()
        data = response.data or []
        if data and isinstance(data, list):
            row_id = data[0].get("id")
            if row_id:
                logger.info(f"✓ Signal record {row_id} stored for user {user_id} (source={source})")
                return str(row_id)

        logger.warning(f"Signal insert returned empty data for user {user_id}")
        return None
    except Exception as exc:
        logger.error(f"✗ Supabase insert_signal_record failed for user {user_id}: {exc}", exc_info=True)

    return None
