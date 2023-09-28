import datetime
from decimal import Decimal
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from website.facade import cmp, valor_ponto_milhar


def print_minutas_periodo(contexto):
    inicial = datetime.datetime.strptime(
        contexto["inicial"], "%Y-%m-%d"
    ).date()
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
    # pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
    pdf.drawString(cmp(15), cmp(196.4), f"{data_hora}")
    pdf.drawCentredString(cmp(148.5), cmp(196.4), titulo)
    pdf.drawRightString(cmp(282), cmp(196.4), f"PÁGINA: {pagina}")
    return pdf


def body(pdf, contexto, titulo):
    # BUG O final de cada pagina está estourando o limite, corrigir isso.
    minutas = contexto["minutas"]
    linha = 195
    total_seguro_geral = 0.00
    total_despesas_geral = Decimal(0.00)
    total_peso_geral = Decimal(0.00)
    for item_x in minutas:
        if linha <= 20:
            pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
            pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
            pdf.showPage()
            header(pdf, titulo)
            linha = 195
        data = item_x["data"].strftime("%d/%m/%Y")
        minuta = item_x["numero"]
        status_minuta = item_x["status_minuta"]
        cliente = item_x["cliente"]
        solicitado = item_x["veiculo_solicitado"]
        motorista = None
        if item_x["motorista"]:
            motorista = item_x["motorista"][0]["apelido"]
        placa = item_x["veiculo"]
        entregas = str(item_x["quantidade_entregas"]).zfill(2)
        pdf.setFillColor(HexColor("#B0C4DE"))
        pdf.rect(cmp(10), cmp(linha-4), cmp(277), cmp(4), fill=1, stroke=0)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawString(cmp(12), cmp(linha-3), f"{data}")
        pdf.drawString(cmp(33), cmp(linha-3), f"{minuta}")
        pdf.drawString(cmp(43), cmp(linha-3), f"{status_minuta}")
        pdf.drawString(cmp(65), cmp(linha-3), f"{cliente}")
        pdf.drawString(cmp(125), cmp(linha-3), f"{solicitado}")
        if motorista:
            pdf.drawString(cmp(175), cmp(linha-3), f"{motorista}")
        pdf.drawString(cmp(230), cmp(linha-3), f"{placa}")
        pdf.drawRightString(cmp(285), cmp(linha-3), f"ENTREGAS: {entregas}")
        pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
        linha -= 3.5
        linha_top = linha - 0.5
        pdf.drawCentredString(cmp(35), cmp(linha-3), "AJUDANTES")
        pdf.drawCentredString(cmp(75), cmp(linha-3), "ROMANEIO")
        pdf.drawCentredString(cmp(105), cmp(linha-3), "PESO")
        # pdf.drawCentredString(cmp(135), cmp(linha-3), "ENTREGAS")
        pdf.drawCentredString(cmp(175), cmp(linha-3), "DESPESAS DESCRIÇÃO")
        pdf.drawCentredString(cmp(225), cmp(linha-3), "VALOR")
        pdf.drawCentredString(cmp(263.5), cmp(linha-3), "OBS")
        linha -= 3.5
        linha_for = linha
        for item_y in item_x["ajudantes"]:
            apelido = item_y["apelido"]
            pdf.drawString(cmp(12), cmp(linha_for-3), f"{apelido}")
            linha_for -= 3
        linha_final = linha_for
        linha_for = linha
        peso_total = Decimal(0.00)
        for item_y in item_x["romaneio_pesos"]:
            romaneio = item_y["romaneio"]
            peso = valor_ponto_milhar(item_y["peso"], 3)
            if item_y["peso"]:
                peso_total += item_y["peso"]
                total_peso_geral += item_y["peso"]
            pdf.drawCentredString(cmp(75), cmp(linha_for-3), f"{romaneio}")
            pdf.drawRightString(cmp(118), cmp(linha_for-3), f"{peso} kg")
            linha_for -= 3
        linha_final = min(linha_final, linha_for)
        linha_for = linha
        for item_y in item_x["despesas"]:
            descricao = item_y["Descricao"]
            valor_despesa = valor_ponto_milhar(item_y["Valor"], 2)
            obs = item_y["Obs"]
            pdf.drawString(cmp(152), cmp(linha_for-3), f"{descricao}")
            pdf.drawRightString(
                cmp(238),
                cmp(linha_for-3),
                f"R$ {valor_despesa}"
            )
            pdf.drawString(cmp(242), cmp(linha_for-3), f"{obs}")
            linha_for -= 3
        linha_final = min(linha_final, linha_for)
        linha = linha_final - 1
        pdf.line(cmp(60), cmp(linha), cmp(60), cmp(linha_top))
        pdf.line(cmp(90), cmp(linha), cmp(90), cmp(linha_top))
        pdf.line(cmp(120), cmp(linha), cmp(120), cmp(linha_top))
        pdf.line(cmp(150), cmp(linha), cmp(150), cmp(linha_top))
        peso_total = valor_ponto_milhar(peso_total, 3)
        if item_x["romaneio_pesos"] or item_x["despesas"]:
            pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
            if item_x["romaneio_pesos"]:
                pdf.drawRightString(
                    cmp(118),
                    cmp(linha-3),
                    f'Peso Total: {peso_total} kg'
                )
            if item_x["despesas"]:
                total_despesas = valor_ponto_milhar(
                    item_x["t_despesas"]["valor_despesas"], 2
                )
                total_despesas_geral += item_x["t_despesas"]["valor_despesas"]
                pdf.drawRightString(
                    cmp(238),
                    cmp(linha-3),
                    f"Total Despesas: R$ {total_despesas}"
                )
            linha -= 4
        valor_seguro = valor_ponto_milhar(item_x["recebe"]["t_segu"], 2)
        total_seguro_geral += item_x["recebe"]["t_segu"]
        valor_calculo = valor_ponto_milhar(item_x["recebe_minuta"], 2)
        valor_minuta = valor_ponto_milhar(item_x["valor_minuta"], 2)
        pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
        pdf.drawCentredString(
            cmp(56.5),
            cmp(linha-3),
            f"Seguro: R$ {valor_seguro}"
        )
        pdf.drawCentredString(
            cmp(148.5),
            cmp(linha-3),
            f"Calculo R$ {valor_calculo}"
        )
        pdf.drawCentredString(
            cmp(240.5),
            cmp(linha-3),
            f"Valor R$ {valor_minuta}")
        linha -= 4
    pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
    total_seguro_geral = valor_ponto_milhar(total_seguro_geral, 2)
    total_despesas_geral = valor_ponto_milhar(total_despesas_geral, 2)
    total_peso_geral = valor_ponto_milhar(total_peso_geral, 3)
    pdf.line(cmp(10), cmp(15.5), cmp(287), cmp(15.5))
    pdf.drawString(cmp(12), cmp(12), f"{str(len(minutas)).zfill(2)} MINUTAS")
    pdf.drawRightString(
        cmp(285),
        cmp(12),
        f"TOTAL SEGUROS: R$ {total_seguro_geral} - PESO TOTAL: {total_peso_geral} kg - TOTAL DESPESAS: R$ {total_despesas_geral}"
    )
    pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
    return pdf
