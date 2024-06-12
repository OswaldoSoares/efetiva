"""
    Módulo de Impressão
"""
from io import BytesIO
import datetime
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from website.print import header


def ficha_cadastral(cliente):
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'filename="Ficha Cadastral {cliente}.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    pdf.setTitle(f"FICHA CADASTRAL {cliente}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
