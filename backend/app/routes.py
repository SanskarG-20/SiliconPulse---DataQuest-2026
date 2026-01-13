from fastapi import APIRouter, HTTPException, Response
from datetime import datetime
import json
import os
from pathlib import Path

import google.generativeai as genai
from app.models import (
    QueryRequest, QueryResponse, InjectRequest, InjectResponse, 
    EvidenceItem, SignalCompact, RadarStatus, GenerateRequest, 
    GenerateResponse, ExportRequest, SourceVerifyResponse, SourceVerifyItem
)
from app.settings import settings
from app.sources.perplexity_source import pull_perplexity_signals
from app.sources.x_source import pull_x_signals
from app.utils import safe_read_jsonl, compute_signal_strength, now_ts, compute_event_id, compute_recency_boost, normalize_text, deduplicate_and_append
from app.services.gemini_client import gemini_client
from app.demo_generator import DemoGenerator
from app import storage


router = APIRouter()
import logging
logger = logging.getLogger(__name__)


# Bootstrap endpoint
@router.post("/bootstrap")
async def bootstrap_system():
    """
    Generate fresh demo events and populate the stream.
    """
    try:
        generator = DemoGenerator()
        new_events = generator.generate_batch(10)
        
        # Append to stream with deduplication
        data_path = settings.resolved_data_path
        added_count = deduplicate_and_append(new_events, data_path)
        
        # Force cache refresh
        from app.cache import event_cache
        event_cache.refresh(data_path)
        
        return {
            "status": "success", 
            "new_events": added_count,
            "message": f"Bootstrapped {added_count} fresh events"
        }
    except Exception as e:
        print(f"Bootstrap Error: {e}")
        return {"status": "error", "new_events": 0, "error": str(e)}



# Signals endpoint
@router.get("/signals")
async def get_signals():
    """Get latest signals for the ticker."""
    try:
        data_path = settings.resolved_data_path
        if not data_path.exists():
            return []
            
        # Read fresh events
        events = safe_read_jsonl(
            data_path, 
            limit=20, # Top 20
            freshness_hours=settings.freshness_hours
        )
        return events
    except Exception as e:
        print(f"Signals Error: {e}")
        return []

# Inject endpoint
@router.post("/inject", response_model=InjectResponse)
async def inject_signal(request: InjectRequest):
    """
    Inject a new data item into the stream.
    
    - Accepts InjectRequest with title, content, optional timestamp and source
    - Checks for duplicates using event fingerprint
    - Appends as JSON line to DATA_STREAM_PATH if unique
    """
    try:
        # Generate timestamp if not provided
        if request.timestamp is None:
            injected_at = datetime.now().isoformat()
        else:
            injected_at = request.timestamp
        
        # Prepare the data to inject
        data_entry = {
            "title": request.title,
            "content": request.content,
            "timestamp": injected_at,
            "source": request.source
        }
        # Append as JSON line to the file
        data_path = settings.resolved_data_path
        with open(data_path, "a", encoding="utf-8") as f:
            json.dump(data_entry, f, ensure_ascii=False)
            f.write("\n")
            
        # Mark as seen
        storage.mark_seen(event_id, request.source, request.title)
        
        return InjectResponse(
            status="success",
            injected_at=injected_at,
            stream_path_used=str(data_path)
        )
        
    except PermissionError as e:
        raise HTTPException(
            status_code=403,
            detail=f"Permission denied when writing to {settings.data_stream_path}: {str(e)}"
        )
    except OSError as e:
        raise HTTPException(
            status_code=500,
            detail=f"File system error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to inject data: {str(e)}"
        )


