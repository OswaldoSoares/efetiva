from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from website.facade import cmp


def print_minutas_periodo(contexto):
    descricao_arquivo = f"Minutas Periodo {contexto['inicial']} - {contexto['final']}.pdf"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{descricao_arquivo}"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)

    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)

    pdf.setTitle(descricao_arquivo)
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
