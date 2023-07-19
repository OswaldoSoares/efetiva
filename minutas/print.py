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
    body(pdf, contexto, descricao_arquivo)
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
    pdf.setFont("Courier-Bold", 9)
    pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
    pdf.drawString(cmp(15), cmp(196.4), f"{data_hora}")
    pdf.drawCentredString(cmp(148.5), cmp(196.4), titulo)
    pdf.drawRightString(cmp(282), cmp(196.4), f"PÁGINA: {pagina}")
    pdf.line(cmp(10), cmp(195), cmp(287), cmp(195))
    return pdf


def body(pdf, contexto, titulo):
    minutas = contexto["minutas"]
    linha = 194
    for x in minutas:
        if linha <= 20:
            pdf.showPage()
            header(pdf, titulo)
            linha = 194
        data = x["data"].strftime("%d/%m/%Y")
        minuta = x["numero"]
        status_minuta = x["status_minuta"]
        cliente = x["cliente"]
        solicitado = x["veiculo_solicitado"]
        motorista = None
        if x["motorista"]:
            motorista = x["motorista"][0]["apelido"]
        placa = x["veiculo"]
        seguro = f'{x["recebe"]["t_segu"]:.2f}'.replace('.', ',')
        romaneios = None
        if x["romaneio"]:
            romaneios = ', '.join(map(str, x["romaneio"])).replace('[', '').replace(']', '')
        ajudantes = []
        if x["ajudantes"]:
            for y in x["ajudantes"]:
                ajudantes.append(y["apelido"])
        else:
            ajudantes.append("NENHUM AJUDANTE INSERIDO")
        ajudantes = ', '.join(map(str, ajudantes)).replace('[', '').replace(']', '')
        despesas = []
        if x["despesas"]:
            for y in x["despesas"]:
                despesas.append(f'{y["Descricao"]} - R$ {y["Valor"]}')
        despesas = ', '.join(map(str, despesas)).replace('[', '').replace(']', '')
        entregas = x["quantidade_entregas"]
        peso = f'{x["t_entregas"]["peso_entregas"]:.3f}'.replace('.', ',')
        calculo = f'{x["recebe_minuta"]:.2f}'.replace('.', ',')
        valor_minuta = f'{x["valor_minuta"]:.2f}'.replace('.', ',')
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(12), cmp(linha-4), cmp(275), cmp(4), fill=1, stroke=0)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawString(cmp(12), cmp(linha-3), f"{data}")
        pdf.drawString(cmp(33), cmp(linha-3), f"{minuta}")
        pdf.drawString(cmp(43), cmp(linha-3), f"{status_minuta}")
        pdf.drawString(cmp(65), cmp(linha-3), f"{cliente}")
        pdf.drawString(cmp(125), cmp(linha-3), f"{solicitado}")
        if motorista:
            pdf.drawString(cmp(175), cmp(linha-3), f"{motorista}")
        pdf.drawString(cmp(230), cmp(linha-3), f"{placa}")
        pdf.drawRightString(cmp(285), cmp(linha-3), f"Seguro: R$ {seguro}")
        linha -= 3.5
        pdf.drawString(cmp(12), cmp(linha-3), f"AJs: {ajudantes}")
        if romaneios:
            pdf.drawString(cmp(130), cmp(linha-3), f"Romaneios: {romaneios} - Peso: {peso} - Entregas: {entregas}")
        pdf.drawRightString(cmp(285), cmp(linha-3), f"Calculo R$ {calculo}")
        linha -= 4
        if despesas:
            pdf.drawString(cmp(12), cmp(linha-3), f"{despesas}")
        pdf.drawRightString(cmp(285), cmp(linha-3), f"Valor R$ {valor_minuta}")
        linha -= 4
    return pdf