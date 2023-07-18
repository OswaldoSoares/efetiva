from io import BytesIO
from django.core.files.base import ContentFile
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.pagesizes import A4, landscape

from website.facade import cmp
import datetime


def print_minutas_periodo(contexto):
    inicial = datetime.datetime.strptime(contexto["inicial"], "%Y-%m-%d").date()
    inicial = datetime.datetime.strftime(inicial, "%d/%m/%Y")
    final = datetime.datetime.strptime(contexto["final"], "%Y-%m-%d").date()
    final = datetime.datetime.strftime(final, "%d/%m/%Y")
    descricao_arquivo = f"Minutas Periodo {inicial} - {final}"
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="{descricao_arquivo}"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    header(pdf, descricao_arquivo)
    pdf.setTitle(f"{descricao_arquivo}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response

def header(pdf, titulo):
    agora = datetime.datetime.now()
    data_hora = agora.strftime("%d/%m/%Y %H:%M")
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.setFont("Times-Bold", 10)
    pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
    pdf.drawString(cmp(15), cmp(196.4), f"{data_hora}")
    pdf.drawCentredString(cmp(148.5), cmp(196.4), titulo)
    pdf.drawRightString(cmp(282), cmp(196.4), f"PÁGINA: {pagina}")
    pdf.line(cmp(10), cmp(195), cmp(287), cmp(195))
    return pdf

def body(pdf, contexto):
    minutas = contexto["minutas"]
    for x in minutas:
        print(x)
        # minuta = minutas[]
    return pdf