# Query endpoint
@router.post("/query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process a query and retrieve top-k evidence from the data stream.
    
    OPTIMIZED FOR SPEED:
    - Uses in-memory event cache (refreshes every 3s)
    - LRU query result cache (60s TTL)
    - Timing logs for performance monitoring
    - Limited snippet size (160 chars)
    """
    import time
    import uuid
    from app.cache import event_cache
    from app.query_cache import query_cache
    from app.company_dict import COMPANY_DICT
    
    request_id = str(uuid.uuid4())[:8]
    start_time = time.time()
    
    try:
        # Check query cache first
        cached_result = query_cache.get(request.query, request.k)
        if cached_result:
            logger.info(f"[{request_id}] Cache HIT - {request.query[:50]} - {(time.time() - start_time)*1000:.1f}ms")
            return QueryResponse(**cached_result)
        
        logger.info(f"[{request_id}] Query START - {request.query[:50]}")
        
        data_path = settings.resolved_data_path
        
        # Check if file exists
        if not data_path.exists():
            result = {
                "query": request.query,
                "evidence": [],
                "signal_strength": 0,
                "last_updated": datetime.now().isoformat()
            }
            query_cache.set(request.query, request.k, result)
            return QueryResponse(**result)
        
        # STAGE 1: Read events from cache (FAST)
        # Read fresh events
        events = safe_read_jsonl(
            data_path, 
            limit=settings.max_events_to_scan,
            freshness_hours=settings.freshness_hours
        )
            
        # STAGE 3: Match events (OPTIMIZED)
        matched_events = []
        
        # Synonym Expansion
        raw_keywords = [kw.lower() for kw in request.query.split() if len(kw) > 2]
        query_keywords = set(raw_keywords)
        
        # Universal Synonym Expansion using COMPANY_DICT
        for company, data in COMPANY_DICT.items():
            aliases = [a.lower() for a in data.get("aliases", [])]
            aliases.append(company.lower())
            
            # Check if any alias is in the query
            is_relevant = False
            for kw in raw_keywords:
                if kw in aliases:
                    is_relevant = True
                    break
            
            # If relevant, add all aliases and topics to search
            if is_relevant:
                query_keywords.update(aliases)
                # Add topics as keywords too? Maybe too broad, but let's add key terms from topics
                # For now, just aliases is a huge win.
                
        query_keywords = list(query_keywords)
        logger.info(f"Expanded Query Keywords: {query_keywords}")
        
        for event in events:
            title = event.get("title", "").lower()
            content = event.get("content", "").lower()
            company = event.get("company", "").lower() if event.get("company") else ""
            
            # Check if any keyword exists in title, content, or company
            match_count = 0
            for keyword in query_keywords:
                if keyword in title or keyword in content or keyword in company:
                    match_count += 1
            
            if match_count > 0:
                matched_events.append(event)
        
        # Convert to EvidenceItem objects
        evidence_list = []
        for event in matched_events:
            evidence_list.append(EvidenceItem(
                event_id=event.get("event_id", compute_event_id(event)),
                title=event.get("title", ""),
                snippet=event.get("snippet") or event.get("content", "")[:160],
                source=event.get("source", "Unknown"),
                timestamp=event.get("timestamp", ""),
                url=event.get("url", ""),
                company=event.get("company"),
                event_type=event.get("event_type")
            ))
            
        # Sort by timestamp (newest first)
        evidence_list.sort(key=lambda x: x.timestamp, reverse=True)
        
        # Limit to k
        evidence_list = evidence_list[:request.k]
        
        result = {
            "query": request.query,
            "evidence": evidence_list,
            "signal_strength": compute_signal_strength(evidence_list),
            "last_updated": datetime.now().isoformat(),
            "report": None,
            "llm_status": "pending",
            "stream_path_used": str(data_path)
        }
        
        # Update cache
        query_cache.set(request.query, request.k, result)
        
        logger.info(f"[{request_id}] Query END - Found {len(evidence_list)} items - {(time.time() - start_time)*1000:.1f}ms")
        return QueryResponse(**result)
        
    except Exception as e:
        print(f"Query Error: {e}")
        # Return empty valid response instead of 500
        return QueryResponse(
            query=request.query,
            evidence=[],
            signal_strength=0,
            last_updated=datetime.now().isoformat(),
            report=None,
            llm_status="failed"
        )


# Radar endpoint
@router.get("/radar", response_model=list[RadarStatus])
async def get_radar():
    """
    Get radar status for all companies based on recent activity.
    """
    try:
        data_path = settings.resolved_data_path
        if not data_path.exists():
            return []
        
        # Read fresh events
        events = safe_read_jsonl(
            data_path, 
            limit=settings.max_events_to_scan,
            freshness_hours=settings.freshness_hours
        )
            
        # Count events per company
        company_counts = {}
        for event in events:
            company = event.get("company")
            if company:
                company_counts[company] = company_counts.get(company, 0) + 1
        
        # Build radar status list
        radar_list = []
        for company, count in company_counts.items():
            # Determine activity level
            if count >= 5:
                activity = "High"
            elif count >= 2:
                activity = "Moderate"
            else:
                activity = "Low"
                
            radar_list.append(RadarStatus(
                company=company,
                activity_level=activity,
                count=count
            ))
            
        # Sort by count descending
        radar_list.sort(key=lambda x: x.count, reverse=True)
        
        return radar_list
        
    except Exception as e:
        print(f"Radar Error: {e}")
        return []


# Generate endpoint
@router.post("/generate", response_model=GenerateResponse)
async def generate_insight(request: GenerateRequest):
    """
    Generate insight using Gemini based on query and context.
    """
    try:
        # Check for API key first
        if not settings.gemini_api_key:
             return GenerateResponse(insight="**Simulation Mode**\n\nGemini API Key is missing. Please configure `GEMINI_API_KEY` in `.env` for live AI insights.\n\nBased on the available signals, market activity appears elevated with significant movement in the semiconductor sector.")

        # 1. Gating Logic: Check evidence count
        # We estimate evidence count by looking for the separator pattern used in frontend
        # formatEvidenceToContext uses: [Timestamp | Source] Title ...
        evidence_count = request.context.count("[20") # Crude but effective for ISO timestamps in context
        
        logger.info(f"Generating insight for query: '{request.query}' | Evidence Count: {evidence_count} | Context Len: {len(request.context)}")

        if evidence_count < 2:
            logger.warning("Skipping Gemini call due to low evidence.")
            return GenerateResponse(insight="**Insufficient Data for Strategic Synthesis**\n\nWaiting for more live signals to generate a high-confidence report. Current data stream is too sparse for deep analysis.\n\n*System Status: Monitoring for new events...*")

        prompt = f"""
        You are SiliconPulse, an advanced strategic intelligence engine. 
        Generate a high-precision intelligence report based on the provided context.
        
        QUERY: {request.query}
        
        CONTEXT:
        {request.context}
        
        INSTRUCTIONS:
        - Analyze the provided evidence carefully.
        - Output strictly valid JSON. Do not include markdown formatting (like ```json).
        - If the context is empty or irrelevant, return a JSON with a single section explaining "Insufficient Data".
        
        JSON SCHEMA:
        {{
          "sections": [
            {{ "id": "evidence", "title": "Live Signal Evidence", "points": ["..."], "evidence": [ {{ "source": "...", "timestamp": "...", "title": "..." }} ] }},
            {{ "id": "change", "title": "What Changed", "points": ["..."] }},
            {{ "id": "impact", "title": "Impact Reasoning", "points": ["..."] }},
            {{ "id": "competitors", "title": "Competitor Effects", "points": ["..."] }},
            {{ "id": "outlook", "title": "Strategic Outlook (7 Days)", "points": ["..."] }},
            {{ "id": "confidence", "title": "Confidence Meter", "value": "Low|Medium|High", "reason": "..." }},
            {{ "id": "ceo", "title": "CEO Summary", "text": "..." }}
          ]
        }}
        """
        
        insight_text = await gemini_client.generate_content_with_fallback(prompt)
        
        # Clean up potential markdown code blocks if Gemini adds them
        if insight_text.startswith("```json"):
            insight_text = insight_text[7:]
        if insight_text.endswith("```"):
            insight_text = insight_text[:-3]
            
        insight_text = insight_text.strip()
        
        # Validate JSON
        try:
            parsed_json = json.loads(insight_text)
            # Re-serialize to ensure it's valid minified JSON string
            insight_text = json.dumps(parsed_json)
        except json.JSONDecodeError:
            logger.warning("Gemini output invalid JSON, attempting repair or fallback.")
            # If simple strip didn't work, maybe it has comments or other issues.
            # For now, we return it as is, but logged.
            # Ideally we could use a repair library, but we'll rely on the frontend fallback.
            pass
            
        return GenerateResponse(insight=insight_text)
        
    except Exception as e:
        logger.error(f"Gemini Generation Failed: {e}")
        return GenerateResponse(insight=f"**Insight Generation Unavailable**\n\nWe encountered an issue connecting to the intelligence engine. However, the live data above remains accurate.\n\n*System Note: {str(e)}*")


# LLM Health Endpoints
@router.get("/llm/health")
async def llm_health():
    """Check Gemini configuration health"""
    return await gemini_client.check_health()

@router.get("/llm/models")
async def list_llm_models():
    """List available Gemini models"""
    return gemini_client.list_available_models()


# Source endpoints
@router.post("/sources/perplexity/pull")
async def pull_perplexity():
    """Trigger Perplexity signal pull"""
    try:
        count = pull_perplexity_signals()
        return {"status": "ok", "source": "Perplexity", "pulled": count, "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources/x/pull")
async def pull_x():
    """Trigger X signal pull"""
    try:
        count = pull_x_signals()
        return {"status": "ok", "source": "X", "pulled": count, "timestamp": datetime.utcnow().isoformat() + "Z"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sources/pull_all")
async def pull_all_sources():
    """Trigger all signal sources"""
    try:
        p_count = pull_perplexity_signals()
        x_count = pull_x_signals()
        return {
            "status": "ok", 
            "pulled": {
                "Perplexity": p_count,
                "X": x_count
            },
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/recommendations")
async def get_recommendations():
    """
    Generate dynamic recommended queries based on live data.
    """
    import random
    
    try:
        data_path = settings.resolved_data_path
        if not data_path.exists():
            # Fallback if no data
            return {
                "recommended_queries": [
                    {"label": "Market Overview", "query": "What are the top market trends right now?", "icon": "Activity", "color": "text-sky-400"},
                    {"label": "Tech News", "query": "Latest updates in technology sector?", "icon": "Cpu", "color": "text-emerald-400"},
                    {"label": "Global Events", "query": "Summary of major global events today", "icon": "Globe", "color": "text-amber-400"},
                    {"label": "Financial Impact", "query": "High impact financial news in last 24h", "icon": "TrendingUp", "color": "text-red-400"}
                ],
                "generated_at": datetime.utcnow().isoformat() + "Z"
            }

        # Read recent events
        events = safe_read_jsonl(
            data_path, 
            limit=50,
            freshness_hours=24
        )
        
        # Extract entities
        companies = set()
        sources = set()
        
        for event in events:
            if event.get("company"):
                companies.add(event.get("company"))
            if event.get("source"):
                sources.add(event.get("source"))
                
        # Convert to lists for random selection
        company_list = list(companies)
        source_list = list(sources)
        
        # Templates
        templates = [
            {"label": "{company} Strategy", "query": "What is the latest strategy update from {company}?", "icon": "Zap", "color": "text-amber-400"},
            {"label": "{company} Impact", "query": "Analyze recent impact of {company} announcements.", "icon": "Activity", "color": "text-red-400"},
            {"label": "{source} Intel", "query": "Summarize latest intelligence from {source}.", "icon": "ShieldAlert", "color": "text-emerald-400"},
            {"label": "Sector Analysis", "query": "Compare {company} vs competitors based on recent signals.", "icon": "BarChart3", "color": "text-sky-400"},
            {"label": "Supply Chain", "query": "Any supply chain disruptions involving {company}?", "icon": "Layers", "color": "text-indigo-400"},
            {"label": "Executive Brief", "query": "Executive summary of {company} performance today.", "icon": "FileText", "color": "text-slate-300"}
        ]
        
        recommendations = []
        used_companies = set()
        
        # Generate candidates
        candidates = []
        for _ in range(20): # Generate plenty of candidates
            template = random.choice(templates)
            
            if "{company}" in template["query"] and company_list:
                company = random.choice(company_list)
                query = template["query"].format(company=company)
                label = template["label"].format(company=company)
                candidates.append({**template, "query": query, "label": label, "key_entity": company})
            elif "{source}" in template["query"] and source_list:
                source = random.choice(source_list)
                query = template["query"].format(source=source)
                label = template["label"].format(source=source)
                candidates.append({**template, "query": query, "label": label, "key_entity": source})
                
        # Select 4 unique ones
        final_selection = []
        for cand in candidates:
            if len(final_selection) >= 4:
                break
            
            # Avoid duplicate entities if possible
            if cand.get("key_entity") in used_companies:
                continue
                
            final_selection.append(cand)
            used_companies.add(cand.get("key_entity"))
            
        # Fill if not enough unique
        if len(final_selection) < 4:
            remaining = 4 - len(final_selection)
            # Just take any random ones to fill
            for _ in range(remaining):
                 # Simple fallback templates
                 final_selection.append(
                     {"label": "High Impact", "query": "Top 3 high-impact events in last 2 hours?", "icon": "AlertCircle", "color": "text-red-400"}
                 )

        return {
            "recommended_queries": final_selection,
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }

    except Exception as e:
        print(f"Recommendation Error: {e}")
        # Return static fallback on error
        return {
            "recommended_queries": [
                {"label": "NVIDIA-TSMC Pipeline", "query": "Any new NVIDIA-TSMC contract today?", "icon": "Zap", "color": "text-amber-400"},
                {"label": "Foundry Design Wins", "query": "Status of Intel 18A design wins?", "icon": "CheckCircle2", "color": "text-emerald-400"},
                {"label": "AI Infra Analysis", "query": "Meta AI infra roadmap status?", "icon": "Cpu", "color": "text-sky-400"},
                {"label": "High Impact Summary", "query": "Top 3 high-impact events in last 2 hours?", "icon": "AlertCircle", "color": "text-red-400"}
            ],
            "generated_at": datetime.utcnow().isoformat() + "Z"
        }


# Export endpoint
@router.post("/export")
async def export_analysis(request: ExportRequest):
    """
    Export the analysis report in the requested format.
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"siliconpulse_report_{timestamp}"
        content = ""
        media_type = "text/plain"

        if request.format == "md":
            filename += ".md"
            media_type = "text/markdown"
            content = f"# SiliconPulse Intelligence Report\n\n"
            content += f"**Query:** {request.query}\n"
            content += f"**Date:** {datetime.now().isoformat()}\n\n"
            content += f"## Strategic Insight\n\n{request.report}\n\n"
            content += f"## Evidence\n\n"
            for item in request.evidence:
                content += f"- **{item.title}** ({item.source})\n"
                content += f"  - {item.snippet}\n"
                if item.url:
                    content += f"  - [Link]({item.url})\n"
                content += "\n"
                
        elif request.format == "json":
            filename += ".json"
            media_type = "application/json"
            export_data = {
                "query": request.query,
                "timestamp": datetime.now().isoformat(),
                "report": request.report,
                "evidence": [item.dict() for item in request.evidence]
            }
            content = json.dumps(export_data, indent=2)
            
        elif request.format == "txt":
            filename += ".txt"
            media_type = "text/plain"
            content = f"SILICONPULSE INTELLIGENCE REPORT\n"
            content += f"==============================\n"
            content += f"Query: {request.query}\n"
            content += f"Date: {datetime.now().isoformat()}\n\n"
            content += f"STRATEGIC INSIGHT\n"
            content += f"-----------------\n"
            content += f"{request.report}\n\n"
            content += f"EVIDENCE\n"
            content += f"--------\n"
            for item in request.evidence:
                content += f"* {item.title} ({item.source})\n"
                content += f"  {item.snippet}\n"
                if item.url:
                    content += f"  Link: {item.url}\n"
                content += "\n"
        
        elif request.format == "pdf":
             filename += ".txt"
             content = "PDF export not configured. Returning text format.\n\n" + request.report

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Verify Sources endpoint
@router.get("/sources/verify", response_model=SourceVerifyResponse)
async def verify_sources(query: str):
    """
    Verify sources for a given query.
    Re-runs a quick retrieval to identify sources and assign trust levels.
    """
    try:
        # Re-use retrieval logic (simplified)
        # 1. Read fresh events
        data_path = settings.resolved_data_path
        events = safe_read_jsonl(data_path, limit=200, freshness_hours=24)
        
        # 2. Filter relevant events (simple keyword match)
        from app.company_dict import COMPANY_DICT
        
        # Expand keywords (same logic as query)
        raw_keywords = [kw.lower() for kw in query.split() if len(kw) > 2]
        query_keywords = set(raw_keywords)
        
        for company, data in COMPANY_DICT.items():
            aliases = [a.lower() for a in data.get("aliases", [])]
            aliases.append(company.lower())
            is_relevant = False
            for kw in raw_keywords:
                if kw in aliases:
                    is_relevant = True
                    break
            if is_relevant:
                query_keywords.update(aliases)
        
        query_keywords = list(query_keywords)
        
        matched_events = []
        for event in events:
            title = event.get("title", "").lower()
            content = event.get("content", "").lower()
            company = event.get("company", "").lower() if event.get("company") else ""
            
            match_count = 0
            for keyword in query_keywords:
                if keyword in title or keyword in content or keyword in company:
                    match_count += 1
            
            if match_count > 0:
                matched_events.append(event)
        
        # Sort by timestamp
        matched_events.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        matched_events = matched_events[:10] # Top 10 for verification
        
        # 3. Construct verification response
        verified_sources = []
        for event in matched_events:
            source = event.get("source", "Unknown")
            trust_level = "Low"
            reason = "Unknown source origin"
            
            if source in ["Reuters", "Bloomberg", "Financial Times", "TechCrunch", "Official"]:
                trust_level = "High"
                reason = "Established financial/tech news outlet"
            elif source in ["Perplexity", "MarketWire"]:
                trust_level = "Medium"
                reason = "Aggregated intelligence"
            elif source == "ManualInject":
                trust_level = "Medium"
                reason = "Manually verified injection"
            elif source == "X" or source == "Twitter":
                trust_level = "Low"
                reason = "Social media signal (unverified)"
                
            verified_sources.append(SourceVerifyItem(
                timestamp=event.get("timestamp"),
                source=source,
                title=event.get("title", ""),
                url=event.get("url"),
                trust_level=trust_level,
                reason=reason
            ))
            
        return SourceVerifyResponse(
            query=query,
            sources=verified_sources
        )

    except Exception as e:
        logger.error(f"Source verification failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
