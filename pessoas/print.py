import datetime
import ast
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from reportlab.lib.enums import TA_JUSTIFY
from pessoas.facade import do_crop
from romaneios.print import header
from transefetiva.settings.settings import STATIC_ROOT
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
    response["Content-Disposition"] = f'filename="RESCISAO DE TRABALHO.pdf"'
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
    print(contexto)
    print("Teste")
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
    meses_decimo_terceiro = contexto["decimo_terceiro_meses"]
    decimo_terceiro = contexto["decimo_terceiro_valor"]
    decimo_terceiro_pago = contexto["decimo_terceiro_total_pago"]
    ferias_paga = contexto["desconto_ferias"]
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
    if meses_decimo_terceiro:
        pdf.drawString(
            cmp(col),
            cmp(linha),
            f"13º PROPORCIONAL - {meses_decimo_terceiro}/12",
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
    if contexto["decimo_terceiro_parcelas_pagas"]:
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
    if contexto["desconto_ferias"]:
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
    pdf.drawString(cmp(col), cmp(linha), f"1/3 FÉRIAS PROPORCIONAIS")
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
    return pdf


def base_contra_cheque(pdf):
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
    pdf.drawString(cmp(10), cmp(linha - 139), "SALÁRIO BASE")
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
    response["Content-Disposition"] = f'filename="Contra Cheque.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    contra_cheque_dados(pdf, contexto)
    contra_cheque_itens(pdf, contexto)
    contra_cheque_totais(pdf, contexto)
    if contexto["contra_cheque"].Descricao == "PAGAMENTO":
        contra_cheque_cartao_ponto(pdf, contexto)
        contra_cheque_minutas(pdf, contexto)
    base_contra_cheque(pdf)
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
    pdf.drawString(
        cmp(10),
        cmp(linha - 144),
        f"R$ {salario_base}",
    )
    contra_cheque_obs(pdf, contexto)
    return pdf


def contra_cheque_itens(pdf, contexto):
    linha = 297
    linhaitens = 0
    for itens in contexto["contra_cheque_itens"]:
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
