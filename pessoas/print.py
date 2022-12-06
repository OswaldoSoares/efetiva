import datetime
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from romaneios.print import header
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
    foto = contexto["colaborador"]["foto"].path
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
    pdf.setFont("Helvetica", 16)
    pdf.setFillColor(HexColor("#FF0000"))
    pdf.drawCentredString(cmp(105), cmp(202), nome)
    pdf.line(cmp(10), cmp(200), cmp(200), cmp(200))
    pdf.circle(cmp(105), cmp(230), 57, stroke=1, fill=0)
    linha = 196
    pdf.setFont("Times-Roman", 12)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawString(cmp(12), cmp(linha), f"DATA DE NSCIMENTO: {data_nascimento}")
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
