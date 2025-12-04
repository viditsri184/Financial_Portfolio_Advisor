# backend/routers/report.py

from fastapi import APIRouter, HTTPException, Query, Response

from ..memory.store import memory_store

router = APIRouter(prefix="/download_plan", tags=["report"])


@router.get("")
def download_plan(session_id: str = Query(..., description="User session ID")):
    """
    Generates and returns a financial plan PDF.
    This uses ReportLab for PDF creation.

    You can later upgrade this to a fully styled template-based PDF.
    """
    try:
        # ---------------------------------
        # Fetch memory for this session
        # ---------------------------------
        session_data = memory_store.get_session(session_id)
        entity = session_data.get("entity", {})
        summary = session_data.get("summary", "")

        # ---------------------------------
        # Create PDF with ReportLab
        # ---------------------------------
        from reportlab.pdfgen import canvas
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.units import inch
        from io import BytesIO

        buffer = BytesIO()
        pdf = canvas.Canvas(buffer, pagesize=A4)

        # ---------------------------------
        # Header Section
        # ---------------------------------
        pdf.setFont("Helvetica-Bold", 18)
        pdf.drawString(1 * inch, 10.5 * inch, "Financial Plan Summary")

        pdf.setFont("Helvetica", 11)
        pdf.drawString(1 * inch, 10.1 * inch, f"Session ID: {session_id}")

        # ---------------------------------
        # Memory Data Section
        # ---------------------------------
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(1 * inch, 9.6 * inch, "User Profile & Risk Assessment")

        pdf.setFont("Helvetica", 11)
        y = 9.3 * inch
        for key, val in entity.items():
            pdf.drawString(1 * inch, y, f"{key}: {val}")
            y -= 0.25 * inch
            if y < 1.5 * inch:
                pdf.showPage()
                y = 10.5 * inch

        # ---------------------------------
        # Summary Memory Section
        # ---------------------------------
        pdf.setFont("Helvetica-Bold", 14)
        pdf.drawString(1 * inch, y - 0.3 * inch, "Conversation Summary")

        pdf.setFont("Helvetica", 11)
        y -= 0.6 * inch

        for line in summary.split("\n"):
            pdf.drawString(1 * inch, y, line)
            y -= 0.25 * inch
            if y < 1.5 * inch:
                pdf.showPage()
                y = 10.5 * inch

        pdf.showPage()
        pdf.save()

        pdf_bytes = buffer.getvalue()
        buffer.close()

        # ---------------------------------
        # Return response
        # ---------------------------------
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": 'attachment; filename="financial_plan.pdf"'
            }
        )

    except Exception as ex:
        raise HTTPException(status_code=500, detail=str(ex))
