import datetime
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pessoas.facade import do_crop
from romaneios.print import header
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import cmp


def print_pdf_decimno_terceiro(contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="DÉCIMO TERCEIRO.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    linha = 297
    for x in range(1):
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
        pdf.setFillColor(HexColor("#808080"))
        pdf.setFont("Times-Roman", 14)
        pdf.drawString(
            cmp(101.6),
            cmp(linha - 11),
            "{}".format("Recibo de Pagamento de 13º Salário"),
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(cmp(5.8), cmp(linha - 22.9), "{}".format("Código"))
        pdf.drawString(
            cmp(20.2),
            cmp(linha - 22.9),
            "{}".format("Nome do Funcionário"),
        )
        pdf.drawString(
            cmp(102.6),
            cmp(linha - 22.9),
            "{}".format("CBO    Emp.   Local   Dept.  Setor   Seção   Fl."),
        )
        pdf.drawCentredString(cmp(10.85), cmp(linha - 35), "{}".format("Cód."))
        pdf.drawCentredString(cmp(56.3), cmp(linha - 35), "{}".format("Descrição"))
        pdf.drawCentredString(cmp(106), cmp(linha - 35), "{}".format("Referência"))
        pdf.drawCentredString(cmp(131.95), cmp(linha - 35), "{}".format("Vencimentos"))
        pdf.drawCentredString(cmp(162.9), cmp(linha - 35), "{}".format("Descontos"))
        pdf.setFont("Times-Roman", 9)
        pdf.drawCentredString(
            cmp(131.95),
            cmp(linha - 119.7),
            "{}".format("Total de Vencimentos"),
        )
        pdf.drawCentredString(
            cmp(162.9),
            cmp(linha - 119.7),
            "{}".format("Total de Descontos"),
        )
        pdf.drawCentredString(
            cmp(131.95),
            cmp(linha - 132),
            "{} {}".format("Valor Líquido", "\u279C"),
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(
            cmp(6),
            cmp(linha - 13.8),
            "{}".format("TRANSEFETIVA TRANSPORTES - EIRELLI - ME"),
        )
        pdf.drawString(
            cmp(6),
            cmp(linha - 17.7),
            "{}".format("CNPJ: 21.602.117/0001-15"),
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(
            cmp(5.8),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"]["idpes"]).zfill(4),
        )
        pdf.drawString(
            cmp(20.2),
            cmp(linha - 27.4),
            "{}".format(contexto["colaborador"]["nome"]),
        )
        pdf.drawString(
            cmp(102.6),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"]["categoria"]),
        )
        pdf.setFont("Times-Roman", 11)
        linhaitens = 0
        for itens in contexto["colaborador"]["decimo_terceiro"][0]["parcelas"]:
            if itens.idParcelasDecimoTerceiro == int(contexto["idparcela"]):
                pdf.drawString(
                    cmp(17.5),
                    cmp(linha - 41.2 - linhaitens),
                    "13º {}ª Parcela".format(itens.Parcela),
                )
                pdf.drawCentredString(
                    cmp(106),
                    cmp(linha - 41.2 - linhaitens),
                    "0{}".format(
                        contexto["colaborador"]["decimo_terceiro"][0]["dozeavos"]
                    ),
                )
                pdf.drawRightString(
                    cmp(142.6),
                    cmp(linha - 41.2 - linhaitens),
                    "{}".format(itens.Valor).replace(".", ","),
                )
                pdf.setFont("Times-Roman", 11)
                pdf.drawRightString(
                    cmp(142.6),
                    cmp(linha - 124),
                    "{}".format(itens.Valor).replace(".", ","),
                )
                pdf.drawRightString(cmp(171.7), cmp(linha - 124), "R$ 0,00")
                pdf.drawRightString(
                    cmp(171.7),
                    cmp(linha - 132),
                    "{}".format(itens.Valor).replace(".", ","),
                )
        pdf.setFont("Times-Roman", 8)
        # if contexto["banco"]:
        #     if contexto["mais_banco"]:
        #         pdf.drawString(cmp(6), cmp(linha - 124), "*")
        #     pdf.drawString(
        #         cmp(8),
        #         cmp(linha - 124),
        #         f"PIX: {contexto['banco'][0].PIX} - BANCO: {contexto['banco'][0].Banco} - AG: {contexto['banco'][0].Agencia} - CONTA {contexto['banco'][0].Conta} - {contexto['banco'][0].TipoConta}",
        #     )
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(cmp(10), cmp(linha - 139), "SALÁRIO BASE")
        pdf.drawString(
            cmp(10),
            cmp(linha - 144),
            f'R$ {contexto["colaborador"]["decimo_terceiro"][0]["valor_base"]}'.replace(
                ".", ","
            ),
        )
    pdf.setFont("Times-Roman", 9)
    pdf.setFillColor(HexColor("#808080"))
    pdf.line(cmp(0), cmp(148.5), cmp(210), cmp(148.5))
    pdf.rotate(90)
    linha = 297
    for x in range(1):
        pdf.drawString(
            cmp(linha - 138),
            cmp(-186),
            "DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA " "DISCRIMINADA NESTE RECIBO",
        )
        pdf.drawString(cmp(linha - 133), cmp(-197), "_____/_____/_____")
        pdf.drawString(cmp(linha - 133), cmp(-201), "          DATA       ")
        pdf.drawString(cmp(linha - 83), cmp(-197), "_______________________________")
        pdf.drawString(cmp(linha - 83), cmp(-201), "ASSINATURA DO FUNCIONÁRIO")
        # linha = 148.5
    pdf.setTitle("contracheque.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def print_pdf_ferias(contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="FÉRIAS.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    linha = 297
    for x in range(1):
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
        pdf.setFillColor(HexColor("#808080"))
        pdf.setFont("Times-Roman", 14)
        pdf.drawString(
            cmp(101.6),
            cmp(linha - 11),
            "{}".format("Recibo de Pagamento de Férias"),
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(cmp(5.8), cmp(linha - 22.9), "{}".format("Código"))
        pdf.drawString(
            cmp(20.2),
            cmp(linha - 22.9),
            "{}".format("Nome do Funcionário"),
        )
        pdf.drawString(
            cmp(102.6),
            cmp(linha - 22.9),
            "{}".format("CBO    Emp.   Local   Dept.  Setor   Seção   Fl."),
        )
        pdf.drawCentredString(cmp(10.85), cmp(linha - 35), "{}".format("Cód."))
        pdf.drawCentredString(cmp(56.3), cmp(linha - 35), "{}".format("Descrição"))
        pdf.drawCentredString(cmp(106), cmp(linha - 35), "{}".format("Referência"))
        pdf.drawCentredString(cmp(131.95), cmp(linha - 35), "{}".format("Vencimentos"))
        pdf.drawCentredString(cmp(162.9), cmp(linha - 35), "{}".format("Descontos"))
        pdf.setFont("Times-Roman", 9)
        pdf.drawCentredString(
            cmp(131.95),
            cmp(linha - 119.7),
            "{}".format("Total de Vencimentos"),
        )
        pdf.drawCentredString(
            cmp(162.9),
            cmp(linha - 119.7),
            "{}".format("Total de Descontos"),
        )
        pdf.drawCentredString(
            cmp(131.95),
            cmp(linha - 132),
            "{} {}".format("Valor Líquido", "\u279C"),
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(
            cmp(6),
            cmp(linha - 13.8),
            "{}".format("TRANSEFETIVA TRANSPORTES - EIRELLI - ME"),
        )
        pdf.drawString(
            cmp(6),
            cmp(linha - 17.7),
            "{}".format("CNPJ: 21.602.117/0001-15"),
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(
            cmp(5.8),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"]["idpes"]).zfill(4),
        )
        pdf.drawString(
            cmp(20.2),
            cmp(linha - 27.4),
            "{}".format(contexto["colaborador"]["nome"]),
        )
        pdf.drawString(
            cmp(102.6),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"]["categoria"]),
        )
        pdf.setFont("Times-Roman", 11)
        linhaitens = 0
        salario_base = contexto["colaborador"]["salario_ferias"]
        aquisitivo_inicial = datetime.datetime.strftime(
            contexto["aquisitivo"].DataInicial, "%d/%m/%Y"
        )
        aquisitivo_final = datetime.datetime.strftime(
            contexto["aquisitivo"].DataFinal, "%d/%m/%Y"
        )
        um_terco = round(salario_base / 100 * Decimal(33.3333), 2)
        total = salario_base + um_terco
        faltas = len(contexto["colaborador"]["faltas"])
        if faltas < 6:
            data_referencia = "30d"
        elif faltas > 5 and faltas < 15:
            data_referencia = "24d"
        elif faltas > 14 and faltas < 24:
            data_referencia = "18d"
        elif faltas > 23 and faltas < 33:
            data_referencia = "12d"
        pdf.drawString(
            cmp(17.5),
            cmp(linha - 41.2 - linhaitens),
            "FÉRIAS",
        )
        pdf.setFont("Times-Roman", 8)
        pdf.drawString(
            cmp(32),
            cmp(linha - 40.9 - linhaitens),
            f"(PERÍODO AQUISITIVO {aquisitivo_inicial} - E {aquisitivo_final})",
        )
        pdf.setFont("Times-Roman", 11)
        pdf.drawCentredString(
            cmp(106),
            cmp(linha - 41.2 - linhaitens),
            f"{data_referencia}",
        )
        pdf.drawRightString(
            cmp(142.6),
            cmp(linha - 41.2 - linhaitens),
            "R$ {}".format(salario_base).replace(".", ","),
        )
        linhaitens += 4
        pdf.drawString(
            cmp(17.5),
            cmp(linha - 41.2 - linhaitens),
            "ADICIONAL 1/3 S/FÉRIAS",
        )
        pdf.drawCentredString(
            cmp(106),
            cmp(linha - 41.2 - linhaitens),
            "33,333%",
        )
        pdf.drawRightString(
            cmp(142.6),
            cmp(linha - 41.2 - linhaitens),
            "R$ {}".format(um_terco).replace(".", ","),
        )
        pdf.setFont("Times-Roman", 11)
        pdf.drawRightString(
            cmp(142.6),
            cmp(linha - 124),
            "R$ {}".format(total).replace(".", ","),
        )
        pdf.drawRightString(cmp(171.7), cmp(linha - 124), "R$ 0,00")
        pdf.drawRightString(
            cmp(171.7),
            cmp(linha - 132),
            "R$ {}".format(total).replace(".", ","),
        )
        pdf.setFont("Times-Roman", 8)
        # if contexto["banco"]:
        #     if contexto["mais_banco"]:
        #         pdf.drawString(cmp(6), cmp(linha - 124), "*")
        #     pdf.drawString(
        #         cmp(8),
        #         cmp(linha - 124),
        #         f"PIX: {contexto['banco'][0].PIX} - BANCO: {contexto['banco'][0].Banco} - AG: {contexto['banco'][0].Agencia} - CONTA {contexto['banco'][0].Conta} - {contexto['banco'][0].TipoConta}",
        #     )
        pdf.drawString(
            cmp(6),
            cmp(linha - 124),
            f"FALTAS NO PERIODO AQUISITIVO: {faltas}",
        )
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(cmp(10), cmp(linha - 139), "SALÁRIO BASE")
        pdf.drawString(
            cmp(10),
            cmp(linha - 144),
            "R$ {}".format(contexto["colaborador"]["salario"][0]["salario"]).replace(
                ".", ","
            ),
        )
    pdf.setFont("Times-Roman", 9)
    pdf.setFillColor(HexColor("#808080"))
    pdf.line(cmp(0), cmp(148.5), cmp(210), cmp(148.5))
    pdf.rotate(90)
    linha = 297
    for x in range(1):
        pdf.drawString(
            cmp(linha - 138),
            cmp(-186),
            "DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA DISCRIMINADA NESTE RECIBO",
        )
        pdf.drawString(cmp(linha - 133), cmp(-197), "_____/_____/_____")
        pdf.drawString(cmp(linha - 133), cmp(-201), "          DATA       ")
        pdf.drawString(cmp(linha - 83), cmp(-197), "_______________________________")
        pdf.drawString(cmp(linha - 83), cmp(-201), "ASSINATURA DO FUNCIONÁRIO")
        # linha = 148.5
    pdf.setTitle("contracheque.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def print_pdf_ficha_colaborador(contexto):
    nome_curto = contexto["colaborador"]["nome_curto"]
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="FICHA CADASTRAL {nome_curto}.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf, contexto)
    ficha_colaborador(pdf, contexto)
    pdf.setTitle(f"FICHA CADSTRAl {nome_curto}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def ficha_colaborador(pdf, contexto):
    if contexto["colaborador"]["foto"]:
        foto = contexto["colaborador"]["foto"].path
        foto = do_crop(foto)
    else:
        foto = f"{STATIC_ROOT}/website/img/usuario.png"
    nome = contexto["colaborador"]["nome"]
    data_nascimento = datetime.datetime.strftime(
        contexto["colaborador"]["data_nascimento"], "%d/%m/%Y"
    )
    mae = contexto["colaborador"]["mae"]
    pai = contexto["colaborador"]["pai"]
    doc = contexto["colaborador"]["documentos"]
    fone = contexto["colaborador"]["telefones"]
    pdf.drawCentredString(cmp(105), cmp(255.8), "FICHA CADASTRAL")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    pdf.drawImage(foto, cmp(85), cmp(210), cmp(40), cmp(40), mask="auto")
    pdf.setFont("Helvetica", 15)
    pdf.setFillColor(HexColor("#FF0000"))
    pdf.drawCentredString(cmp(105), cmp(202), nome)
    pdf.line(cmp(10), cmp(200), cmp(200), cmp(200))
    if contexto["colaborador"]["foto"]:
        pdf.circle(cmp(105), cmp(230), 57, stroke=1, fill=0)
    linha = 196
    pdf.setFont("Times-Roman", 12)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawString(cmp(12), cmp(linha), f"DATA DE NASCIMENTO: {data_nascimento}")
    if mae:
        linha -= 5
        pdf.drawString(cmp(12), cmp(linha), f"NOME DA MÃE: {mae}")
    if pai:
        linha -= 5
        pdf.drawString(cmp(12), cmp(linha), f"NOME DO PAI: {pai}")
    linha -= 1
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if doc:
        linha -= 6
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(5), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(cmp(105), cmp(linha + 1), "DOCUMENTOS")
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha += 1
        for i in doc:
            linha -= 5
            pdf.drawString(cmp(12), cmp(linha), f'{i["tipo"]}: {i["documento"]}')
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if fone:
        linha -= 6
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.setStrokeColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(5), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(cmp(105), cmp(linha + 1), "TELEFONES")
        linha -= 1
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
        linha += 1
        for i in fone:
            linha -= 5
            pdf.drawString(cmp(12), cmp(linha), f'{i["tipo"]}: {i["fone"]}')


def print_pdf_rescisao_trabalho(pdf, contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="RESCISAO DE TRABALHO.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf = formulario_rescisao_trabalho(pdf, contexto)

    pdf.setTitle(f"RESCISÃO DE TRABALHO - .pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def formulario_rescisao_trabalho(pdf, contexto):
    pdf.setFont("Times-Roman", 12)
    pdf.rect(cmp(10), cmp(10), cmp(190), cmp(277), fill=0)
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(11), cmp(281), cmp(188), cmp(5), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(105), cmp(282), "RESCISÃO DO CONTRATO DE TRABALHO")
    pdf.setFont("Times-Roman", 10)
    pdf.rect(cmp(10), cmp(275), cmp(190), cmp(5), fill=0)
    pdf.drawCentredString(cmp(105), cmp(276), "IDENTIFICAÇÃO DO EMPREGADOR")
    pdf.drawString(cmp(11), cmp(271), "CNPJ: 21.602.117/0001-15")
    razao = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    pdf.drawString(cmp(80), cmp(271), f"RAZAO SOCIAL: {razao}")
    endereco = "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010"
    pdf.drawString(cmp(11), cmp(266), f"ENDEREÇO: {endereco}")
    pdf.rect(cmp(10), cmp(251), cmp(190), cmp(5), fill=0)
    pdf.drawCentredString(cmp(105), cmp(252), "IDENTIFICAÇÃO DO TRABALHADOR")
    for x in contexto["colaborador"]["documentos"]:
        if x["tipo"] == "CPF":
            pdf.drawString(cmp(11), cmp(247), f"CPF: {x['documento']}")
    pdf.drawString(cmp(80), cmp(247), f"NOME: {contexto['colaborador']['nome']}")
    endereco = contexto["colaborador"]["endereco"]
    bairro = contexto["colaborador"]["bairro"]
    cidade = contexto["colaborador"]["cidade"]
    cep = contexto["colaborador"]["cep"]
    pdf.drawString(
        cmp(11),
        cmp(242),
        f"ENDEREÇO: {endereco} - {bairro} - {cidade} - SP - CEP {cep}",
    )
    nascimento = datetime.datetime.strftime(
        contexto["colaborador"]["data_nascimento"], "%d/%m/%Y"
    )
    pdf.drawString(cmp(10), cmp(237), f"NASCIMENTO: {nascimento}")
    pdf.drawString(cmp(80), cmp(237), f"MÃE: {contexto['colaborador']['mae']}")
    pdf.rect(cmp(10), cmp(227), cmp(190), cmp(5), fill=0)
    pdf.drawCentredString(cmp(105), cmp(228), "DADOS CONTRATO")
    pdf.drawString(
        cmp(11), cmp(223), f"CATEGORIA: {contexto['colaborador']['categoria']}"
    )
    salario = contexto["colaborador"]["salario"][0]["salario"]
    pdf.drawString(cmp(80), cmp(223), f"SALÁRIO: R$ {salario}")
    admissao = datetime.datetime.strftime(
        contexto["colaborador"]["data_admissao"], "%d/%m/%Y"
    )
    demissao = datetime.datetime.strftime(
        contexto["colaborador"]["data_demissao"], "%d/%m/%Y"
    )
    pdf.drawString(cmp(11), cmp(218), f"ADMISSÃO: {admissao}")
    pdf.drawString(cmp(80), cmp(218), f"AFASTAMENTO: {demissao}")
    pdf.drawString(
        cmp(11), cmp(213), f"CAUSA DO AFASTAMENTO: PEDIDO DE DEMISSÃO PELO FUNCIONÁRIO"
    )
    pdf.rect(cmp(10), cmp(203), cmp(190), cmp(5), fill=0)
    pdf.drawCentredString(cmp(105), cmp(204), "VERBAS RESCISORIA")
    linha = 199
    bruto = Decimal(0.00)
    meses_ferias = contexto["rescisao"][0]["meses_ferias"]
    ferias = contexto["rescisao"][0]["ferias"]
    bruto += ferias
    terco_ferias = contexto["rescisao"][0]["terco_ferias"]
    bruto += terco_ferias
    meses_decimo_terceiro = contexto["rescisao"][0]["meses_decimo_terceiro"]
    decimo_terceiro = contexto["rescisao"][0]["decimo_terceiro"]
    bruto += decimo_terceiro
    pdf.drawString(cmp(11), cmp(linha), f"FÉRIAS PROPORCIONAIS - {meses_ferias}/12")
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {ferias}")
    linha -= 5
    pdf.drawString(cmp(11), cmp(linha), f"1/3 FÉRIAS PROPORCIONAIS")
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {terco_ferias}")
    linha -= 5
    pdf.drawString(
        cmp(11), cmp(linha), f"13º PROPORCIONAL - {meses_decimo_terceiro}/12"
    )
    pdf.drawRightString(cmp(199), cmp(linha), f"R$ {decimo_terceiro}")
    linha -= 5
    for x in contexto["rescisao"][0]["folha_contra_cheque_itens"]:
        if x["registro"] == "C":
            pdf.drawString(cmp(11), cmp(linha), f"{x['descricao']} - {x['referencia']}")
            pdf.drawRightString(cmp(199), cmp(linha), f"R$ {x['valor']}")
            bruto += x["valor"]
            linha -= 5
    linha -= 5
    pdf.drawRightString(cmp(199), cmp(linha), f"TOTAL BRUTO - R$ {bruto}")
    linha -= 10
    pdf.rect(cmp(10), cmp(linha - 1), cmp(190), cmp(5), fill=0)
    pdf.drawCentredString(cmp(105), cmp(linha), "DEDUÇÕES")
    linha -= 5
    deducoes = Decimal(0.00)
    for x in contexto["rescisao"][0]["folha_contra_cheque_itens"]:
        if x["registro"] == "D":
            pdf.drawString(cmp(11), cmp(linha), f"{x['descricao']}")
            pdf.drawRightString(cmp(199), cmp(linha), f"R$ {x['valor']}")
            deducoes += x["valor"]
            linha -= 5
    linha -= 5
    pdf.drawRightString(cmp(199), cmp(linha), f"TOTAL DEDUÇÕES - R$ {deducoes}")
    linha -= 20
    pdf.drawCentredString(cmp(105), cmp(50), f"VALOR LIQUIDO - R$ {bruto - deducoes}")
    pdf.line(cmp(50), cmp(19), cmp(160), cmp(19))
    pdf.drawCentredString(cmp(105), cmp(15), f"{contexto['colaborador']['nome']}")
    return pdf
