"""
    Modulo impressões de relátorios
"""
import datetime
from decimal import Decimal
from io import BytesIO

from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4, landscape
from reportlab.pdfgen import canvas
from website.facade import valor_ponto_milhar

from textwrap import wrap
from minutas.models import Minuta, MinutaColaboradores
from clientes.models import FoneContatoCliente
from transefetiva.settings.settings import STATIC_ROOT
from core.tools import convert_milimetro_pontos as cmp
from veiculos.models import Veiculo


def print_minutas_periodo(contexto):
    """

    Args:
        contexto:

    Returns:


    """
    inicial = datetime.datetime.strptime(
        contexto["inicial"],
        "%Y-%m-%d",
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
    """

    Args:
        pdf:
        titulo:

    Returns:


    """
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
    """

    Args:
        pdf:
        contexto:
        titulo:

    Returns:


    """
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
        pdf.rect(cmp(10), cmp(linha - 4), cmp(277), cmp(4), fill=1, stroke=0)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawString(cmp(12), cmp(linha - 3), f"{data}")
        pdf.drawString(cmp(33), cmp(linha - 3), f"{minuta}")
        pdf.drawString(cmp(43), cmp(linha - 3), f"{status_minuta}")
        pdf.drawString(cmp(65), cmp(linha - 3), f"{cliente}")
        pdf.drawString(cmp(125), cmp(linha - 3), f"{solicitado}")
        if motorista:
            pdf.drawString(cmp(175), cmp(linha - 3), f"{motorista}")
        pdf.drawString(cmp(230), cmp(linha - 3), f"{placa}")
        pdf.drawRightString(cmp(285), cmp(linha - 3), f"ENTREGAS: {entregas}")
        pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
        linha -= 3.5
        linha_top = linha - 0.5
        pdf.drawCentredString(cmp(35), cmp(linha - 3), "AJUDANTES")
        pdf.drawCentredString(cmp(75), cmp(linha - 3), "ROMANEIO")
        pdf.drawCentredString(cmp(105), cmp(linha - 3), "PESO")
        # pdf.drawCentredString(cmp(135), cmp(linha-3), "ENTREGAS")
        pdf.drawCentredString(cmp(175), cmp(linha - 3), "DESPESAS DESCRIÇÃO")
        pdf.drawCentredString(cmp(225), cmp(linha - 3), "VALOR")
        pdf.drawCentredString(cmp(263.5), cmp(linha - 3), "OBS")
        linha -= 3.5
        linha_for = linha
        for item_y in item_x["ajudantes"]:
            apelido = item_y["apelido"]
            pdf.drawString(cmp(12), cmp(linha_for - 3), f"{apelido}")
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
            pdf.drawCentredString(cmp(75), cmp(linha_for - 3), f"{romaneio}")
            pdf.drawRightString(cmp(118), cmp(linha_for - 3), f"{peso} kg")
            linha_for -= 3
        linha_final = min(linha_final, linha_for)
        linha_for = linha
        for item_y in item_x["despesas"]:
            descricao = item_y["Descricao"]
            valor_despesa = valor_ponto_milhar(item_y["Valor"], 2)
            obs = item_y["Obs"]
            pdf.drawString(cmp(152), cmp(linha_for - 3), f"{descricao}")
            pdf.drawRightString(
                cmp(238),
                cmp(linha_for - 3),
                f"R$ {valor_despesa}",
            )
            pdf.drawString(cmp(242), cmp(linha_for - 3), f"{obs}")
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
                    cmp(118), cmp(linha - 3), f"Peso Total: {peso_total} kg"
                )
            if item_x["despesas"]:
                total_despesas = valor_ponto_milhar(
                    item_x["t_despesas"]["valor_despesas"], 2
                )
                total_despesas_geral += item_x["t_despesas"]["valor_despesas"]
                pdf.drawRightString(
                    cmp(238),
                    cmp(linha - 3),
                    f"Total Despesas: R$ {total_despesas}",
                )
            linha -= 4
        valor_seguro = valor_ponto_milhar(item_x["recebe"]["t_segu"], 2)
        total_seguro_geral += item_x["recebe"]["t_segu"]
        valor_calculo = valor_ponto_milhar(item_x["recebe_minuta"], 2)
        valor_minuta = valor_ponto_milhar(item_x["valor_minuta"], 2)
        pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
        pdf.drawCentredString(
            cmp(56.5),
            cmp(linha - 3),
            f"Seguro: R$ {valor_seguro}",
        )
        pdf.drawCentredString(
            cmp(148.5),
            cmp(linha - 3),
            f"Calculo R$ {valor_calculo}",
        )
        pdf.drawCentredString(
            cmp(240.5),
            cmp(linha - 3),
            f"Valor R$ {valor_minuta}",
        )
        linha -= 4
    pdf.line(cmp(10), cmp(linha), cmp(287), cmp(linha))
    total_seguro_geral = valor_ponto_milhar(total_seguro_geral, 2)
    total_despesas_geral = valor_ponto_milhar(total_despesas_geral, 2)
    total_peso_geral = valor_ponto_milhar(total_peso_geral, 3)
    pdf.line(cmp(10), cmp(15.5), cmp(287), cmp(15.5))
    pdf.drawString(cmp(12), cmp(12), f"{str(len(minutas)).zfill(2)} MINUTAS")
    txt_seguro = f"TOTAL SEGUROS: R$ {total_seguro_geral}"
    txt_peso = f"PESO TOTAL: {total_peso_geral} kg"
    txt_despesa = f"TOTAL DESPESAS: R$ {total_despesas_geral}"
    pdf.drawRightString(
        cmp(285),
        cmp(12),
        f"{txt_seguro} - {txt_peso} - {txt_despesa}",
    )
    pdf.roundRect(cmp(10), cmp(10), cmp(277), cmp(190), 10)
    return pdf


