from fastapi import APIRouter, HTTPException
from datetime import datetime
import json
import os
from pathlib import Path

import google.generativeai as genai
from app.models import QueryRequest, QueryResponse, InjectRequest, InjectResponse, EvidenceItem, SignalCompact, RadarStatus, GenerateRequest, GenerateResponse
from app.models import QueryRequest, QueryResponse, InjectRequest, InjectResponse, EvidenceItem, SignalCompact, RadarStatus, GenerateRequest, GenerateResponse
from app.settings import settings
from app.sources.perplexity_source import pull_perplexity_signals
from app.sources.x_source import pull_x_signals
from app.utils import safe_read_jsonl, compute_signal_strength, now_ts
from app.services.gemini_client import gemini_client

router = APIRouter()


# Inject endpoint
@router.post("/inject", response_model=InjectResponse)
async def inject_signal(request: InjectRequest):
    """
    Inject a new data item into the stream.
    
    - Accepts InjectRequest with title, content, optional timestamp and source
    - Appends as JSON line to DATA_STREAM_PATH
    - Generates timestamp if not provided
    - Creates file if it doesn't exist
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
        
        # Get the data stream path from settings
        data_path = Path(settings.data_stream_path)
        
        # Create parent directories if they don't exist
        data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Append as JSON line to the file
        with open(data_path, "a", encoding="utf-8") as f:
            json.dump(data_entry, f, ensure_ascii=False)
            f.write("\n")
        
        return InjectResponse(
            status="success",
            injected_at=injected_at
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
    """
    try:
        data_path = Path(settings.data_stream_path)
        
        # Safe read
        events = safe_read_jsonl(data_path, limit=200)
        
        # Extract keywords
        query_keywords = [kw.lower() for kw in request.query.split() if len(kw) > 2]
        
        if not query_keywords:
            return QueryResponse(
                query=request.query,
                evidence=[],
                signal_strength=0,
                last_updated=now_ts()
            )
        
        # Match events
        matched_events = []
        for event in events:
            title = event.get("title", "").lower()
            content = event.get("content", "").lower()
            
            match_count = 0
            for keyword in query_keywords:
                if keyword in title or keyword in content:
                    match_count += 1
            
            if match_count > 0:
                matched_events.append({
                    "event": event,
                    "match_score": match_count
                })
        
        # Sort and top-k
        matched_events.sort(key=lambda x: x["match_score"], reverse=True)
        top_k_events = matched_events[:request.k]
        
        # Build evidence list
        evidence_list = []
        for matched in top_k_events:
            event = matched["event"]
            evidence_list.append(EvidenceItem(
                timestamp=event.get("timestamp"),
                source=event.get("source"),
                title=event.get("title", ""),
                snippet=event.get("content", "")[:200],
                company=event.get("company"),
                event_type=event.get("event_type")
            ))
        
        # Compute signal strength
        signal_strength = compute_signal_strength(evidence_list)
        
        return QueryResponse(
            query=request.query,
            evidence=evidence_list,
            signal_strength=signal_strength,
            last_updated=now_ts()
        )
        
    except Exception as e:
        # Log error but return valid response
        print(f"Error in process_query: {e}")
        return QueryResponse(
            query=request.query,
            evidence=[],
            signal_strength=0,
            last_updated=now_ts()
        )
    """
    Process a query and retrieve top-k evidence from the data stream.
    
    - Retrieves latest ~200 events from stream.jsonl
    - Simple keyword matching in title/content
    - Returns top-k evidence with signal strength score
    """
    try:
        data_path = Path(settings.data_stream_path)
        
        # Check if file exists
        if not data_path.exists():
            return QueryResponse(
                query=request.query,
                evidence=[],
                signal_strength=0,
                last_updated=datetime.now().isoformat()
            )
        
        # Read the latest ~200 events from the stream
        events = []
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                # Read all lines and take the last 200
                all_lines = f.readlines()
                recent_lines = all_lines[-200:] if len(all_lines) > 200 else all_lines
                
                for line in recent_lines:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading data stream: {str(e)}"
            )
        
        # Extract keywords from query (simple split by whitespace and lowercase)
        query_keywords = [kw.lower() for kw in request.query.split() if len(kw) > 2]
        
        if not query_keywords:
            return QueryResponse(
                query=request.query,
                evidence=[],
                signal_strength=0,
                last_updated=datetime.now().isoformat()
            )
        
        # Match events based on keyword presence in title/content
        matched_events = []
        for event in events:
            title = event.get("title", "").lower()
            content = event.get("content", "").lower()
            
            # Check if any keyword exists in title or content
            match_count = 0
            for keyword in query_keywords:
                if keyword in title or keyword in content:
                    match_count += 1
            
            if match_count > 0:
                matched_events.append({
                    "event": event,
                    "match_score": match_count
                })
        
        # Sort by match score (descending) and take top-k
        matched_events.sort(key=lambda x: x["match_score"], reverse=True)
        top_k_events = matched_events[:request.k]
        
        # Build evidence list
        evidence_list = []
        for matched in top_k_events:
            event = matched["event"]
            evidence_list.append(EvidenceItem(
                timestamp=event.get("timestamp"),
                source=event.get("source"),
                title=event.get("title", ""),
                snippet=event.get("content", "")[:200],  # Limit snippet to 200 chars
                company=event.get("company"),
                event_type=event.get("event_type")
            ))
        
        # Calculate signal strength (0-100)
        # Based on: number of matches and recency
        if len(evidence_list) == 0:
            signal_strength = 0
        else:
            # Base score on evidence count (max 50 points)
            count_score = min(len(evidence_list) * 10, 50)
            
            # Recency bonus (max 50 points) - more recent events get higher score
            recency_score = 50 if len(evidence_list) > 0 else 0
            
            signal_strength = min(count_score + recency_score, 100)
        
        return QueryResponse(
            query=request.query,
            evidence=evidence_list,
            signal_strength=signal_strength,
            last_updated=datetime.now().isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Query processing failed: {str(e)}"
        )


