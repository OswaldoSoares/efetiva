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


def dados_cliente(pdf, cliente):
    global linha
    nome = cliente["Nome"]
    cnpj = cliente["CNPJ"]
    endereco = cliente["Endereco"]
    bairro = cliente["Bairro"]
    cidade = cliente["Cidade"]
    estado = cliente["Estado"]
    cep = cliente["CEP"]
    endereco_completo = (
        f"{endereco} - {bairro} - CEP: {cep} - {cidade} - {estado}"
    )
    linha = 250.8
    pdf.drawCentredString(cmp(105), cmp(255.8), "FICHA CLIENTE")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#483D8B"))
    pdf.drawString(cmp(12), cmp(linha), f"{nome}")
    if cnpj:
        pdf.drawRightString(cmp(198), cmp(linha), f"CNPJ: {cnpj}")
    linha = 247.3
    pdf.drawString(cmp(12), cmp(linha), f"{endereco_completo}")
    pdf.setFillColor(HexColor("#000000"))
    linha = 246.3
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    return pdf


def telefones_cliente(pdf, telefones):
    global linha
    linha = 242.8
    pdf.drawCentredString(cmp(105), cmp(linha), "CONTATOS")
    pdf.line(cmp(95), cmp(linha - 0.5), cmp(115), cmp(linha - 0.5))
    linha -= 3
    pdf.setFont("Times-Roman", 8)
    for telefone in telefones:
        contato = telefone["Contato"]
        tipo = telefone["TipoFone"]
        numero = telefone["Fone"]
        pdf.drawString(cmp(12), cmp(linha), f"{contato} - {tipo} - {numero}")
        linha -= 3
    return pdf
