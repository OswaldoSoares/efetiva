import datetime
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from pessoas.facade import do_crop
from romaneios.print import header
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import cmp, valor_ponto_milhar


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
        pdf.line(
            cmp(147.8), cmp(linha - 125.2), cmp(147.8), cmp(linha - 116.8)
        )
        pdf.line(
            cmp(147.8), cmp(linha - 134.1), cmp(147.8), cmp(linha - 125.7)
        )
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
        pdf.drawCentredString(
            cmp(56.3), cmp(linha - 35), "{}".format("Descrição")
        )
        pdf.drawCentredString(
            cmp(106), cmp(linha - 35), "{}".format("Referência")
        )
        pdf.drawCentredString(
            cmp(131.95), cmp(linha - 35), "{}".format("Vencimentos")
        )
        pdf.drawCentredString(
            cmp(162.9), cmp(linha - 35), "{}".format("Descontos")
        )
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
                        contexto["colaborador"]["decimo_terceiro"][0][
                            "dozeavos"
                        ]
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
            "DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA "
            "DISCRIMINADA NESTE RECIBO",
        )
        pdf.drawString(cmp(linha - 133), cmp(-197), "_____/_____/_____")
        pdf.drawString(cmp(linha - 133), cmp(-201), "          DATA       ")
        pdf.drawString(
            cmp(linha - 83), cmp(-197), "_______________________________"
        )
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
        pdf.line(
            cmp(147.8), cmp(linha - 125.2), cmp(147.8), cmp(linha - 116.8)
        )
        pdf.line(
            cmp(147.8), cmp(linha - 134.1), cmp(147.8), cmp(linha - 125.7)
        )
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
        pdf.drawCentredString(
            cmp(56.3), cmp(linha - 35), "{}".format("Descrição")
        )
        pdf.drawCentredString(
            cmp(106), cmp(linha - 35), "{}".format("Referência")
        )
        pdf.drawCentredString(
            cmp(131.95), cmp(linha - 35), "{}".format("Vencimentos")
        )
        pdf.drawCentredString(
            cmp(162.9), cmp(linha - 35), "{}".format("Descontos")
        )
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
        #  salario_base = contexto["colaborador"]["salario_ferias"]
        salario_base = contexto["salario_aquisitivo"]
        print(salario_base)
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
            "R$ {}".format(contexto["salario_aquisitivo"]).replace(".", ","),
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
        pdf.drawString(
            cmp(linha - 83), cmp(-197), "_______________________________"
        )
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
    response[
        "Content-Disposition"
    ] = f'filename="FICHA CADASTRAL {nome_curto}.pdf'
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
        if foto == False:
            foto = f"{STATIC_ROOT}/website/img/usuario.png"
    else:
        foto = f"{STATIC_ROOT}/website/img/usuario.png"
    nome = contexto["colaborador"]["nome"]
    categoria = contexto["colaborador"]["categoria"]
    data_nascimento = datetime.datetime.strftime(
        contexto["colaborador"]["data_nascimento"], "%d/%m/%Y"
    )
    mae = contexto["colaborador"]["mae"]
    pai = contexto["colaborador"]["pai"]
    endereco = contexto["colaborador"]["endereco"]
    bairro = contexto["colaborador"]["bairro"]
    cep = contexto["colaborador"]["cep"]
    cidade_estado = contexto["colaborador"]["cidade_estado"]
    doc = contexto["colaborador"]["documentos"]
    fone = contexto["colaborador"]["telefones"]
    banco = contexto["colaborador"]["bancos"]
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
    if contexto["colaborador"]["foto"]:
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
    if doc:
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
        for i in doc:
            linha -= 5
            if i["tipo"] == "HABILITAÇÃO":
                data = datetime.datetime.strftime(i["data_doc"], "%d/%m/%Y")
                pdf.drawString(
                    cmp(12),
                    cmp(linha),
                    f'{i["tipo"]}: {i["documento"]} - VENCIMENTO: {data}',
                )
            else:
                pdf.drawString(
                    cmp(12), cmp(linha), f'{i["tipo"]}: {i["documento"]}'
                )
        linha -= 1.5
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if fone:
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
        for i in fone:
            linha -= 5
            pdf.drawString(cmp(12), cmp(linha), f'{i["tipo"]}: {i["fone"]}')
        linha -= 1.5
        pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    if banco:
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
        for i in banco:
            linha -= 5
            pdf.drawString(
                cmp(12),
                cmp(linha),
                f'{i["banco"]} - AGÊNCIA: {i["agencia"]} CONTA {i["tipo"]}:'
                f' {i["conta"]} - CHAVE PIX: {i["pix"]}',
            )


def print_pdf_rescisao_trabalho(pdf, contexto):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="RESCISAO DE TRABALHO.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf = formulario_rescisao_trabalho(pdf, contexto)
    pdf = dados_rescisao_trabalho(pdf, contexto)
    pdf.setTitle(f"RESCISÃO DE TRABALHO - .pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


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
        if x["registro"] == "C":
            if x["descricao"].startswith("SALARIO"):
                descricao = x["descricao"].replace(
                    "SALARIO", "SALDO DE SALARIO"
                )
            else:
                descricao = x["descricao"]
            pdf.drawString(
                cmp(col), cmp(linha), f"{descricao} - {x['referencia']}"
            )
            pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {x['valor']}")
            bruto += x["valor"]
            if col == 11:
                col = 106
            else:
                col = 11
                linha -= 7.7
    pdf.drawString(
        cmp(col), cmp(linha), f"FÉRIAS PROPORCIONAIS - {meses_ferias}/12"
    )
    pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {ferias}")
    if col == 11:
        col = 106
    else:
        col = 11
        linha -= 7.7
    pdf.drawString(cmp(col), cmp(linha), f"1/3 FÉRIAS PROPORCIONAIS")
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
    pdf.drawRightString(cmp(199), cmp(linha + 1), f"R$ {bruto}")
    linha -= 7.7
    linha -= 4
    linha += 1
    deducoes = Decimal(0.00)
    col = 11
    for x in contexto["rescisao"][0]["folha_contra_cheque_itens"]:
        if x["registro"] == "D":
            pdf.drawString(cmp(col), cmp(linha), f"{x['descricao']}")
            pdf.drawRightString(cmp(col + 93), cmp(linha), f"R$ {x['valor']}")
            deducoes += x["valor"]
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
