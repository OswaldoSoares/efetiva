import datetime
from decimal import Decimal
from io import BytesIO
from pathlib import Path

import fitz
from django.http import HttpResponse
from pdfrw import PdfReader, PdfWriter
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph

from core.tools import (
    antecipar_data_final_de_semana,
    formatar_numero_com_separadores,
    get_saldo_contra_cheque,
    periodo_por_extenso,
    valor_por_extenso,
)
from pessoas.facade import do_crop
from pessoas.facades.ferias import faltas_periodo_aquisitivo
from romaneios.print import header
from transefetiva.settings.settings import MEDIA_ROOT, STATIC_ROOT
from website.facade import cmp, valor_ponto_milhar


def print_pdf_ficha_colaborador(contexto):
    nome_curto = contexto["colaborador"].nome_curto
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'filename="FICHA CADASTRAL {nome_curto}.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    ficha_colaborador(pdf, contexto)
    pdf.setTitle(f"FICHA CADSTRAl {nome_curto}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def ficha_colaborador(pdf, contexto):
    if contexto["colaborador"].foto:
        foto = contexto["colaborador"].foto.path
        foto = do_crop(foto)
        if foto == False:
            foto = f"{STATIC_ROOT}/website/img/usuario.png"
    else:
        foto = f"{STATIC_ROOT}/website/img/usuario.png"
    nome = contexto["colaborador"].nome
    categoria = contexto["colaborador"].dados_profissionais.categoria
    data_nascimento = datetime.datetime.strftime(
        contexto["colaborador"].filiacao.data_nascimento, "%d/%m/%Y"
    )
    mae = contexto["colaborador"].filiacao.mae
    pai = contexto["colaborador"].filiacao.pai
    endereco = contexto["colaborador"].residencia.endereco
    bairro = contexto["colaborador"].residencia.bairro
    cep = contexto["colaborador"].residencia.cep
    cidade_estado = contexto["colaborador"].residencia.cidade_estado
    docs = contexto["colaborador"].documentos.docs
    fones = contexto["colaborador"].telefones.fones
    contas = contexto["colaborador"].bancos.contas
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(105), cmp(255.8), "FICHA CADASTRAL")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    pdf.drawImage(foto, cmp(85), cmp(210), cmp(40), cmp(40), mask="auto")
    pdf.setFont("Helvetica", 15)
    pdf.setFillColor(HexColor("#FF0000"))
    pdf.drawCentredString(cmp(105), cmp(202), nome)
    pdf.setFont("Helvetica", 12)
    pdf.drawCentredString(cmp(105), cmp(198), categoria)
    pdf.line(cmp(10), cmp(196), cmp(200), cmp(196))
    if contexto["colaborador"].foto:
        pdf.circle(cmp(105), cmp(230), 57, stroke=1, fill=0)
    linha = 192
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawString(cmp(12), cmp(linha), f"ENDEREÇO: {endereco}")
    linha -= 5
    pdf.drawString(cmp(12), cmp(linha), f"BAIRRO: {bairro} - {cidade_estado}")
    linha -= 5
    pdf.drawString(
        cmp(12), cmp(linha), f"DATA DE NASCIMENTO: {data_nascimento}"
    )
    if mae:
        linha -= 5
        pdf.drawString(cmp(12), cmp(linha), f"NOME DA MÃE: {mae}")
    if pai:
        linha -= 5
        pdf.drawString(cmp(12), cmp(linha), f"NOME DO PAI: {pai}")
    linha -= 1.5
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if docs:
        linha -= 6
        pdf.setFont("Times-Roman", 12)
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(5), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(cmp(105), cmp(linha + 1), "DOCUMENTOS")
        pdf.setFont("Times-Roman", 10)
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha += 1
        for doc in docs:
            linha -= 5
            tipo = doc.TipoDocumento
            documento = doc.Documento
            data = datetime.datetime.strftime(doc.Data, "%d/%m/%Y")
            if tipo == "HABILITAÇÃO":
                pdf.drawString(
                    cmp(12),
                    cmp(linha),
                    f"{tipo}: {documento} - VENCIMENTO: {data}",
                )
            else:
                pdf.drawString(cmp(12), cmp(linha), f"{tipo}: {documento}")
        linha -= 1.5
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if fones:
        linha -= 6
        pdf.setFont("Times-Roman", 12)
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(5), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(cmp(105), cmp(linha + 1), "TELEFONES")
        pdf.setFont("Times-Roman", 10)
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha += 1
        for fone in fones:
            linha -= 5
            pdf.drawString(
                cmp(12), cmp(linha), f"{fone.TipoFone}: {fone.Fone}"
            )
        linha -= 1.5
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if contas:
        linha -= 6
        pdf.setFont("Times-Roman", 12)
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(5), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            cmp(105), cmp(linha + 1), "INFORMAÇÕES BANCÁRIAS"
        )
        pdf.setFont("Times-Roman", 10)
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha += 1
        for conta in contas:
            linha -= 5
            pdf.drawString(
                cmp(12),
                cmp(linha),
                f"BANCO {conta.Banco} - AGÊNCIA: {conta.Agencia}"
                f" CONTA {conta.TipoConta}:"
                f" {conta.Conta} - CHAVE PIX: {conta.PIX}",
            )


