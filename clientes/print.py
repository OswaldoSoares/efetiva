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


def emails_cliente(pdf, emails):
    global linha
    pdf.setFont("Times-Roman", 8)
    for email in emails:
        contato = email["Contato"]
        email = email["EMail"]
        pdf.drawString(cmp(12), cmp(linha), f"{contato} - {email}")
        linha -= 3
    pdf.line(cmp(10), cmp(linha + 2), cmp(200), cmp(linha + 2))
    linha -= 3
    return pdf


def cobranca_cliente(pdf, cobranca):
    global linha
    print(cobranca)


def tabela_cliente(pdf, tabela):
    global linha
    seguro = f'Seguro: {tabela["Seguro"]}%'
    taxa = f'Taxa de Expedição: R$ {tabela["TaxaExpedicao"]}'
    ajudante = f'Ajudante: R$ {tabela["AjudanteCobra"]}'
    extra = f'Hora Extra Ajudante: RS {tabela["AjudanteCobraHoraExtra"]}'
    pdf.rect(cmp(11), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(60), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(109), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(158), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.setFont("Times-Roman", 8)
    pdf.drawCentredString(cmp(31.5), cmp(linha + 1), seguro)
    pdf.drawCentredString(cmp(80.5), cmp(linha + 1), taxa)
    pdf.drawCentredString(cmp(129.5), cmp(linha + 1), ajudante)
    pdf.drawCentredString(cmp(178.5), cmp(linha + 1), extra)
    pdf.line(cmp(10), cmp(linha - 1), cmp(200), cmp(linha - 1))
    linha -= 3
    return pdf


def tipo_pagamento(pdf, tabela):
    global linha
    phkesc = tabela["phkescCobra"]
    porcentagem = int(phkesc[0])
    hora = int(phkesc[1])
    kilometragem = int(phkesc[2])
    entrega = int(phkesc[3])
    entrega_kg = int(phkesc[6])
    entrega_volume = int(phkesc[7])
    saida = int(phkesc[4])
    pdf.line(cmp(11), cmp(linha), cmp(199), cmp(linha))
    linha -= 3
    pdf.setFont("Times-Roman", 7)
    pdf.drawCentredString(cmp(24.5), cmp(linha), "PERIMETRO")
    pdf.drawCentredString(cmp(51.5), cmp(linha), "HORA")
    pdf.drawCentredString(cmp(78.5), cmp(linha), "KILOMETRAGEM")
    pdf.drawCentredString(cmp(105.5), cmp(linha), "ENTREGA")
    pdf.drawCentredString(cmp(132.5), cmp(linha), "ENTREGA KG")
    pdf.drawCentredString(cmp(159.5), cmp(linha), "ENTREGA VOLUME")
    pdf.drawCentredString(cmp(186.5), cmp(linha), "SAÍDA")
    pdf.setFont("Times-Roman", 8)
    linha -= 1
    pdf.line(cmp(11), cmp(linha), cmp(11), cmp(linha + 4))
    pdf.line(cmp(38), cmp(linha), cmp(38), cmp(linha + 4))
    pdf.line(cmp(65), cmp(linha), cmp(65), cmp(linha + 4))
    pdf.line(cmp(92), cmp(linha), cmp(92), cmp(linha + 4))
    pdf.line(cmp(119), cmp(linha), cmp(119), cmp(linha + 4))
    pdf.line(cmp(146), cmp(linha), cmp(146), cmp(linha + 4))
    pdf.line(cmp(173), cmp(linha), cmp(173), cmp(linha + 4))
    pdf.line(cmp(199), cmp(linha), cmp(199), cmp(linha + 4))
    pdf.line(cmp(11), cmp(linha), cmp(199), cmp(linha))
    linha -= 6
    return pdf