# TODO Removida do views.py fazer refatoração
def imprime_minuta(request, idmin):
    minuta = Minuta.objects.get(idMinuta=idmin)
    contato = FoneContatoCliente.objects.filter(idCliente=minuta.idCliente)
    veiculo = ""
    if minuta.idVeiculo_id:
        veiculo = Veiculo.objects.get(idVeiculo=minuta.idVeiculo_id)
    colaboradores = MinutaColaboradores.objects.filter(idMinuta=idmin)
    motorista = ""
    ajudante = ""
    if colaboradores:
        minutacolaboradores = MinutaColaboradores.objects.filter(
            idMinuta=idmin, Cargo="MOTORISTA"
        )
        motorista = [item.idPessoal for item in minutacolaboradores]
        motorista = motorista[0]
        ajudante = MinutaColaboradores.objects.filter(
            idMinuta=idmin, Cargo="AJUDANTE"
        )
    response = HttpResponse(content_type="application/pdf")
    buffer = BytesIO()

    # Create the PDF object, using the BytesIO object as its "file."
    pdf = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.

    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)
    pdf.drawImage(url, cmp(12), cmp(265), cmp(40), cmp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawString(
        cmp(56),
        cmp(279),
        "TRANSEFETIVA TRANSPORTE - EIRELLI - ME",
    )
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(
        cmp(53),
        cmp(273),
        "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010",
    )
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(
        cmp(70),
        cmp(268),
        "(11) 2305-0582 - WHATSAPP (11) 94167-0583",
    )
    pdf.drawString(
        cmp(67),
        cmp(263),
        "e-mail: transefetiva@terra.com.br - "
        "operacional.efetiva@terra.com.br",
    )
    pdf.line(cmp(10), cmp(260), cmp(200), cmp(260))
    # ----
    pdf.setFillColor(HexColor("#FFFFFF"))
    pdf.setStrokeColor(HexColor("#FFFFFF"))
    pdf.rect(
        cmp(10),
        cmp(254.1),
        cmp(190),
        cmp(5.6),
        fill=1,
        stroke=1,
    )
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    # ----
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(
        cmp(10),
        cmp(255.8),
        "ORDEM DE SERVIÇO Nº: " + str(minuta.Minuta),
    )
    pdf.drawRightString(
        cmp(200),
        cmp(255.8),
        "DATA: " + minuta.DataMinuta.strftime("%d/%m/%Y"),
    )
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(cmp(10), cmp(249), cmp(95), cmp(5), fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(57.5), cmp(250.3), "DADOS DO CLIENTE")
    # ----
    pdf.setFont("Times-Roman", 8)
    pdf.drawString(
        cmp(11),
        cmp(246),
        "CLIENTE: " + str(minuta.idCliente.Nome),
    )
    endereco = minuta.idCliente.Endereco + " - " + minuta.idCliente.Bairro
    if len(endereco) > 45:
        pdf.drawString(
            cmp(11),
            cmp(242),
            "ENDEREÇO: " + endereco[0:45] + "...",
        )
    else:
        pdf.drawString(
            cmp(11),
            cmp(242),
            "ENDEREÇO: "
            + minuta.idCliente.Endereco
            + " - "
            + minuta.idCliente.Bairro,
        )
    pdf.drawString(
        cmp(27),
        cmp(238),
        minuta.idCliente.Cidade
        + " - "
        + minuta.idCliente.Estado
        + " - "
        + minuta.idCliente.CEP,
    )
    pdf.drawString(
        cmp(11),
        cmp(234),
        "INSCRIÇÃO CNPJ:" + minuta.idCliente.CNPJ,
    )
    pdf.drawString(
        cmp(11),
        cmp(230),
        "INSCRIÇÃO ESTADUAL: " + minuta.idCliente.IE,
    )
    if contato:
        pdf.drawString(
            cmp(11),
            cmp(226),
            "CONTATO: " + contato[0].Contato,
        )
        pdf.drawString(cmp(11), cmp(222), "TELEFONE: " + contato[0].Fone)
    # ----
    pdf.line(cmp(105), cmp(249), cmp(105), cmp(217))
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(
        cmp(105),
        cmp(249),
        cmp(95),
        cmp(5),
        fill=1,
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(
        cmp(152.5), cmp(250.3), "DADOS DO SERVIÇO SOLICITADO"
    )
    # ----
    pdf.setFont("Times-Roman", 8)
    y = 250
    if minuta.idCategoriaVeiculo:
        y -= 4
        pdf.drawString(
            cmp(106),
            cmp(y),
            "VEÍCULO: {}".format(minuta.idCategoriaVeiculo),
        )
        if veiculo:
            pdf.drawRightString(cmp(199), cmp(y), "PLACA: {}".format(veiculo))
    if motorista:
        y -= 4
        pdf.drawString(
            cmp(106),
            cmp(y),
            "MOTORISTA: {}".format(motorista),
        )
    if ajudante:
        if ajudante.count() == 1:
            y -= 4
            pdf.drawString(
                cmp(106),
                cmp(y),
                "AJUDANTE: {}".format(ajudante[0].idPessoal),
            )
        else:
            for x in range(ajudante.count()):
                y -= 4
                if x == 0:
                    pdf.drawString(
                        cmp(106),
                        cmp(y),
                        str(ajudante.count())
                        + " AJUDANTES: "
                        + str(ajudante[x].idPessoal),
                    )
                else:
                    pdf.drawString(
                        cmp(126),
                        cmp(y),
                        str(ajudante[x].idPessoal),
                    )
    if minuta.KMInicial:
        y -= 4
        pdf.drawString(
            cmp(106),
            cmp(y),
            "KM Inicial: " + str(minuta.KMInicial),
        )
    y -= 4
    pdf.drawString(
        cmp(106),
        cmp(y),
        "HORA INICIAL: " + minuta.HoraInicial.strftime("%H:%M"),
    )
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(
        cmp(10),
        cmp(212),
        cmp(95),
        cmp(5),
        fill=1,
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(
        cmp(57.5),
        cmp(213.3),
        "DESCRIÇÃO DO SERVIÇO EXECUTADO",
    )
    # ----
    pdf.line(cmp(105), cmp(212), cmp(105), cmp(172))
    # TODO Excluido custo operacional da minuta 18/09/2020
    # pdf.setFont("Times-Roman", 10)
    # pdf.setFillColor(HexColor("#c1c1c1"))
    # pdf.rect(cmp(105), cmp(212), cmp(95), cmp(5), fill=1)
    # pdf.setFillColor(HexColor("#000000"))
    # pdf.drawCentredString(cmp(152.5), cmp(213.3), 'CUSTO OPERACIONAL')
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(
        cmp(10),
        cmp(167),
        cmp(190),
        cmp(5),
        fill=1,
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(105), cmp(168.3), "DESCRIÇÃO DOS SERVIÇOS")
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(
        cmp(10),
        cmp(87),
        cmp(190),
        cmp(5),
        fill=1,
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(105), cmp(88.3), "LOCAIS DE ENTREGAS E COLETAS")
    pdf.setFont("Times-Roman", 8)
    entregacoleta = ""
    if minuta.Entrega and minuta.Coleta:
        entregacoleta = (
            "ENTREGA: " + minuta.Entrega + " - COLETA: " + minuta.Coleta
        )
    elif minuta.Entrega:
        entregacoleta = "ENTREGA: " + minuta.Entrega
    elif minuta.Coleta:
        entregacoleta = "COLETA: " + minuta.Coleta
    if len(entregacoleta) > 115:
        wrap_entcol = wrap(entregacoleta, width=115)
        y = 87.4
        for linha in range(len(wrap_entcol)):
            if linha == 4:
                break
            y -= 3
            pdf.drawString(cmp(11), cmp(y), wrap_entcol[linha])
    else:
        pdf.drawString(cmp(11), cmp(84.4), entregacoleta)
        # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(
        cmp(10),
        cmp(69),
        cmp(190),
        cmp(5),
        fill=1,
    )
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(105), cmp(70.3), "OBSERVAÇÕES")
    pdf.setFont("Times-Roman", 8)
    observ = minuta.Obs
    if len(observ) > 115:
        wrap_obs = wrap(observ, width=115)
        y = 69.4
        for linha in range(len(wrap_obs)):
            if linha == 4:
                break
            y -= 3
            pdf.drawString(cmp(11), cmp(y), wrap_obs[linha])
    else:
        pdf.drawString(cmp(11), cmp(66.4), observ)
        # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(cmp(10), cmp(51), cmp(190), cmp(5), fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(cmp(105), cmp(52.3), "KILOMETRAGEM")
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(cmp(11), cmp(45.5), "KM INICIAL: ")
    pdf.drawString(cmp(106), cmp(45.5), "KM FINAL: ")
    # ----
    pdf.line(cmp(10), cmp(43), cmp(200), cmp(43))
    # ----
    pdf.roundRect(cmp(12), cmp(12), cmp(101), cmp(19), 3)
    pdf.setFont("Times-Roman", 7)
    textominuta = (
        "A TRANSEFETIVA TRANSPORTE - EIRELI - ME, só se responsabilizará pela mercadoria que o\ncliente"
        " pagar seguro antes da mesma ser carregada. A responsabilidade da mercadoria e demais en-\ncargos"
        " nela contida é unicamente do cliente. É de responsábilidade do cliente MULTAS DE TRAN-\nSITO e"
        " outros encargos que podem ser cobrados, devido as restrições de horário e locais de entrega.\n"
        "Reconheço estar de pleno acordo com o serviço executado e dos dados informados, não tendo"
        " recla-\nmações posteriores à assinatura deste documento."
    )
    textobject = pdf.beginText(cmp(13), cmp(28))
    for line in textominuta.splitlines(False):
        textobject.textLine(line.rstrip())
        pdf.drawText(textobject)
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.line(cmp(118), cmp(15), cmp(194), cmp(15))
    pdf.drawString(
        cmp(118),
        cmp(12),
        "DATA, ASSINATURA E CARIMBO DO CLIENTE",
    )
    # Close the PDF object cleanly.
    pdf.setTitle("Minuta.pdf")
    pdf.showPage()
    pdf.save()
    # Get the value of the BytesIO buffer and write it to the response.
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
