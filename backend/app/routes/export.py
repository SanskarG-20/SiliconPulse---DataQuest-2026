import json
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response

from ..core.auth import get_current_user
from ..models import ExportRequest

router = APIRouter(dependencies=[Depends(get_current_user)])


@router.post("/export")
async def export_analysis(request: ExportRequest):
    """Export the analysis report in the requested format."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"siliconpulse_report_{timestamp}"
        content = ""
        media_type = "text/plain"

        if request.format == "md":
            filename += ".md"
            media_type = "text/markdown"
            content = "# SiliconPulse Intelligence Report\n\n"
            content += f"**Query:** {request.query}\n"
            content += f"**Date:** {datetime.now().isoformat()}\n\n"
            content += f"## Strategic Insight\n\n{request.report}\n\n"

            if request.include_evidence:
                content += "## Evidence\n\n"
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
                "report": request.report
            }
            if request.include_evidence:
                export_data["evidence"] = [item.dict() for item in request.evidence]
            content = json.dumps(export_data, indent=2)

        elif request.format == "txt":
            filename += ".txt"
            media_type = "text/plain"
            content = "SILICONPULSE INTELLIGENCE REPORT\n"
            content += "==============================\n"
            content += f"Query: {request.query}\n"
            content += f"Date: {datetime.now().isoformat()}\n\n"
            content += "STRATEGIC INSIGHT\n"
            content += "-----------------\n"
            content += f"{request.report}\n\n"

            if request.include_evidence:
                content += "EVIDENCE\n"
                content += "--------\n"
                for item in request.evidence:
                    content += f"* {item.title} ({item.source})\n"
                    content += f"  {item.snippet}\n"
                    if item.url:
                        content += f"  Link: {item.url}\n"
                    content += "\n"

        elif request.format == "pdf":
            filename += ".pdf"
            return _pdf_response(filename, request.query, request.report, request.evidence if request.include_evidence else [])

        return Response(
            content=content,
            media_type=media_type,
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )

    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Export failed: {e}")
        raise HTTPException(status_code=500, detail=str(e)) from e


def _pdf_response(filename: str, query: str, report: str, evidence: list) -> Response:
    """Generate a clean single-column PDF with PyMuPDF (no new dependency)."""
    import re
    from datetime import datetime

    from fastapi import Response

    def strip_md(text: str) -> str:
        text = re.sub(r"```.*?```", " ", text or "", flags=re.DOTALL)
        text = re.sub(r"[#>*`_]", "", text)
        text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
        return " ".join(text.split())

    try:
        import fitz  # PyMuPDF (already a backend dependency)

        doc = fitz.open()
        page = doc.new_page(width=595, height=842)  # A4
        margin, y, max_w = 56, 64, 595 - 112

        def draw(text: str, size: int = 11, bold: bool = False, gap: float = 4, color=(0.08, 0.11, 0.18)):
            nonlocal y, page
            # pymupdf built-ins: helv, hebo
            fname = "hebo" if bold else "helv"
            for para in (text or "").split("\n"):
                para = para.strip()
                if not para:
                    y += gap
                    continue
                # crude word-wrap using textbox length estimate
                words, line = para.split(), ""
                for w in words:
                    trial = f"{line} {w}".strip()
                    try:
                        tw = fitz.get_text_length(trial, fontname=fname, fontsize=size)
                    except Exception:
                        tw = len(trial) * size * 0.55
                    if tw > max_w and line:
                        if y > 770:
                            page = doc.new_page(width=595, height=842)
                            y = 64
                        page.insert_text((margin, y), line, fontname=fname, fontsize=size, color=color)
                        y += size + 3.5
                        line = w
                    else:
                        line = trial
                if line:
                    if y > 770:
                        page = doc.new_page(width=595, height=842)
                        y = 64
                    page.insert_text((margin, y), line, fontname=fname, fontsize=size, color=color)
                    y += size + 3.5
                y += gap * 0.5

        draw("SiliconPulse Intelligence Report", size=18, bold=True, gap=2)
        draw(f"Query: {query}  •  {datetime.now().isoformat(timespec='seconds')}", size=9, gap=8, color=(0.35, 0.42, 0.52))
        draw("Strategic Insight", size=13, bold=True, gap=2)
        draw(strip_md(report)[:12000] or "No insight available.", size=11, gap=6)
        if evidence:
            draw("Evidence", size=13, bold=True, gap=2)
            for i, item in enumerate(evidence[:20], 1):
                title = getattr(item, "title", "") or (item.get("title") if isinstance(item, dict) else "")
                source = getattr(item, "source", "") or (item.get("source") if isinstance(item, dict) else "")
                snippet = getattr(item, "snippet", "") or getattr(item, "content", "") or ((item.get("snippet") or item.get("content")) if isinstance(item, dict) else "")
                draw(f"{i}. {strip_md(str(title))} ({strip_md(str(source))})", size=10, bold=True, gap=1)
                if snippet:
                    draw(strip_md(str(snippet))[:800], size=10, gap=5)
        pdf_bytes = doc.tobytes()
        doc.close()
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"PDF render failed, falling back to text: {e}")
        fallback = f"SILICONPULSE INTELLIGENCE REPORT\nQuery: {query}\n\n{report}\n"
        return Response(
            content=fallback,
            media_type="text/plain",
            headers={"Content-Disposition": f"attachment; filename={filename.replace('.pdf', '.txt')}"},
        )
