import os
from datetime import datetime
from io import BytesIO
from turtle import color

from django.core.files.base import ContentFile
from django.http import HttpResponse
from minutas.facade import nome_curto
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from transefetiva.settings.settings import STATIC_ROOT
from website.models import FileUpload

from romaneios.models import NotasOcorrencias


def cmp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def print_multas_pagar(contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="MULTAS A PAGAR.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    header_multas(pdf, contexto)
    multas_pagar(pdf, contexto)
    pdf.setTitle(f"MULTAS.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def header(pdf):
    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    nom_empresa = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    end_empresa = "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010"
    fon_empresa = "(11) 2305-0582 - WHATSAPP (11) 94167-0583"
    ema_empresa = "e-mail: transefetiva@terra.com.br - operacional.efetiva@terra.com.br"
    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)
    pdf.drawImage(url, cmp(12), cmp(265), cmp(40), cmp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawCentredString(cmp(126), cmp(279), nom_empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(273), end_empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(268), fon_empresa)
    pdf.drawCentredString(cmp(126), cmp(263), ema_empresa)
    pdf.line(cmp(10), cmp(260), cmp(200), cmp(260))
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(254.1), cmp(190), cmp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 12)
    return pdf


def header_multas(pdf, contexto):
    return pdf


def multas_pagar(pdf, contexto):
    styles_claro = ParagraphStyle(
        "claro", fontName="Times-Roman", fontSize=8, leading=9, alignment=TA_JUSTIFY
    )
    linha = 251.8
    for x in contexto["multas"]:
        vencimento = datetime.strftime(x["vencimento"], "%d/%m/%Y")
        valor = x["valor"]
        doc = x["doc"]
        ait = x["ait"]
        data_hora = datetime.combine(x["data"], x["hora"])
        str_data_hora = datetime.strftime(data_hora, "%d/%m/%Y %H:%M")
        placa = x["placa"]
        infracao = x["infracao"]
        local = x["local"]
        motorista = x["motorista"]
        codigo = f"{x['digitavel_sp'][0:12]} {x['digitavel_sp'][12:24]} {x['digitavel_sp'][24:36]} {x['digitavel_sp'][36:48]}"
        if x["desconta"]:
            paga = "MOTORISTA"
        else:
            paga = "EMPRESA"
        pdf.setFont("Times-Roman", 8)
        pdf.drawString(
            cmp(12),
            cmp(linha),
            f"VENCIMENTO: {vencimento} - VALOR: R$ {valor} - NÚMERO DOC: {doc} -  NÚMERO AIT: {ait}",
        )
        pdf.drawRightString(cmp(198), cmp(linha), f"DATA: {str_data_hora}")
        if infracao:
            para = Paragraph(infracao, style=styles_claro)
            para.wrapOn(pdf, cmp(186), cmp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, cmp(12), cmp(linha))
        if local:
            para = Paragraph(local, style=styles_claro)
            para.wrapOn(pdf, cmp(186), cmp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, cmp(12), cmp(linha))
        linha -= 3
        pdf.drawString(cmp(12), cmp(linha), f"MOTORISTA: {motorista}")
        pdf.drawRightString(cmp(198), cmp(linha), f"VEÍCULO: {placa}")
        linha -= 3
        pdf.drawString(cmp(12), cmp(linha), f"LINHA DIGITÁVEL: {codigo}")
        pdf.drawRightString(cmp(198), cmp(linha), f"PAGADOR: {paga}")
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha -= 3
        if linha < 38:
            print(linha)
            pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
            multas = str(len(contexto["multas"])).zfill(2)
            pagina = str(pdf.getPageNumber()).zfill(2)
            pdf.drawString(cmp(20), cmp(11), f"{multas} MULTAS")
            pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
            pdf.showPage()
            header(pdf)
            header_multas(pdf, contexto)
            linha = 251.8
    pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
    multas = str(len(contexto["multas"])).zfill(2)
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.drawString(cmp(20), cmp(11), f"{multas} MULTAS")
    pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
    return pdf
