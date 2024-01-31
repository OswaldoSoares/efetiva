"""
    Modulo de Impressão
"""
from reportlab.lib.colors import HexColor
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import cmp


def header(pdf):
    """

    Args:
        pdf:

    Returns:


    """
    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    empresa = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    rua = "RUA OLIMPIO PORTUGAL, 245 - MOOCA"
    cidade = "SÃO PAULO - SP - CEP 03112-010"
    endereco = f"{rua} - {cidade}"
    telefone = "(11) 2305-0582 - WHATSAPP (11) 94167-0583"
    email_1 = "transefetiva@terra.com.br"
    email_2 = "operacional.efetiva@terra.com.br"
    email = f"e-mail: {email_1} - {email_2}"
    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)
    pdf.drawImage(url, cmp(12), cmp(265), cmp(40), cmp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawCentredString(cmp(126), cmp(279), empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(273), endereco)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(268), telefone)
    pdf.drawCentredString(cmp(126), cmp(263), email)
    pdf.line(cmp(10), cmp(260), cmp(200), cmp(260))
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(254.1), cmp(190), cmp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 12)
    return pdf