# Signals endpoint
# Signals endpoint
@router.get("/signals", response_model=list[SignalCompact])
async def get_signals():
    """
    Get latest signals from the data stream.
    
    - Returns latest 10 events
    - Sorted by timestamp (newest first)
    - Compact format
    """
    try:
        data_path = Path(settings.data_stream_path)
        
        if not data_path.exists():
            return []
        
        signals = []
        with open(data_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    try:
                        event = json.loads(line)
                        signals.append(SignalCompact(
                            timestamp=event.get("timestamp"),
                            company=event.get("company"),
                            event_type=event.get("event_type"),
                            title=event.get("title", ""),
                            source=event.get("source")
                        ))
                    except json.JSONDecodeError:
                        continue
        
        # Sort by timestamp descending (newest first)
        # Handle None timestamps by treating them as oldest
        signals.sort(key=lambda x: x.timestamp or "", reverse=True)
        
        return signals[:10]  # Return top 10
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve signals: {str(e)}"
        )


# Radar endpoint
@router.get("/radar", response_model=list[RadarStatus])
async def get_radar():
    """
    Get radar status for all companies based on recent activity.
    
    - Analyzes last 200 events
    - Counts events per company
    - Determines activity level (High/Moderate/Low)
    - Returns list sorted by count (descending)
    """
    try:
        data_path = Path(settings.data_stream_path)
        
        if not data_path.exists():
            return []
        
        # Read the latest ~200 events from the stream
        events = []
        try:
            with open(data_path, "r", encoding="utf-8") as f:
                # Read all lines and take the last 200
                all_lines = f.readlines()
                recent_lines = all_lines[-200:] if len(all_lines) > 200 else all_lines
                
                for line in recent_lines:
                    line = line.strip()
                    if line:
                        try:
                            event = json.loads(line)
                            events.append(event)
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error reading data stream: {str(e)}"
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
            if count >= 8:
                activity = "High"
            elif count >= 3:
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
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve radar data: {str(e)}"
        )


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

        prompt = f"""
        You are SiliconPulse, an advanced strategic intelligence engine. 
        Generate a high-precision intelligence report based ONLY on the provided context.
        
        QUERY: {request.query}
        
        CONTEXT:
        {request.context}
        
        INSTRUCTIONS:
        - Do not hallucinate. If the context is empty or insufficient, state "Insufficient Intelligence Signal".
        - Use a professional, executive-briefing tone.
        - Format the output in Markdown.
        
        REPORT STRUCTURE:
        
        ### 1. Live Signal Evidence
        - List the specific data points used (timestamps, sources).
        
        ### 2. What Changed (Before vs After)
        - Contrast the new signal against the previous baseline or expectations.
        
        ### 3. Impact Reasoning
        - Analyze the Business, Technical, and Supply Chain implications.
        
        ### 4. Competitor Effects
        - Who gains? Who loses? (e.g., TSMC vs Intel vs Samsung).
        
        ### 5. Strategic Outlook (Next 7 Days)
        - Infer the immediate next steps or market reactions.
        
        ### 6. Confidence Meter
        - Rate confidence (Low/Medium/High) based on source reliability and signal strength.
        
        ### 7. CEO Summary
        - A single sentence bottom-line for executive leadership.
        """
        
        insight_text = gemini_client.generate_content_with_fallback(prompt)
        return GenerateResponse(insight=insight_text)
        
    except Exception as e:
        print(f"Gemini Generation Failed: {e}")
        return GenerateResponse(insight=f"**Insight Generation Unavailable**\n\nWe encountered an issue connecting to the intelligence engine. However, the live data above remains accurate.\n\n*System Note: {str(e)}*")


# LLM Health Endpoints
@router.get("/llm/health")
async def llm_health():
    """Check Gemini configuration health"""
    return gemini_client.check_health()

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