def print_pdf_rescisao_trabalho(pdf, contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="RESCISAO DE TRABALHO.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf = formulario_rescisao_trabalho(pdf, contexto)
    #  pdf = dados_rescisao_trabalho(pdf, contexto)
    pdf = dados_rescisao_trabalho_nova(pdf, contexto)
    pdf.setTitle("RESCISÃO DE TRABALHO - .pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def dados_rescisao_trabalho_nova(pdf, contexto):
    cnpj = "21.602.117/0001-15"
    razao_social = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    endereco_empregador = "RUA OLIMPIO PORTUGAL, 245"
    bairro_empregador = "MOOCA"
    cidade_empregador = "SÃO PAULO"
    estado_empregador = "SP"
    cep_empregador = "03112-010"
    for doc in contexto["colaborador"].documentos.docs:
        if doc.TipoDocumento == "CPF":
            cpf = doc.Documento
    nome_trabalhador = contexto["colaborador"].nome
    endereco_trabalhador = contexto["colaborador"].residencia.endereco
    bairro_trabalhador = contexto["colaborador"].residencia.bairro
    cidade_trabalhador = contexto["colaborador"].residencia.cidade
    estado_trabalhador = contexto["colaborador"].residencia.estado
    cep_trabalhador = contexto["colaborador"].residencia.cep
    nascimento = datetime.datetime.strftime(
        contexto["colaborador"].filiacao.data_nascimento, "%d/%m/%Y"
    )
    mae_trabalhador = contexto["colaborador"].filiacao.mae
    categoria = contexto["colaborador"].dados_profissionais.categoria
    causa = contexto["motivo"]
    salario = contexto["colaborador"].salarios.salarios.Salario
    admissao = datetime.datetime.strftime(
        contexto["colaborador"].dados_profissionais.data_admissao, "%d/%m/%Y"
    )
    demissao = datetime.datetime.strftime(
        contexto["colaborador"].dados_profissionais.data_demissao, "%d/%m/%Y"
    )
    bruto = Decimal(0.00)
    meses_ferias = contexto["ferias_meses"]
    ferias = contexto["ferias_valor"]
    bruto += ferias
    terco_ferias = contexto["ferias_um_terco"]
    bruto += terco_ferias
    if contexto["decimo_terceiro_valor"] is not None:
        meses_decimo_terceiro = contexto["decimo_terceiro_meses"]
        decimo_terceiro = contexto["decimo_terceiro_valor"]
        decimo_terceiro_pago = contexto["decimo_terceiro_total_pago"]
        bruto += decimo_terceiro
    if "desconto_ferias" in contexto:
        ferias_paga = contexto["desconto_ferias"]
    linha = 267.3
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(cmp(15), cmp(linha), f"{cnpj}")
    pdf.drawString(cmp(60), cmp(linha), f"{razao_social}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{endereco_empregador}")
    pdf.drawString(cmp(131), cmp(linha), f"{bairro_empregador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{cidade_empregador}")
    pdf.drawString(cmp(73), cmp(linha), f"{estado_empregador}")
    pdf.drawString(cmp(85), cmp(linha), f"{cep_empregador}")
    linha -= 7.7
    linha -= 4
    pdf.drawString(cmp(15), cmp(linha), f"{cpf}")
    pdf.drawString(cmp(60), cmp(linha), f"{nome_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{endereco_trabalhador}")
    pdf.drawString(cmp(131), cmp(linha), f"{bairro_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{cidade_trabalhador}")
    pdf.drawString(cmp(73), cmp(linha), f"{estado_trabalhador}")
    pdf.drawString(cmp(85), cmp(linha), f"{cep_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{nascimento}")
    pdf.drawString(cmp(60), cmp(linha), f"{mae_trabalhador}")
    linha -= 7.7
    linha -= 4
    pdf.drawString(cmp(15), cmp(linha), f"{categoria}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{causa}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"R$ {salario}")
    pdf.drawString(cmp(49), cmp(linha), f"{admissao}")
    pdf.drawString(cmp(123), cmp(linha), f"{demissao}")
    linha -= 7.7
    linha -= 4
    col = 11
    if contexto["saldo_salario"] is not None:
        for x in contexto["contra_cheque_itens"]:
            if x.Registro == "C":
                if x.Descricao.startswith("SALARIO"):
                    descricao = x.Descricao.replace("SALARIO", "SALDO DE SALARIO")
                else:
                    descricao = x.Descricao
                pdf.drawString(
                    cmp(col), cmp(linha), f"{descricao} - {x.Referencia}"
                )
                pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {x.Valor}")
                bruto += x.Valor
                if col == 11:
                    col = 106
                else:
                    col = 11
                    linha -= 7.7
    if meses_ferias > 0:
        pdf.drawString(
            cmp(col), cmp(linha), f"FÉRIAS PROPORCIONAIS - {meses_ferias}/12"
        )
        pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {ferias}")
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7
        pdf.drawString(cmp(col), cmp(linha), "1/3 FÉRIAS PROPORCIONAIS")
        #  terco_ferias = "0,00"
        pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {terco_ferias}")
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7
    if contexto["decimo_terceiro_valor"] is not None and meses_decimo_terceiro:
        pdf.drawString(
            cmp(col),
            cmp(linha),
            f"13º PROPORCIONAL - {meses_decimo_terceiro}/12",
        )
        pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {decimo_terceiro}")
    if col == 11:
        col = 106
    else:
        col = 11
        linha -= 7.7
    for x in contexto["ferias_vencidas"]:
        pdf.setFont("Times-Roman", 7)
        pdf.drawString(
            cmp(col),
            cmp(linha + 4),
            f"Periodo Aquisitivo {x['periodo']} - FALTAS {x['numero_faltas']}",
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(
            cmp(col), cmp(linha), f"FÉRIAS VENCIDAS {x['dias_pagar']}d"
        )
        pdf.drawRightString(
            cmp(col + 93), cmp(linha), f"R$ {x['valor_pagar']}"
        )
        bruto += x["valor_pagar"]
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7
        pdf.setFont("Times-Roman", 7)
        pdf.drawString(
            cmp(col), cmp(linha + 4), f"Periodo Aquisitivo {x['periodo']}"
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(
            cmp(col), cmp(linha), f"1/3 FÉRIAS VENCIDAS {x['dias_pagar']}d"
        )
        pdf.drawRightString(
            cmp(col + 93), cmp(linha), f"R$ {x['um_terco_pagar']}"
        )
        bruto += x["um_terco_pagar"]
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7
    linha = 116.7
    #  bruto = "261,87"
    pdf.drawRightString(cmp(199), cmp(linha + 1), f"R$ {bruto}")
    linha -= 7.7
    linha -= 4
    linha += 1
    deducoes = Decimal(0.00)
    col = 11
    if "decimo_terceiro_parcelas_pagas" in contexto:
        pdf.drawString(cmp(col), cmp(linha), "13º PARCELAS PAGAS")
        pdf.drawRightString(
            cmp(col + 93), cmp(linha), f"R$ {decimo_terceiro_pago}"
        )
        deducoes += decimo_terceiro_pago
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7
    if contexto["saldo_salario"] is not None:
        for item in contexto["contra_cheque_itens"]:
            if item.Registro == "D":
                pdf.drawString(cmp(col), cmp(linha), f"{item.Descricao}")
                pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {item.Valor}")
                deducoes += item.Valor
                if col == 11:
                    col = 106
                else:
                    col = 11
                    linha -= 7.7
    if "desconto_ferias" in contexto:
        pdf.drawString(cmp(col), cmp(linha), "DESCONTO FÉRIAS PAGA")
        pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {ferias_paga}")
        deducoes += ferias_paga
        if col == 11:
            col = 106
        else:
            col = 11
            linha -= 7.7

    linha = 44.4
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {deducoes}")
    linha -= 7.7
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {bruto - deducoes}")
    pdf.drawCentredString(cmp(105), cmp(15), f"{nome_trabalhador}")
    return pdf


def dados_rescisao_trabalho(pdf, contexto):
    cnpj = "21.602.117/0001-15"
    razao_social = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    endereco_empregador = "RUA OLIMPIO PORTUGAL, 245"
    bairro_empregador = "MOOCA"
    cidade_empregador = "SÃO PAULO"
    estado_empregador = "SP"
    cep_empregador = "03112-010"
    for x in contexto["colaborador"]["documentos"]:
        if x["tipo"] == "CPF":
            cpf = x["documento"]
    nome_trabalhador = contexto["colaborador"]["nome"]
    endereco_trabalhador = contexto["colaborador"]["endereco"]
    bairro_trabalhador = contexto["colaborador"]["bairro"]
    cidade_trabalhador = contexto["colaborador"]["cidade"]
    estado_trabalhador = contexto["colaborador"]["estado"]
    cep_trabalhador = contexto["colaborador"]["cep"]
    nascimento = datetime.datetime.strftime(
        contexto["colaborador"]["data_nascimento"], "%d/%m/%Y"
    )
    mae_trabalhador = contexto["colaborador"]["mae"]
    categoria = contexto["colaborador"]["categoria"]
    causa = contexto["causa"]
    salario = contexto["colaborador"]["salario"][0]["salario"]
    admissao = datetime.datetime.strftime(
        contexto["colaborador"]["data_admissao"], "%d/%m/%Y"
    )
    demissao = datetime.datetime.strftime(
        contexto["colaborador"]["data_demissao"], "%d/%m/%Y"
    )
    bruto = Decimal(0.00)
    meses_ferias = contexto["rescisao"][0]["meses_ferias"]
    ferias = contexto["rescisao"][0]["ferias"]
    bruto += ferias
    terco_ferias = contexto["rescisao"][0]["terco_ferias"]
    bruto += terco_ferias
    meses_decimo_terceiro = contexto["rescisao"][0]["meses_decimo_terceiro"]
    decimo_terceiro = contexto["rescisao"][0]["decimo_terceiro"]
    bruto += decimo_terceiro
    linha = 267.3
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(cmp(15), cmp(linha), f"{cnpj}")
    pdf.drawString(cmp(60), cmp(linha), f"{razao_social}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{endereco_empregador}")
    pdf.drawString(cmp(131), cmp(linha), f"{bairro_empregador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{cidade_empregador}")
    pdf.drawString(cmp(73), cmp(linha), f"{estado_empregador}")
    pdf.drawString(cmp(85), cmp(linha), f"{cep_empregador}")
    linha -= 7.7
    linha -= 4
    pdf.drawString(cmp(15), cmp(linha), f"{cpf}")
    pdf.drawString(cmp(60), cmp(linha), f"{nome_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{endereco_trabalhador}")
    pdf.drawString(cmp(131), cmp(linha), f"{bairro_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{cidade_trabalhador}")
    pdf.drawString(cmp(73), cmp(linha), f"{estado_trabalhador}")
    pdf.drawString(cmp(85), cmp(linha), f"{cep_trabalhador}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{nascimento}")
    pdf.drawString(cmp(60), cmp(linha), f"{mae_trabalhador}")
    linha -= 7.7
    linha -= 4
    pdf.drawString(cmp(15), cmp(linha), f"{categoria}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"{causa}")
    linha -= 7.7
    pdf.drawString(cmp(15), cmp(linha), f"R$ {salario}")
    pdf.drawString(cmp(49), cmp(linha), f"{admissao}")
    pdf.drawString(cmp(123), cmp(linha), f"{demissao}")
    linha -= 7.7
    linha -= 4
    col = 11
    for x in contexto["rescisao"][0]["folha_contra_cheque_itens"]:
        if x.Registro == "C":
            if x.Descricao.startswith("SALARIO"):
                descricao = x.Descricao.replace("SALARIO", "SALDO DE SALARIO")
            else:
                descricao = x.Descricao
            pdf.drawString(
                cmp(col), cmp(linha), f"{descricao} - {x.Referencia}"
            )
            pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {x.Valor}")
            bruto += x.Valor
            if col == 11:
                col = 106
            else:
                col = 11
                linha -= 7.7
    #  meses_ferias = "0"
    pdf.drawString(
        cmp(col), cmp(linha), f"FÉRIAS PROPORCIONAIS - {meses_ferias}/12"
    )
    #  ferias = "0,00"
    pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {ferias}")
    if col == 11:
        col = 106
    else:
        col = 11
        linha -= 7.7
    pdf.drawString(cmp(col), cmp(linha), "1/3 FÉRIAS PROPORCIONAIS")
    #  terco_ferias = "0,00"
    pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {terco_ferias}")
    if col == 11:
        col = 106
    else:
        col = 11
        linha -= 7.7
    pdf.drawString(
        cmp(col), cmp(linha), f"13º PROPORCIONAL - {meses_decimo_terceiro}/12"
    )
    pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {decimo_terceiro}")
    linha = 116.7
    #  bruto = "261,87"
    pdf.drawRightString(cmp(199), cmp(linha + 1), f"R$ {bruto}")
    linha -= 7.7
    linha -= 4
    linha += 1
    deducoes = Decimal(0.00)
    col = 11
    for x in contexto["rescisao"][0]["folha_contra_cheque_itens"]:
        if x.Registro == "D":
            pdf.drawString(cmp(col), cmp(linha), f"{x.Descricao}")
            pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {x.Valor}")
            deducoes += x.Valor
            if col == 11:
                col = 106
            else:
                col = 11
                linha -= 7.7
    linha = 44.4
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {deducoes}")
    linha -= 7.7
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {bruto - deducoes}")
    pdf.drawCentredString(cmp(105), cmp(15), f"{nome_trabalhador}")
    return pdf


def formulario_rescisao_trabalho(pdf, contexto):
    pdf.setFont("Times-Roman", 12)
    pdf.rect(cmp(10), cmp(10), cmp(190), cmp(277), fill=0)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(11), cmp(281), cmp(188), cmp(5), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    linha = 282
    pdf.drawCentredString(
        cmp(105), cmp(linha), "RESCISÃO DO CONTRATO DE TRABALHO"
    )
    linha -= 8
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=0)
    pdf.drawCentredString(
        cmp(105), cmp(linha + 1), "IDENTIFICAÇÃO DO EMPREGADOR"
    )
    pdf.setFont("Times-Roman", 6)
    pdf.drawString(cmp(11), cmp(linha - 2.7), "CNPJ:")
    pdf.line(cmp(54), cmp(linha - 7.7), cmp(54), cmp(linha))
    pdf.drawString(cmp(55), cmp(linha - 2.7), "RAZÃO SOCIAL:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "ENDEREÇO (logradouro, nº):")
    pdf.line(cmp(126), cmp(linha - 7.7), cmp(126), cmp(linha))
    pdf.drawString(cmp(127), cmp(linha - 2.7), "BAIRRO:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "MUNICÍPIO:")
    pdf.line(cmp(68), cmp(linha - 7.7), cmp(68), cmp(linha))
    pdf.drawString(cmp(69), cmp(linha - 2.7), "UF:")
    pdf.line(cmp(83), cmp(linha - 7.7), cmp(83), cmp(linha))
    pdf.drawString(cmp(84), cmp(linha - 2.7), "CEP:")
    pdf.line(cmp(103), cmp(linha - 7.7), cmp(103), cmp(linha))
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    linha -= 4
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=0)
    pdf.drawCentredString(
        cmp(105), cmp(linha + 1), "IDENTIFICAÇÃO DO TRABALHADOR"
    )
    pdf.setFont("Times-Roman", 6)
    pdf.drawString(cmp(11), cmp(linha - 2.7), "CPF:")
    pdf.line(cmp(54), cmp(linha - 7.7), cmp(54), cmp(linha))
    pdf.drawString(cmp(55), cmp(linha - 2.7), "NOME:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "ENDEREÇO (logradouro, nº):")
    pdf.line(cmp(126), cmp(linha - 7.7), cmp(126), cmp(linha))
    pdf.drawString(cmp(127), cmp(linha - 2.7), "BAIRRO:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "MUNICÍPIO:")
    pdf.line(cmp(68), cmp(linha - 7.7), cmp(68), cmp(linha))
    pdf.drawString(cmp(69), cmp(linha - 2.7), "UF:")
    pdf.line(cmp(83), cmp(linha - 7.7), cmp(83), cmp(linha))
    pdf.drawString(cmp(84), cmp(linha - 2.7), "CEP:")
    pdf.line(cmp(103), cmp(linha - 7.7), cmp(103), cmp(linha))
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "DATA NASCIMENTO:")
    pdf.line(cmp(54), cmp(linha - 7.7), cmp(54), cmp(linha))
    pdf.drawString(cmp(55), cmp(linha - 2.7), "NOME DA MÃE:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    linha -= 4
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=0)
    pdf.drawCentredString(cmp(105), cmp(linha + 1), "DADOS CONTRATO")
    pdf.setFont("Times-Roman", 6)
    pdf.drawString(cmp(11), cmp(linha - 2.7), "TIPO CONTRATO:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "CAUSA DO AFASTAMENTO:")
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    pdf.drawString(cmp(11), cmp(linha - 2.7), "REMUNERAÇÃO MÊS ANT.:")
    pdf.line(cmp(44), cmp(linha - 7.7), cmp(44), cmp(linha))
    pdf.drawString(cmp(45), cmp(linha - 2.7), "DATA ADMISSÃO:")
    pdf.line(cmp(80), cmp(linha - 7.7), cmp(80), cmp(linha))
    pdf.drawString(cmp(81), cmp(linha - 2.7), "DATA AVISO PRÉVIO:")
    pdf.line(cmp(118), cmp(linha - 7.7), cmp(118), cmp(linha))
    pdf.drawString(cmp(119), cmp(linha - 2.7), "DATA AFASTAMENTO:")
    pdf.line(cmp(155), cmp(linha - 7.7), cmp(155), cmp(linha))
    pdf.line(cmp(10), cmp(linha - 7.7), cmp(200), cmp(linha - 7.7))
    linha -= 7.7
    linha -= 4
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=0)
    pdf.drawCentredString(cmp(105), cmp(linha + 1), "VERBAS RESCISORIA")
    pdf.setFont("Times-Roman", 6)
    for x in range(7):
        linha -= 7.7
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    linha -= 7.7
    pdf.line(cmp(70), cmp(linha), cmp(70), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(105), cmp(linha), cmp(105), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(165), cmp(linha), cmp(165), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    linha = 116.7
    pdf.setFont("Times-Roman", 10)
    pdf.drawRightString(cmp(164), cmp(linha + 1), "TOTAL BRUTO")
    pdf.line(cmp(165), cmp(linha), cmp(165), cmp(linha + 7.7))
    linha -= 4
    pdf.setFont("Times-Roman", 8)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(10), cmp(linha), cmp(190), cmp(4), fill=0)
    pdf.drawCentredString(cmp(105), cmp(linha + 1), "DEDUÇÕES")
    pdf.setFont("Times-Roman", 6)
    for x in range(7):
        linha -= 7.7
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    linha -= 7.7
    pdf.line(cmp(70), cmp(linha), cmp(70), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(105), cmp(linha), cmp(105), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(165), cmp(linha), cmp(165), cmp(linha + (8 * 7.7)))
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    linha -= 7.7
    pdf.setFont("Times-Roman", 10)
    pdf.drawRightString(cmp(164), cmp(linha + 1), "TOTAL DEDUÇÕES")
    pdf.line(cmp(165), cmp(linha), cmp(165), cmp(linha + 7.7))
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    linha -= 7.7
    pdf.drawRightString(cmp(164), cmp(linha + 1), "TOTAL LIQUIDO")
    pdf.line(cmp(165), cmp(linha), cmp(165), cmp(linha + 7.7))
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    pdf.line(cmp(50), cmp(19), cmp(160), cmp(19))
    pdf.drawCentredString(cmp(105), cmp(31), contexto["data_extenso"])
    return pdf


def base_contra_cheque(pdf, contexto):
    linha = 297
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(cmp(5), cmp(linha - 18.5), cmp(173), cmp(13.5), fill=0)
    pdf.rect(cmp(5), cmp(linha - 28.3), cmp(173), cmp(9.3), fill=0)
    pdf.rect(cmp(5), cmp(linha - 36), cmp(173), cmp(4.8), fill=0)
    pdf.rect(cmp(5), cmp(linha - 116.3), cmp(173), cmp(79.8), fill=0)
    pdf.rect(cmp(5), cmp(linha - 134.1), cmp(111.1), cmp(17.3), fill=0)
    pdf.rect(cmp(5), cmp(linha - 144.8), cmp(173), cmp(10.2), fill=0)
    pdf.rect(cmp(116.1), cmp(linha - 125.2), cmp(61.9), cmp(8.4), fill=0)
    pdf.rect(cmp(116.1), cmp(linha - 134.1), cmp(61.9), cmp(8.4), fill=0)
    pdf.rect(cmp(180.9), cmp(linha - 144.8), cmp(24.1), cmp(139.8), fill=0)
    pdf.line(cmp(16.7), cmp(linha - 36), cmp(16.7), cmp(linha - 31.2))
    pdf.line(cmp(95.9), cmp(linha - 36), cmp(95.9), cmp(linha - 31.2))
    pdf.line(cmp(116.1), cmp(linha - 36), cmp(116.1), cmp(linha - 31.2))
    pdf.line(cmp(147.8), cmp(linha - 36), cmp(147.8), cmp(linha - 31.2))
    pdf.line(cmp(16.7), cmp(linha - 116.3), cmp(16.7), cmp(linha - 36.5))
    pdf.line(cmp(95.9), cmp(linha - 116.3), cmp(95.9), cmp(linha - 36.5))
    pdf.line(cmp(116.1), cmp(linha - 116.3), cmp(116.1), cmp(linha - 36.5))
    pdf.line(cmp(147.8), cmp(linha - 116.3), cmp(147.8), cmp(linha - 36.5))
    pdf.line(cmp(147.8), cmp(linha - 125.2), cmp(147.8), cmp(linha - 116.8))
    pdf.line(cmp(147.8), cmp(linha - 134.1), cmp(147.8), cmp(linha - 125.7))
    pdf.setFont("Times-Roman", 11)
    pdf.drawString(
        cmp(6), cmp(linha - 13.8), "TRANSEFETIVA TRANSPORTES - EIRELLI - ME"
    )
    pdf.drawString(cmp(6), cmp(linha - 17.7), "CNPJ: 21.602.117/0001-15")
    pdf.setFillColor(HexColor("#808080"))
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(cmp(5.8), cmp(linha - 22.9), "{}".format("Código"))
    pdf.drawString(cmp(20.2), cmp(linha - 22.9), "Nome do Funcionário")
    pdf.drawString(
        cmp(102.6),
        cmp(linha - 22.9),
        "CBO    Emp.   Local   Dept.  Setor   Seção   Fl.",
    )
    pdf.drawCentredString(cmp(10.85), cmp(linha - 35), "Cód.")
    pdf.drawCentredString(cmp(56.3), cmp(linha - 35), "Descrição")
    pdf.drawCentredString(cmp(106), cmp(linha - 35), "Referência")
    pdf.drawCentredString(cmp(131.95), cmp(linha - 35), "Vencimentos")
    pdf.drawCentredString(cmp(162.9), cmp(linha - 35), "Descontos")
    pdf.setFont("Times-Roman", 9)
    pdf.drawCentredString(
        cmp(131.95), cmp(linha - 119.7), "Total de Vencimentos"
    )
    pdf.drawCentredString(cmp(162.9), cmp(linha - 119.7), "Total de Descontos")
    pdf.drawCentredString(
        cmp(131.95), cmp(linha - 132), "Valor Líquido \u279C"
    )
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(cmp(10), cmp(linha - 139), "Salário Base")
    if contexto["colaborador"].dados_profissionais.registrado:
        pdf.drawString(cmp(32), cmp(linha - 139), "Sal. Contr. INSS")
        pdf.drawString(cmp(61), cmp(linha - 139), "Base Calculo FGTS")
        pdf.drawString(cmp(93), cmp(linha - 139), "FGTS do Mês")
        pdf.drawString(cmp(120), cmp(linha - 139), "Base Calculo IRRF")
        pdf.drawString(cmp(155), cmp(linha - 139), "Faixa IRRF")
    pdf.setFillColor(HexColor("#808080"))



    pdf.line(cmp(0), cmp(148.5), cmp(210), cmp(148.5))
    pdf.rotate(90)
    linha = 297
    pdf.setFont("Times-Roman", 9)
    pdf.drawString(
        cmp(linha - 138),
        cmp(-186),
        "DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA DISCRIMINADA NESTE RECIBO",
    )
    pdf.drawString(cmp(linha - 133), cmp(-197), "_____/_____/_____")
    pdf.drawString(cmp(linha - 133), cmp(-201), "          DATA       ")
    pdf.drawString(
        cmp(linha - 83), cmp(-197), "_______________________________"
    )
    pdf.drawString(cmp(linha - 83), cmp(-201), "ASSINATURA DO FUNCIONÁRIO")
    return pdf


def print_contra_cheque(contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = 'filename="Contra Cheque.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    contra_cheque_dados(pdf, contexto)
    contra_cheque_itens(pdf, contexto)
    contra_cheque_totais(pdf, contexto)
    if contexto["contra_cheque"].Descricao == "PAGAMENTO":
        contra_cheque_cartao_ponto(pdf, contexto)
        contra_cheque_minutas(pdf, contexto)
    base_contra_cheque(pdf, contexto)
    pdf.setTitle("Contra Cheque")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def contra_cheque_dados(pdf, contexto):
    linha = 297
    pdf.setFillColor(HexColor("#808080"))
    pdf.setFont("Times-Roman", 14)
    pdf.drawString(
        cmp(101.6),
        cmp(linha - 11),
        f'RECIBO DE {contexto["contra_cheque"].Descricao}',
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 11)
    descricao = contexto["contra_cheque"].Descricao
    mes = contexto["contra_cheque"].MesReferencia
    ano = contexto["contra_cheque"].AnoReferencia
    if descricao == "FERIAS" or descricao[:15] == "DECIMO TERCEIRO":
        pdf.drawString(
            cmp(122.8),
            cmp(linha - 17.7),
            f"{ano}",
        )
    else:
        pdf.drawString(
            cmp(122.8),
            cmp(linha - 17.7),
            f"{mes}/{ano}",
        )
    pdf.setFont("Times-Roman", 10)
    pdf.drawString(
        cmp(5.8),
        cmp(linha - 27.2),
        f'{contexto["colaborador"].id_pessoal}'.zfill(4),
    )
    pdf.drawString(
        cmp(20.2),
        cmp(linha - 27.4),
        f'{contexto["colaborador"].nome}',
    )
    pdf.drawString(
        cmp(102.6),
        cmp(linha - 27.2),
        f'{contexto["colaborador"].dados_profissionais.categoria}',
    )
    salario_base = valor_ponto_milhar(
        contexto["colaborador"].salarios.salarios.Salario, 2
    )
    base_inss = valor_ponto_milhar(
        contexto["contra_cheque"].BaseINSS, 2
    )
    base_fgts = valor_ponto_milhar(
        contexto["contra_cheque"].BaseFGTS, 2
    )
    base_irrf = valor_ponto_milhar(
        contexto["contra_cheque"].BaseIRRF, 2
    )
    valor_fgts = valor_ponto_milhar(
        (contexto["contra_cheque"].BaseFGTS / 100 * 8), 2
    )
    faixa_irrf = "******"

    pdf.drawString(
        cmp(10),
        cmp(linha - 144),
        f"R$ {salario_base}",
    )
    if contexto["colaborador"].dados_profissionais.registrado:
        pdf.drawString(
            cmp(32),
            cmp(linha - 144),
            f"R$ {base_inss}",
        )
        pdf.drawString(
            cmp(61),
            cmp(linha - 144),
            f"R$ {base_fgts}",
        )
        pdf.drawString(
            cmp(93),
            cmp(linha - 144),
            f"R$ {valor_fgts}",
        )
        pdf.drawString(
            cmp(120),
            cmp(linha - 144),
            f"R$ {base_irrf}",
        )
        pdf.drawString(
            cmp(155),
            cmp(linha - 144),
            f"{faixa_irrf}",
        )

    contra_cheque_obs(pdf, contexto)
    return pdf


def contra_cheque_itens(pdf, contexto):
    linha = 297
    linhaitens = 0
    for itens in contexto["contra_cheque_itens"]:
        pdf.drawString(
            cmp(7.4),
            cmp(linha - 41.2 - linhaitens),
            f"{itens.Codigo}",
        )
        pdf.drawString(
            cmp(17.5),
            cmp(linha - 41.2 - linhaitens),
            f"{itens.Descricao}",
        )
        pdf.drawCentredString(
            cmp(106),
            cmp(linha - 41.2 - linhaitens),
            f"{itens.Referencia}",
        )
        valor = valor_ponto_milhar(itens.Valor, 2)
        if itens.Registro == "C":
            pdf.drawRightString(
                cmp(142.6), cmp(linha - 41.2 - linhaitens), f"R$ {valor}"
            )
        else:
            pdf.drawRightString(
                cmp(171.7), cmp(linha - 41.2 - linhaitens), f"R$ {valor}"
            )
        linhaitens += 4
    return pdf


def contra_cheque_totais(pdf, contexto):
    credito = f'R$ {valor_ponto_milhar(contexto["credito"], 2)}'
    debito = f'R$ {valor_ponto_milhar(contexto["debito"], 2)}'
    saldo = f'R$ {valor_ponto_milhar(contexto["saldo"], 2)}'
    linha = 297
    pdf.setFont("Times-Roman", 11)
    pdf.drawRightString(cmp(142.6), cmp(linha - 124), credito)
    pdf.drawRightString(cmp(171.7), cmp(linha - 124), debito)
    pdf.drawRightString(cmp(171.7), cmp(linha - 132), saldo)
    return pdf


def contra_cheque_obs(pdf, contexto):
    #  dict_obs = ast.literal_eval(contexto["contra_cheque"].Obs)
    #  obs = ""
    #  for item_x in dict_obs:
    #  if isinstance(dict_obs[item_x], str):
    #  obs = obs + f"* {dict_obs[item_x]} "
    #  elif isinstance(dict_obs[item_x], dict):
    #  for item_y in dict_obs[item_x]:
    #  if isinstance(dict_obs[item_x][item_y], dict):
    #  obs = obs + f"* {dict_obs[item_x][item_y]} "
    obs = str(contexto["contra_cheque"].Obs)
    obs = obs.replace("{", "").replace("}", "").replace("'", "")
    obs = obs[:-1]
    styles_claro = ParagraphStyle(
        "claro",
        fontName="Times-Roman",
        fontSize=7,
        leading=9,
        alignment=TA_JUSTIFY,
    )
    para = Paragraph(obs, style=styles_claro)
    linha = 297
    para.wrapOn(pdf, cmp(105), cmp(297))
    linha -= para.height * 0.352777
    para.drawOn(pdf, cmp(8), cmp(linha - 117.7))


def contra_cheque_cartao_ponto(pdf, contexto):
    if contexto["cartao_ponto"]:
        linha = 140
        numerodias = len(contexto["cartao_ponto"])
        pdf.setFont("Times-Roman", 9)
        pdf.rect(cmp(5), cmp(linha), cmp(55), cmp(6), fill=0)
        pdf.drawCentredString(cmp(32.5), cmp(linha + 2), "CARTÃO DE PONTO")
        linha -= 4
        pdf.setFont("Times-Roman", 9)
        pdf.drawCentredString(cmp(15), cmp(linha + 0.5), "DATA")
        pdf.drawCentredString(cmp(35), cmp(linha + 0.5), "ENTRADA")
        pdf.drawCentredString(cmp(50), cmp(linha + 0.5), "SAÍDA")
        pdf.line(cmp(5), cmp(linha - 1), cmp(60), cmp(linha - 1))
        linha -= 4
        for dia in contexto["cartao_ponto"]:
            pdf.drawCentredString(
                cmp(15), cmp(linha), f"{dia.Dia.strftime('%d/%m/%Y')}"
            )
            if dia.Ausencia == "":
                pdf.drawCentredString(cmp(35), cmp(linha), f"{dia.Entrada}")
                pdf.drawCentredString(cmp(50), cmp(linha), f"{dia.Saida}")
            else:
                pdf.drawCentredString(cmp(42.5), cmp(linha), f"{dia.Ausencia}")
            linha -= 4
        pdf.rect(
            cmp(5),
            cmp(linha + 3),
            cmp(55),
            cmp(numerodias * 4 + 5),
            fill=0,
        )
    return pdf


def contra_cheque_minutas(pdf, contexto):
    if contexto["minutas"]:
        linha = 140
        numerominutas = len(contexto["minutas"])
        pdf.setFont("Times-Roman", 9)
        pdf.rect(cmp(65), cmp(linha), cmp(140), cmp(6), fill=0)
        pdf.drawCentredString(cmp(135), cmp(linha + 2), "AGENDA")
        linha -= 4
        pdf.setFont("Times-Roman", 9)
        pdf.drawCentredString(cmp(75), cmp(linha + 0.5), "DATA")
        pdf.drawCentredString(cmp(100), cmp(linha + 0.5), "MINUTA")
        pdf.drawCentredString(cmp(130), cmp(linha + 0.5), "CLIENTE")
        pdf.drawCentredString(cmp(165), cmp(linha + 0.5), "INICIO")
        pdf.drawCentredString(cmp(180), cmp(linha + 0.5), "FIM")
        pdf.drawCentredString(cmp(195), cmp(linha + 0.5), "EXTRA")
        pdf.line(cmp(65), cmp(linha - 1), cmp(205), cmp(linha - 1))
        linha -= 4
        for minutas in contexto["minutas"]:
            pdf.drawCentredString(
                cmp(75),
                cmp(linha),
                f'{minutas["data_minuta"].strftime("%d/%m/%Y")}',
            )
            pdf.drawCentredString(
                cmp(100),
                cmp(linha),
                f'{minutas["idminuta"]}',
            )
            pdf.drawCentredString(
                cmp(130),
                cmp(linha),
                f'{minutas["fantasia"]}',
            )
            pdf.drawCentredString(
                cmp(165),
                cmp(linha),
                f'{minutas["hora_inicial"]}',
            )
            pdf.drawCentredString(
                cmp(180),
                cmp(linha),
                f'{minutas["hora_final"]}',
            )
            #  if minutas["Extra"] != "00:00":
            #  pdf.drawCentredString(
            #  cmp(195),
            #  cmp(linha),
            #  "{}".format(minutas["Extra"]),
            #  )
            linha -= 4
        # linha += 3
        pdf.rect(
            cmp(65),
            cmp(linha + 3),
            cmp(140),
            cmp(numerominutas * 4 + 5),
            fill=0,
        )
    return pdf


def foto_colaborador(foto):
    if foto:
        return f"{MEDIA_ROOT}/{foto}"

    return f"{STATIC_ROOT}/website/img/usuario.png"


def preencher_campos_pdf(pdf_base, campos, filename, contexto):
    template_pdf = PdfReader(str(pdf_base))

    output = BytesIO()
    PdfWriter().write(output, template_pdf)
    output.seek(0)

    doc = fitz.open(stream=output.getvalue(), filetype="pdf")
    page = doc[0]

    for widget in page.widgets():
        nome = widget.field_name
        if nome in campos:
            widget.field_value = str(campos[nome])
            widget.update()

    foto_path = foto_colaborador(campos["foto"])
    if campos["descricao"] == "FERIAS":
        rect_top = fitz.Rect(30, 84, 131, 194)
    else:
        rect_top = fitz.Rect(30, 30, 126, 136.5)
    page.insert_image(rect_top, filename=foto_path)

    pdf_bytes = doc.convert_to_pdf()
    flattened_doc = fitz.open("pdf", pdf_bytes)
    doc.close()

    # REMOVE TEMPORÁRIAMENTE A 2ª VIA DO CONTRA-CHEQUE 09/10/2025
    #  if campos["descricao"] != "FERIAS":
        #  page = flattened_doc[0]
        #  clip = fitz.Rect(0, 0, 595, 418)
        #  pix = page.get_pixmap(clip=clip, dpi=150)
        #  image_bytes = pix.tobytes("png")

        #  rect_bottom = fitz.Rect(0, 424, 595, 842)
        #  page.insert_image(rect_bottom, stream=image_bytes)

    if campos["descricao"] == "PAGAMENTO":
        overlay_buffers = BytesIO()
        pdf_ponto = canvas.Canvas(overlay_buffers)

        contra_cheque_cartao_ponto(pdf_ponto, contexto)

        pdf_ponto.save()
        overlay_buffers.seek(0)

        flattened_doc2 = fitz.open(stream=overlay_buffers.getvalue(), filetype="pdf")

        page_top = flattened_doc[0]
        page_base = flattened_doc2[0]

        rect_top = fitz.Rect(0, 0, 595, 421)
        rect_bottom = fitz.Rect(0, 421, 595, 842)

        pix_top = page_top.get_pixmap(clip=rect_top, dpi=150)
        pix_bottom = page_base.get_pixmap(clip=rect_bottom, dpi=150)

        merge_doc = fitz.open()
        new_page = merge_doc.new_page(width=595, height=842)

        new_page.insert_image(rect_top, stream=pix_top.tobytes("png"))
        new_page.insert_image(rect_bottom, stream=pix_bottom.tobytes("png"))

        pdf = BytesIO()
        merge_doc.save(pdf, deflate=True)
        merge_doc.close()
        flattened_doc.close()
        flattened_doc2.close()

    else:
        pdf = BytesIO()
        flattened_doc.save(pdf, deflate=True)
        flattened_doc.close()

    pdf.seek(0)

    response = HttpResponse(pdf.getvalue(), content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{filename}"'

    return response


def sete_digitos_iniciais_cpf(cpf):
    somente_numero = "".join(filter(str.isdigit, cpf.Documento))
    return somente_numero[:7]


def quatro_digitos_finais_cpf(cpf):
    somente_numero = "".join(filter(str.isdigit, cpf.Documento))
    return somente_numero[-4:]


def campos_do_colaborador(campos, colaborador):
    nome = colaborador.nome
    cpf = colaborador.documentos.docs.filter(TipoDocumento="CPF").first()
    ctps = colaborador.documentos.docs.filter(TipoDocumento="CTPS").first()
    ctps_numero = ctps.Documento[:7] if ctps else False
    serie = ctps.Documento[-4:] if ctps else False
    ctps_cpf = sete_digitos_iniciais_cpf(cpf)
    serie_cpf = quatro_digitos_finais_cpf(cpf)
    # TODO Adicionar registro na class do colaborador
    registro = False
    #  registro = colaborador.dados_profissionais.registro
    # TODO Adicionar livro_folha na class do colaborador
    livro_folha = False
    #  livro_folha = colaborador.dados_profissionais.livro_folha
    admissao = colaborador.dados_profissionais.data_admissao
    salario = colaborador.salarios.salarios.Salario


    campos |= {
        "foto": colaborador.foto,
        "codigo": colaborador.id_pessoal.zfill(4),
        "funcao": colaborador.dados_profissionais.categoria,
        "colaborador_1": nome,
        "colaborador_2": nome,
        "colaborador_3": nome,
        "colaborador_4": nome,
        "cpf": f"CPF: {cpf.Documento}",
        "ctps": ctps if ctps_numero else ctps_cpf,
        "serie": serie if ctps_numero else serie_cpf,
        "registro": registro if registro else "",
        "livro": livro_folha if livro_folha else "",
        "admissao": datetime.datetime.strftime(admissao, "%d/%m/%Y"),
        "salario": f"R$ {formatar_numero_com_separadores(salario, 2)}",
        "salario_base": f"R$ {formatar_numero_com_separadores(salario, 2)}",
    }

    return campos


def campos_das_ferias(campos, contexto):
    aquisitivo = contexto["aquisitivo"]
    feria = contexto["feria"]

    aquisitivo_extenso = periodo_por_extenso(
        aquisitivo.DataInicial, aquisitivo.DataFinal
    )
    feria_extenso = periodo_por_extenso(feria.DataInicial, feria.DataFinal)
    faltas = faltas_periodo_aquisitivo(aquisitivo.idPessoal_id, aquisitivo)
    par_de_faltas = []
    for item in range(0, len(faltas), 2):
        par = " ".join(faltas[item:item+2])
        par_de_faltas.append(par)

    campos |= {
        "descricao": "FERIAS",
        "aquisitivo": aquisitivo_extenso,
        "gozo": feria_extenso,
        "faltas": str(len(faltas)).zfill(2),
        "faltas_rows": "\n".join(par_de_faltas),
    }

    return campos


def campos_do_contra_cheque_vencimentos(campos, contra_cheque_itens):
    itens_vencimentos = contra_cheque_itens.filter(Registro="C")


    list_codigos_vencimentos = []
    list_eventos_vencimentos = []
    list_referencias_vencimentos = []
    list_valores_vencimentos = []

    for itens in itens_vencimentos:
        list_codigos_vencimentos.append(f"{itens.Codigo}\n")
        list_eventos_vencimentos.append(f"{itens.Descricao}\n")
        list_referencias_vencimentos.append(f"{itens.Referencia}\n")
        list_valores_vencimentos.append(f"{itens.Valor}\n")

    campos |= {
        "vencimentos_codigos": "".join(list_codigos_vencimentos),
        "vencimentos_eventos": "".join(list_eventos_vencimentos),
        "vencimentos_referencias": "".join(list_referencias_vencimentos),
        "vencimentos_valores": "".join(list_valores_vencimentos),
    }

    return campos


def campos_do_contra_cheque_descontos(campos, contra_cheque_itens):
    itens_descontos = contra_cheque_itens.filter(Registro="D")

    list_codigos_descontos = []
    list_eventos_descontos = []
    list_referencias_descontos = []
    list_valores_descontos = []

    for itens in itens_descontos:
        list_codigos_descontos.append(f"{itens.Codigo}\n")
        list_eventos_descontos.append(f"{itens.Descricao}\n")
        list_referencias_descontos.append(f"{itens.Referencia}\n")
        list_valores_descontos.append(f"{itens.Valor}\n")

    campos |= {
        "descontos_codigos": "".join(list_codigos_descontos),
        "descontos_eventos": "".join(list_eventos_descontos),
        "descontos_referencias": "".join(list_referencias_descontos),
        "descontos_valores": "".join(list_valores_descontos),
    }

    return campos


def campos_do_contra_cheque_totais(campos, saldo):
    vencimentos = saldo["credito"]
    descontos = saldo["debito"]
    total = saldo["saldo"]

    total_extenso = valor_por_extenso(total, tamanho=239)

    campos |= {
        "vencimentos": f"R$ {formatar_numero_com_separadores(vencimentos, 2)}",
        "descontos": f"R$ {formatar_numero_com_separadores(descontos, 2)}",
        "total": f"R$ {formatar_numero_com_separadores(total, 2)}",
        "extenso_1": total_extenso,
        "extenso_2": total_extenso,
    }

    return campos


def campos_datas_aviso_pgto(campos, contexto):
    feria = contexto["feria"]
    data_inicio = feria.DataInicial

    data_aviso = data_inicio - datetime.timedelta(days=30)
    data_aviso = antecipar_data_final_de_semana(data_aviso)
    data_aviso_str = datetime.datetime.strftime(data_aviso, "%d de %B de %Y")

    data_pgto = data_inicio - datetime.timedelta(days=2)
    data_pgto = antecipar_data_final_de_semana(data_pgto)
    data_pgto_str = datetime.datetime.strftime(data_pgto, "%d de %B de %Y")

    campos |= {
        "aviso": f"São Paulo, {data_aviso_str}.",
        "pgto": f"São Paulo, {data_pgto_str}.",
    }
    return campos


def print_recibo_ferias(contexto):
    colaborador = contexto["colaborador"]
    contra_cheque_itens = contexto["contra_cheque_itens"]
    nome_curto = colaborador.nome_curto
    saldo = get_saldo_contra_cheque(contra_cheque_itens)

    campos = {}

    campos_do_colaborador(campos, colaborador)
    campos_das_ferias(campos, contexto)
    campos_do_contra_cheque_vencimentos(campos, contra_cheque_itens)
    campos_do_contra_cheque_descontos(campos, contra_cheque_itens)
    campos_do_contra_cheque_totais(campos, saldo)
    campos_datas_aviso_pgto(campos, contexto)

    pdf_base = Path(f"{STATIC_ROOT}/website/pdf/pdf_base_recibo_ferias.pdf")
    campos |= {"eventos": "", "referencia": "", "valor": ""}
    file_name = f"RECIBO DE FÉRIAS {nome_curto}.pdf"

    return preencher_campos_pdf(pdf_base, campos, file_name, contexto)


def campos_regitro_colaborador(campos, colaborador):
    conta = colaborador.bancos.contas.first()

    campos |= {
        "codigo": colaborador.id_pessoal.zfill(4),
        "pix": f"PIX: {conta.PIX}",
        "funcao": colaborador.dados_profissionais.categoria,
        "local": "0001",
        "depto": "0001",
        "secao": "0001",
        "setor": "0001",
        "folha": "01",
        "tipo_colaborador": "01-COLABORADOR",
    }

    return campos


def campos_do_contra_cheque(campos, colaborador, contra_cheque):
    def fmt(valor):
        return formatar_numero_com_separadores(valor, 2)

    pgto = "RECIBO DE PAGAMENTO DE SALÁRIO"
    conducao = "RECIBO DE VALE TRANSPORTE"
    descricao = contra_cheque.Descricao

    mes_referencia = contra_cheque.MesReferencia
    ano_referencia = contra_cheque.AnoReferencia
    base_inss = fmt(contra_cheque.BaseINSS)
    base_fgts = fmt(contra_cheque.BaseFGTS)
    fgts_mes = fmt(contra_cheque.BaseFGTS / 100 * 8)
    base_irrf = fmt(contra_cheque.BaseIRRF)

    tem_registro = colaborador.dados_profissionais.registrado
    mostrar = tem_registro and descricao == "PAGAMENTO"
    ocultar = "********"

    campos |= {
        "descricao": descricao,
        "recibo": conducao if descricao == "VALE TRANSPORTE" else pgto,
        "tipo_recibo": f"{mes_referencia}/{ano_referencia}",
        "contr_inss": f"R$ {base_inss}" if mostrar else f"{ocultar}",
        "base_fgts": f"R$ {base_fgts}" if mostrar else f"{ocultar}",
        "fgts_mes": f"R$ {fgts_mes}" if mostrar else f"{ocultar}",
        "calc_irrf": f"R$ {base_irrf}" if mostrar else f"{ocultar}",
        "faixa_irrf": f"{ocultar}",
    }

    return campos


def campos_do_contra_cheque_itens(campos, contra_cheque_itens):
    list_codigos = []
    list_eventos = []
    list_referencias = []
    list_valores_vencimentos = []
    list_valores_descontos = []

    for itens in contra_cheque_itens:
        list_codigos.append(f"{itens.Codigo}\n")
        list_eventos.append(f"{itens.Descricao}\n")
        list_referencias.append(f"{itens.Referencia}\n")
        if itens.Registro == "C":
            list_valores_vencimentos.append(f"{itens.Valor}\n")
            list_valores_descontos.append("\n")
        else:
            list_valores_vencimentos.append("\n")
            list_valores_descontos.append(f"{itens.Valor}\n")

    campos |= {
        "codigos_rows": "".join(list_codigos),
        "eventos_rows": "".join(list_eventos),
        "referencias_rows": "".join(list_referencias),
        "vencimentos_rows": "".join(list_valores_vencimentos),
        "descontos_rows": "".join(list_valores_descontos),
    }

    return campos


def campos_de_observacao(campos, colaborador, contra_cheque, faltas):
    admissao = colaborador.dados_profissionais.data_admissao
    admissao_br = datetime.datetime.strftime(admissao, "%d/%m/%Y")

    if faltas:
        faltas = f"{str(len(faltas)).zfill(2)} FALTAS: {' '.join(faltas)}"

    descricao = contra_cheque.Descricao
    mostrar = descricao == "PAGAMENTO" or descricao == "VALE TRANSPORTE"

    campos |= {
        "obs": f"{faltas}\n" if faltas and mostrar else "",
        "obs_2": f"ADMISSÃO: {admissao_br}",
    }

    return campos


def print_contra_cheque_pagamento(contexto):
    colaborador = contexto["colaborador"]
    contra_cheque = contexto["contra_cheque"]
    contra_cheque_itens = contexto["contra_cheque_itens"]
    faltas = contexto["faltas"]
    nome_curto = colaborador.nome_curto
    saldo = get_saldo_contra_cheque(contra_cheque_itens)

    campos = {}

    campos_do_colaborador(campos, colaborador)
    campos_regitro_colaborador(campos, colaborador)
    campos_do_contra_cheque(campos, colaborador, contra_cheque)
    campos_do_contra_cheque_itens(
        campos, contra_cheque_itens.order_by("Codigo")
    )
    campos_do_contra_cheque_totais(campos, saldo)
    campos_de_observacao(campos, colaborador, contra_cheque, faltas)

    pdf_base = Path(f"{STATIC_ROOT}/website/pdf/pdf_base_contra_cheque.pdf")
    campos |= {"eventos": "", "referencia": "", "valor": ""}
    file_name = f"RECIBO DE PAGAMENTO {nome_curto}.pdf"

    return preencher_campos_pdf(pdf_base, campos, file_name, contexto)
