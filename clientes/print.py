"""
    Módulo de Impressão
"""
from io import BytesIO
import datetime
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from website.facade import cmp
from website.print import header


linha = 297  # pylint: disable=C0103


def ficha_cadastral(contexto):
    cliente = contexto["cliente"][0]
    telefones = contexto["fone_cliente"]
    emails = contexto["email_cliente"]
    cobranca = contexto["cobranca_cliente"]
    tabela = contexto["tabela_cliente"][0]
    veiculos = contexto["tabela_veiculo_cliente"]
    perimetros = contexto["tabela_perimetro_cliente"]
    capacidades = contexto["tabela_capacidade_cliente"]
    fantasia = cliente["Fantasia"]
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'filename="FICHA CADASTRAL {fantasia}.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    pdf.setTitle(f"FICHA CADASTRAL {fantasia}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
