from __future__ import annotations

import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch


def text_to_pdf_bytes(title: str, text: str) -> bytes:
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    width, height = letter

    margin = 0.75 * inch
    y = height - margin

    c.setFont("Helvetica-Bold", 14)
    c.drawString(margin, y, title)
    y -= 0.35 * inch

    c.setFont("Courier", 9)
    for line in text.splitlines():
        if y < margin:
            c.showPage()
            c.setFont("Courier", 9)
            y = height - margin
        c.drawString(margin, y, line[:120])
        y -= 0.16 * inch

    c.showPage()
    c.save()
    return buf.getvalue()
