import decimal
from io import BytesIO

from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from website.facade import cmp


def print_pdf_decimno_terceiro(contexto, tipoimpressao):
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = "DÉCIMO TERCEIRO.pdf"
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
            "{}".format("Nome do Funcioonário"),
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
        pdf.drawString(
            cmp(122.8),
            cmp(linha - 17.7),
            "{}".format(contexto["contracheque"][0]),
        )
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(
            cmp(5.8),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"][0].idPessoal).zfill(4),
        )
        pdf.drawString(
            cmp(20.2),
            cmp(linha - 27.4),
            "{}".format(contexto["colaborador"][0].Nome),
        )
        pdf.drawString(
            cmp(102.6),
            cmp(linha - 27.2),
            "{}".format(contexto["colaborador"][0].Categoria),
        )
        pdf.setFont("Times-Roman", 11)
        linhaitens = 0
        for itens in contexto["contrachequeitens"]:
            pdf.drawString(
                cmp(17.5),
                cmp(linha - 41.2 - linhaitens),
                "{}".format(itens.Descricao),
            )
            pdf.drawCentredString(
                cmp(106),
                cmp(linha - 41.2 - linhaitens),
                "{}".format(itens.Referencia),
            )
            pdf.drawRightString(
                cmp(142.6),
                cmp(linha - 41.2 - linhaitens),
                "{}".format(itens.Valor).replace(".", ","),
            )
            linhaitens += 4.1
        pdf.setFont("Times-Roman", 8)
        if contexto["banco"]:
            if contexto["mais_banco"]:
                pdf.drawString(cmp(6), cmp(linha - 124), "*")
            pdf.drawString(
                cmp(8),
                cmp(linha - 124),
                f"PIX: {contexto['banco'][0].PIX} - BANCO: {contexto['banco'][0].Banco} - AG: {contexto['banco'][0].Agencia} - CONTA {contexto['banco'][0].Conta} - {contexto['banco'][0].TipoConta}",
            )
        pdf.setFont("Times-Roman", 11)
        pdf.drawRightString(
            cmp(142.6),
            cmp(linha - 124),
            "{}".format(contexto["totais"]["Credito"]).replace(".", ","),
        )
        pdf.drawRightString(
            cmp(171.7),
            cmp(linha - 124),
            "{}".format(contexto["totais"]["Debito"]).replace(".", ","),
        )
        pdf.drawRightString(
            cmp(171.7),
            cmp(linha - 132),
            "{}".format(contexto["totais"]["Liquido"]).replace(".", ","),
        )
        pdf.drawString(cmp(10), cmp(linha - 139), "SALÁRIO BASE")
        pdf.drawString(
            cmp(10),
            cmp(linha - 144),
            f'R$ {contexto["salario_base"]}'.replace(".", ","),
        )
        # linha = 148
    # pdf.drawString(convertemp(5), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawString(convertemp(70), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawRightString(convertemp(140), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawRightString(convertemp(205), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.setLineWidth(0.5)
    if tipoimpressao == "CONTRACHEQUE":
        if contexto["minutas"]:
            linha = 140
            numerominutas = len(contexto["minutas"])
            pdf.setFont("Times-Roman", 9)
            # pdf.rect(cmp(65), cmp(linha), cmp(140), cmp(6), fill=0)
            pdf.drawCentredString(
                cmp(135),
                cmp(linha + 0.5),
                "AGENDA",
                # "{} - {}".format(len(contexto["minutas"]), "MINUTAS"),
            )
            # linha -= 4
            # pdf.setFont("Times-Roman", 9)
            # pdf.drawCentredString(cmp(75), cmp(linha), "{}".format("DATA"))
            # pdf.drawCentredString(cmp(100), cmp(linha), "{}".format("MINUTA"))
            # pdf.drawCentredString(cmp(130), cmp(linha), "{}".format("CLIENTE"))
            # pdf.drawCentredString(cmp(165), cmp(linha), "{}".format("INICIO"))
            # pdf.drawCentredString(cmp(180), cmp(linha), "{}".format("FIM"))
            # pdf.drawCentredString(cmp(195), cmp(linha), "{}".format("EXTRA"))
            pdf.line(cmp(65), cmp(linha - 1), cmp(205), cmp(linha - 1))
            linha -= 4
            for minutas in contexto["minutas"]:
                pdf.drawCentredString(
                    cmp(75),
                    cmp(linha),
                    "{}".format(
                        minutas["idMinuta_id__DataMinuta"].strftime("%d/%m/%Y")
                    ),
                )
                pdf.drawCentredString(
                    cmp(100),
                    cmp(linha),
                    "{}".format(minutas["idMinuta_id__Minuta"]),
                )
                pdf.drawCentredString(
                    cmp(130),
                    cmp(linha),
                    "{}".format(minutas["idMinuta_id__idCliente__Fantasia"]),
                )
                pdf.drawCentredString(
                    cmp(165),
                    cmp(linha),
                    "{}".format(minutas["idMinuta_id__HoraInicial"]),
                )
                pdf.drawCentredString(
                    cmp(180),
                    cmp(linha),
                    "{}".format(minutas["idMinuta_id__HoraFinal"]),
                )
                if minutas["Extra"] != "00:00":
                    pdf.drawCentredString(
                        cmp(195),
                        cmp(linha),
                        "{}".format(minutas["Extra"]),
                    )
                linha -= 4
            # linha += 3
            pdf.rect(
                cmp(65),
                cmp(linha + 3),
                cmp(140),
                cmp(numerominutas * 4 + 5),
                fill=0,
            )
        if contexto["multas"]:
            numeromultas = len(contexto["multas"])
            linha -= 4
            for multas in contexto["multas"]:
                pdf.setFont("Times-Roman", 7)
                pdf.drawString(cmp(67), cmp(linha), f"DOC - {multas['numero_doc']}")
                pdf.drawString(cmp(90), cmp(linha), f"{multas['placa']}")
                pdf.drawString(
                    cmp(105),
                    cmp(linha),
                    f"{multas['data'].strftime('%d/%m/%Y')} - {multas['hora'].strftime('%H:%M')}",
                )
                pdf.drawString(cmp(130), cmp(linha), f"INFRAÇÃO: {multas['infracao']}")
                linha -= 3
                pdf.drawString(cmp(67), cmp(linha), f"LOCAL: {multas['local']}")
                linha -= 4
            pdf.rect(
                cmp(65),
                cmp(linha + 3),
                cmp(140),
                cmp(numeromultas * 3 + 4),
                fill=0,
            )
        if contexto["cartao_ponto"]:
            linha = 138
            numerodias = len(contexto["cartao_ponto"])
            pdf.setFont("Times-Roman", 9)
            pdf.rect(cmp(5), cmp(linha), cmp(55), cmp(6), fill=0)
            pdf.drawCentredString(cmp(32.5), cmp(linha + 1.5), "CARTÃO DE PONTO")
            linha -= 4
            pdf.setFont("Times-Roman", 9)
            pdf.drawCentredString(cmp(15), cmp(linha), "{}".format("DATA"))
            pdf.drawCentredString(cmp(35), cmp(linha), "{}".format("ENTRADA"))
            pdf.drawCentredString(cmp(50), cmp(linha), "{}".format("SAÍDA"))
            pdf.line(cmp(5), cmp(linha - 1), cmp(60), cmp(linha - 1))
            linha -= 4
            for dia in contexto["cartao_ponto"]:
                pdf.drawCentredString(
                    cmp(15), cmp(linha), f"{dia['dia'].strftime('%d/%m/%Y')}"
                )
                if dia["ausencia"] == "":
                    pdf.drawCentredString(cmp(35), cmp(linha), f"{dia['entrada']}")
                    pdf.drawCentredString(cmp(50), cmp(linha), f"{dia['saida']}")
                else:
                    pdf.drawCentredString(cmp(42.5), cmp(linha), f"{dia['ausencia']}")
                linha -= 4
            pdf.rect(cmp(5), cmp(linha + 3), cmp(55), cmp(numerodias * 4 + 5), fill=0)
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
