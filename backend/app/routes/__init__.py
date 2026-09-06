from fastapi import APIRouter

from ..graph.routes import router as graph_router
from .auth import router as auth_router
from .briefs import router as briefs_router
from .comments import router as comments_router
from .compare import router as compare_router
from .diagnostics import router as diagnostics_router
from .digest import router as digest_router
from .export import router as export_router
from .history import router as history_router
from .ingest import router as ingest_router
from .keys import router as keys_router
from .llm import router as llm_router
from .query import router as query_router
from .recommendations import router as recommendations_router
from .rss import router as rss_router
from .signals import router as signals_router
from .sources import router as sources_router
from .trends import router as trends_router
from .videos import router as videos_router
from .watchlist import router as watchlist_router
from .webhooks import router as webhooks_router
from .workspaces import router as workspaces_router

router = APIRouter(dependencies=[])
router.include_router(auth_router, prefix="/auth", tags=["auth"])
router.include_router(watchlist_router, prefix="", tags=["watchlist"])
router.include_router(briefs_router, prefix="", tags=["briefs"])
router.include_router(history_router, prefix="", tags=["history"])
router.include_router(digest_router, prefix="", tags=["digest"])
router.include_router(keys_router, prefix="", tags=["keys"])
router.include_router(webhooks_router, prefix="", tags=["webhooks"])
router.include_router(workspaces_router, prefix="", tags=["workspaces"])
router.include_router(signals_router, prefix="", tags=["signals"])
router.include_router(rss_router, prefix="", tags=["rss"])
router.include_router(compare_router, prefix="", tags=["compare"])
router.include_router(comments_router, prefix="", tags=["comments"])
router.include_router(trends_router, prefix="", tags=["trends"])
router.include_router(query_router, prefix="", tags=["query"])
router.include_router(sources_router, prefix="/sources", tags=["sources"])
router.include_router(export_router, prefix="", tags=["export"])
router.include_router(recommendations_router, prefix="", tags=["recommendations"])
router.include_router(diagnostics_router, prefix="/user", tags=["diagnostics"])
router.include_router(llm_router, prefix="/llm", tags=["llm"])
router.include_router(graph_router, prefix="/graph", tags=["graph"])
router.include_router(ingest_router, prefix="/ingest", tags=["ingest"])
router.include_router(videos_router, prefix="", tags=["videos"])
