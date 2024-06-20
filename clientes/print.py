"""
    Módulo de Impressão
"""
from io import BytesIO
import datetime
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.graphics.shapes import Drawing, Rect, String
from reportlab.graphics.charts.barcharts import VerticalBarChart
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.lineplots import LinePlot, makeMarker
from reportlab.graphics.charts.textlabels import Label
from reportlab.graphics.charts.legends import Legend
from reportlab.graphics import renderPDF
from reportlab.lib import colors
from website.facade import cmp, date_to_boleto
from website.print import header
from transefetiva.settings.settings import STATIC_ROOT
from collections import defaultdict
from time import mktime
from decimal import Decimal


class LinhaClasse:
    """
        Pega e armazena valor da linha. Valor inivial 297
    Attributes:
        _valor: int

    """

    _valor = 297

    @classmethod
    def get_valor(cls):
        """
            Pega o valor armazenado.
        Returns:
            cls._valor: int

        """
        return cls._valor

    @classmethod
    def set_valor(cls, valor_linha):
        """
            Armazena novo valor da linha
        Args:
            linha: int

        """
        cls._valor = valor_linha


def ficha_cadastral(contexto):
    """
        Gera PDF com a ficha do cliente, Cria variáveis através do argumento
        contexto. Registra a font DejaVuSans, para utilização correta de
        simbolos. Faz a chamada das funções que imprime cada parte do PDF.
    Args:
        contexto: dict

    Returns:
        response: django.http.response.HttpResponse

    """
    cliente = contexto["cliente"][0]
    telefones = contexto["fone_cliente"]
    emails = contexto["email_cliente"]
    tabela = contexto["tabela_cliente"][0]
    veiculos = contexto["tabela_veiculo_cliente"]
    perimetros = contexto["tabela_perimetro_cliente"]
    capacidades = contexto["tabela_capacidade_cliente"]
    forma_pgto = contexto["forma_pagamento"]
    minutas_dia = contexto["minutas_dia"]
    notas_dia = contexto["notas_dia"]
    fantasia = cliente["Fantasia"]
    response = HttpResponse(content_type="application/pdf")
    response[
        "Content-Disposition"
    ] = f'filename="FICHA CADASTRAL {fantasia}.pdf"'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    url = f"{STATIC_ROOT}/website/fonts/DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont("DejaVuSans", url))
    header(pdf)
    dados_cliente(pdf, cliente)
    telefones_cliente(pdf, telefones)
    emails_cliente(pdf, emails)
    tabela_cliente(pdf, tabela)
    tipo_pagamento(pdf, tabela, forma_pgto)
    veiculos_cliente(pdf, veiculos)
    perimetro_cliente(pdf, perimetros)
    capacidades_cliente(pdf, capacidades)
    if len(minutas_dia) > 0:
        grafico_minutas_dia(pdf, minutas_dia, notas_dia)
    pdf.setTitle(f"FICHA CADASTRAL {fantasia}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def dados_cliente(pdf, cliente):
    """
        Imrprime os dados do cliente.
        Nome, CNPJ e Endereço
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        cliente: dict

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
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
    pdf.setFont("DejaVuSans", 12)
    pdf.drawCentredString(cmp(105), cmp(255.5), "FICHA CLIENTE")
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
    """
        Imprime os telefones de contato do cliente
        Contato, Tipo e Número
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        telefones: dict

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = 242.8
    pdf.setFont("DejaVuSans", 9)
    pdf.drawCentredString(cmp(105), cmp(linha), "CONTATOS")
    pdf.line(cmp(95), cmp(linha - 0.5), cmp(115), cmp(linha - 0.5))
    linha -= 3
    pdf.setFont("DejaVuSans", 7)
    for telefone in telefones:
        contato = telefone["Contato"]
        tipo = telefone["TipoFone"]
        numero = telefone["Fone"]
        pdf.drawString(cmp(12), cmp(linha), f"{contato} - {tipo} - {numero}")
        linha -= 3
    LinhaClasse().set_valor(linha)
    return pdf


def emails_cliente(pdf, emails):
    """
        Imprime os emails de contato do cliente
        Contato e email
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        emails: dict

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    pdf.setFont("DejaVuSans", 7)
    for email in emails:
        contato = email["Contato"]
        email = email["EMail"]
        pdf.drawString(cmp(12), cmp(linha), f"{contato} - {email}")
        linha -= 3
    pdf.line(cmp(10), cmp(linha + 2), cmp(200), cmp(linha + 2))
    linha -= 3
    LinhaClasse().set_valor(linha)
    return pdf


def tabela_cliente(pdf, tabela):
    """
        Imprime a tabela do cliente.
        Seguro, Taxa de expedição, Ajudante e Hora Extra Ajudante
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        tabela:

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    seguro = f'Seguro: {tabela["Seguro"]}% \u002A'
    taxa = f'Taxa de Expedição/GR: R$ {tabela["TaxaExpedicao"]}'
    ajudante = f'Ajudante: R$ {tabela["AjudanteCobra"]}'
    extra = f'Hora Extra Ajudante: RS {tabela["AjudanteCobraHoraExtra"]}'
    pdf.rect(cmp(11), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(60), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(109), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.rect(cmp(158), cmp(linha), cmp(41), cmp(4), fill=0, stroke=1)
    pdf.setFont("DejaVuSans", 7)
    pdf.drawCentredString(cmp(31.5), cmp(linha + 1), seguro)
    pdf.drawCentredString(cmp(80.5), cmp(linha + 1), taxa)
    pdf.drawCentredString(cmp(129.5), cmp(linha + 1), ajudante)
    pdf.drawCentredString(cmp(178.5), cmp(linha + 1), extra)
    asteristico_1 = "No caso de não haver cobrança de seguro (não haverá cobertura). o risco do transporte corre por conta do cliente. Notas Fiscais é obrigatório constar CNPJ da transportadora para averbação."
    pdf.setFont("DejaVuSans", 5.5)
    linha -= 2
    pdf.drawString(cmp(11), cmp(linha), asteristico_1)
    pdf.line(cmp(10), cmp(linha - 1), cmp(200), cmp(linha - 1))
    linha -= 5
    LinhaClasse().set_valor(linha)
    return pdf


def tipo_pagamento(pdf, tabela, forma_pgto):
    """
        Imprime a forma de pagamento e quais os tipos de cobrança estão
        ativados.
        Porcentagem - Hora - Kilometragem - Entrega - Entrega KG - Entrega
        Volume - Saída
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        tabela: dict
        forma_pgto: str

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    pdf.setFont("DejaVuSans", 9)
    pdf.drawCentredString(
        cmp(105), cmp(linha), f"FORMA DE PAGAMENTO: {forma_pgto}"
    )
    linha -= 2
    pdf.line(cmp(11), cmp(linha), cmp(199), cmp(linha))
    linha -= 3
    phkes = phkes_tabela(tabela)
    pdf.setFont("DejaVuSans", 6)
    pdf.drawCentredString(cmp(24.5), cmp(linha), phkes["porcentagem"])
    pdf.drawCentredString(cmp(51.5), cmp(linha), phkes["hora"])
    pdf.drawCentredString(cmp(78.5), cmp(linha), phkes["kilometragem"])
    pdf.drawCentredString(cmp(105.5), cmp(linha), phkes["entrega"])
    pdf.drawCentredString(cmp(132.5), cmp(linha), phkes["entrega_kg"])
    pdf.drawCentredString(cmp(159.5), cmp(linha), phkes["entrega_volume"])
    pdf.drawCentredString(cmp(186.5), cmp(linha), phkes["saida"])
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
    LinhaClasse().set_valor(linha)
    return pdf


def phkes_tabela(tabela):
    """
        Gera texto com simbolos dependendo se o tipo de cobrança está
        ativo ou não.
    Args:
        tabela: dict

    Returns:
        contexto: dict

    """
    phkesc = tabela["phkescCobra"]
    porcentagem = (
        "PORCENTAGEM \u2714" if int(phkesc[0]) else "PORCENTAGEM \u2718"
    )
    hora = (
        "HORA ATÉ 17:00hs \u2714"
        if int(phkesc[1])
        else "HORA ATÉ 17:00hs \u2718"
    )
    kilometragem = (
        "KILOMETRAGEM \u2714" if int(phkesc[2]) else "KILOMETRAGEM \u2718"
    )
    entrega = "ENTREGA \u2714" if int(phkesc[3]) else "ENTREGA \u2718"
    entrega_kg = "ENTREGA KG \u2714" if int(phkesc[6]) else "ENTREGA KG \u2718"
    entrega_volume = (
        "ENTREGA VOLUME \u2714" if int(phkesc[7]) else "ENTREGA VOLUME \u2718"
    )
    saida = "SAÍDA \u2714" if int(phkesc[4]) else "SAÍDA \u2718"
    contexto = {
        "porcentagem": porcentagem,
        "hora": hora,
        "kilometragem": kilometragem,
        "entrega": entrega,
        "entrega_kg": entrega_kg,
        "entrega_volume": entrega_volume,
        "saida": saida,
    }
    return contexto


def veiculos_cliente(pdf, veiculos):
    """
        Imprime a tabela de veiculos do cliente
        Porcentagem - Hora - Kilometragem - Entrega - Entrega KG - Entrega
        Volume - Saída para cada tipo de veiculo informando os valores.
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        veiculos: list
        tabela: dict

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(11), cmp(linha), cmp(188), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.line(cmp(11), cmp(linha + 4), cmp(199), cmp(linha + 4))
    pdf.setFont("DejaVuSans", 8)
    pdf.drawCentredString(cmp(105), cmp(linha + 1), "TABELA VEICULO")
    pdf.line(cmp(11), cmp(linha), cmp(199), cmp(linha))
    linha -= 3
    linha_superior = linha + 3
    pdf.setFont("DejaVuSans", 6)
    pdf.drawCentredString(cmp(28), cmp(linha + 0.3), "TIPO VEÍCULO")
    pdf.drawCentredString(cmp(56), cmp(linha + 0.3), "PORCENTAGEM")
    pdf.drawCentredString(cmp(78), cmp(linha + 0.3), "(MÍNIMO) HORA")
    pdf.drawCentredString(cmp(100), cmp(linha + 0.3), "KILOMETRAGEM")
    pdf.drawCentredString(cmp(122), cmp(linha + 0.3), "ENTREGA")
    pdf.drawCentredString(cmp(144), cmp(linha + 0.3), "ENTREGA KG")
    pdf.drawCentredString(cmp(166), cmp(linha + 0.3), "ENTREGA VOLUME")
    pdf.drawCentredString(cmp(188), cmp(linha + 0.3), "SAÍDA")
    pdf.line(cmp(11), cmp(linha - 1), cmp(199), cmp(linha - 1))
    linha -= 4
    pdf.setFont("DejaVuSans", 7)
    for veiculo in veiculos:
        pdf.drawString(
            cmp(12), cmp(linha), f"{veiculo['idCategoriaVeiculo__Categoria']}"
        )
        pdf.drawRightString(
            cmp(66), cmp(linha), f"R$ {veiculo['PorcentagemCobra']}"
        )
        minimo_hora = f"{datetime.time.strftime(veiculo['HoraMinimo'], '%H')}"
        pdf.drawRightString(
            cmp(88), cmp(linha), f"{minimo_hora} R$ {veiculo['HoraCobra']}"
        )
        pdf.drawRightString(cmp(110), cmp(linha), f"R$ {veiculo['KMCobra']}")
        pdf.drawRightString(
            cmp(132), cmp(linha), f"R$ {veiculo['EntregaCobra']}"
        )
        pdf.drawRightString(
            cmp(154), cmp(linha), f"R$ {veiculo['EntregaKGCobra']}"
        )
        pdf.drawRightString(
            cmp(176), cmp(linha), f"R$ {veiculo['EntregaVolumeCobra']}"
        )
        pdf.drawRightString(
            cmp(198), cmp(linha), f"R$ {veiculo['SaidaCobra']}"
        )
        linha -= 3
    pdf.line(cmp(11), cmp(linha + 2), cmp(11), cmp(linha_superior + 4))
    pdf.line(cmp(45), cmp(linha + 2), cmp(45), cmp(linha_superior))
    pdf.line(cmp(67), cmp(linha + 2), cmp(67), cmp(linha_superior))
    pdf.line(cmp(89), cmp(linha + 2), cmp(89), cmp(linha_superior))
    pdf.line(cmp(111), cmp(linha + 2), cmp(111), cmp(linha_superior))
    pdf.line(cmp(133), cmp(linha + 2), cmp(133), cmp(linha_superior))
    pdf.line(cmp(155), cmp(linha + 2), cmp(155), cmp(linha_superior))
    pdf.line(cmp(177), cmp(linha + 2), cmp(177), cmp(linha_superior))
    pdf.line(cmp(199), cmp(linha + 2), cmp(199), cmp(linha_superior + 4))
    pdf.line(cmp(11), cmp(linha + 2), cmp(199), cmp(linha + 2))
    linha -= 4
    LinhaClasse().set_valor(linha)
    return pdf


def perimetro_cliente(pdf, perimetros):
    """
        Imprime a tabela de perimetro do cliente
        Perimetro Inicial, Perimetro Final e a porcentagem a ser adicionada.
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        perimetros: list

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    linha_inicial = linha
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(11), cmp(linha), cmp(85), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.line(cmp(11), cmp(linha + 4), cmp(96), cmp(linha + 4))
    pdf.setFont("DejaVuSans", 8)
    pdf.drawCentredString(cmp(54.5), cmp(linha + 1), "TABELA PERIMETRO")
    pdf.line(cmp(11), cmp(linha), cmp(96), cmp(linha))
    linha_superior = linha
    linha -= 3
    pdf.setFont("DejaVuSans", 6)
    pdf.drawCentredString(cmp(31), cmp(linha + 0.3), "KILOMETROS")
    pdf.drawCentredString(cmp(73.5), cmp(linha + 0.3), "PORCENTAGEM")
    pdf.line(cmp(11), cmp(linha - 1), cmp(96), cmp(linha - 1))
    linha -= 4
    pdf.setFont("DejaVuSans", 7)
    if perimetros:
        for perimetro in perimetros:
            inicial = perimetro["PerimetroInicial"]
            final = perimetro["PerimetroFinal"]
            porcentagem = perimetro["PerimetroCobra"]
            pdf.drawCentredString(cmp(21), cmp(linha), f"{inicial}")
            pdf.drawCentredString(cmp(41), cmp(linha), f"{final}")
            pdf.drawCentredString(cmp(73.5), cmp(linha), f"{porcentagem} %")
            linha -= 3
        pdf.line(cmp(31), cmp(linha + 2), cmp(31), cmp(linha_superior - 4))
        pdf.line(cmp(51), cmp(linha + 2), cmp(51), cmp(linha_superior))
    else:
        pdf.drawCentredString(cmp(54.5), cmp(linha), "SEM CADASTRO")
        linha -= 3
        pdf.line(cmp(51), cmp(linha + 6), cmp(51), cmp(linha_superior))
    pdf.line(cmp(11), cmp(linha + 2), cmp(11), cmp(linha_superior + 4))
    pdf.line(cmp(96), cmp(linha + 2), cmp(96), cmp(linha_superior + 4))
    pdf.line(cmp(11), cmp(linha + 2), cmp(96), cmp(linha + 2))
    LinhaClasse().set_valor(linha_inicial)
    return pdf


def capacidades_cliente(pdf, capacidades):
    """
        Imprime a tabela de capacidade(peso) do cliente
        Peso Inicial, Peso Final e o Valor.
    Args:
        pdf: reportlab.pdfgen.canvas.Canvas
        capacidades: list

    Returns:
        pdf: reportlab.pdfgen.canvas.Canvas

    """
    linha = LinhaClasse().get_valor()
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(114), cmp(linha), cmp(85), cmp(4), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.line(cmp(114), cmp(linha + 4), cmp(199), cmp(linha + 4))
    pdf.setFont("DejaVuSans", 8)
    pdf.drawCentredString(
        cmp(156.5), cmp(linha + 1), "TABELA CAPACIDADE (PESO)"
    )
    pdf.line(cmp(114), cmp(linha), cmp(199), cmp(linha))
    linha_superior = linha
    linha -= 3
    pdf.setFont("DejaVuSans", 6)
    pdf.drawCentredString(cmp(134), cmp(linha + 0.3), "QUILOS")
    pdf.drawCentredString(cmp(176.5), cmp(linha + 0.3), "VALOR")
    pdf.line(cmp(114), cmp(linha - 1), cmp(199), cmp(linha - 1))
    linha -= 4
    pdf.setFont("DejaVuSans", 7)
    if capacidades:
        for capacidade in capacidades:
            inicial = capacidade["CapacidadeInicial"]
            final = capacidade["CapacidadeFinal"]
            valor = capacidade["CapacidadeCobra"]
            pdf.drawCentredString(cmp(124), cmp(linha), f"{inicial}")
            pdf.drawCentredString(cmp(144), cmp(linha), f"{final}")
            pdf.drawCentredString(cmp(176.5), cmp(linha), f"R$ {valor}")
            linha -= 3
        pdf.line(cmp(134), cmp(linha + 2), cmp(134), cmp(linha_superior - 4))
        pdf.line(cmp(154), cmp(linha + 2), cmp(154), cmp(linha_superior))
    else:
        pdf.drawCentredString(cmp(156.5), cmp(linha), "SEM CADASTRO")
        linha -= 3
        pdf.line(cmp(154), cmp(linha + 6), cmp(154), cmp(linha_superior))
    pdf.line(cmp(114), cmp(linha + 2), cmp(114), cmp(linha_superior + 4))
    pdf.line(cmp(199), cmp(linha + 2), cmp(199), cmp(linha_superior + 4))
    pdf.line(cmp(114), cmp(linha + 2), cmp(199), cmp(linha + 2))
    linha -= 3
    LinhaClasse().set_valor(linha)
    return pdf


def grafico_minutas_dia(pdf, minutas_dia, notas_dia):
    # Dicionário para armazenar listas de dados por mês
    dados_por_mes = defaultdict(list)
    # Iterar sobre cada item e separar pelo mês/ano
    for item in minutas_dia:
        mes = item["data"].month  # Extrair o mês da data
        ano = item["data"].year  # Extrair o ano da data
        dados_por_mes[f"{mes}/{ano}"].append(item)
    # Converter defaultdict para dict para facilitar o acesso
    dados_por_mes = dict(dados_por_mes)
    # Cria uma lista das chaves do dict
    lista_mes_ano = list(dados_por_mes.keys())

    lista_qtde = [
        item["quantidade"] for item in dados_por_mes[lista_mes_ano[0]]
    ]
    tupla_qtde = tuple(lista_qtde)
    qtde_y = []
    qtde_y.append(tupla_qtde)
    dias_x = [
        datetime.date.strftime(item["data"], "%d")
        for item in dados_por_mes[lista_mes_ano[0]]
    ]

    drawing = Drawing(cmp(18), cmp(12))
    gera_graphics_lineplot(drawing, minutas_dia, notas_dia)
    renderPDF.draw(drawing, pdf, 0, 0)
    return pdf


def gera_graphics_lineplot(drawing, minutas_dia, notas_dia):
    dados = []
    dados_minuta = []
    dados_nota = []
    dates = []
    for item in minutas_dia[-40:]:
        dados_minuta.append((date_to_boleto(item["data"]), item["quantidade"]))
        dates.append(date_to_boleto(item["data"]))
    dados.append(dados_minuta)
    for item in notas_dia:
        dados_nota.append(
            (date_to_boleto(item), notas_dia[item]["quantidade"])
        )
    dados.append(dados_nota)
    print(dados)
    glp = LinePlot()
    glp.x = (cmp(210) - cmp(150)) / 2  # Centralizar o gráfico na página
    glp.y = cmp(20)
    glp.width = cmp(150)
    glp.height = cmp(30)
    glp.data = dados
    glp.strokeColor = colors.black
    # Definir a cor de fundo do gráfico e centralizar junto com o gráfico
    fundo = Rect(
        glp.x, glp.y, glp.width, glp.height, fillColor=colors.lightgrey
    )
    drawing.add(fundo)
    # Configurar os eixos
    glp.xValueAxis.valueMin = min(dates)
    glp.xValueAxis.valueMax = max(dates)
    glp.xValueAxis.labels.angle = 70
    glp.xValueAxis.labels.dx = -7
    glp.xValueAxis.labels.dy = -14
    glp.xValueAxis.labels.fontSize = 6
    # Configurar os rótulos no eixo x
    glp.xValueAxis.labelTextFormat = lambda x: (
        datetime.datetime(1997, 10, 7) + datetime.timedelta(days=x)
    ).strftime("%d/%m")
    glp.xValueAxis.valueSteps = dates
    glp.yValueAxis.valueMin = 0  # Definindo o valor mínimo do eixo y para 0
    glp.yValueAxis.valueMax = max(max(y for x, y in linha) for linha in dados)
    glp.yValueAxis.visibleGrid = 1
    # Adicionar marcadores aos pontos de dados
    glp.lines[0].symbol = makeMarker("FilledCircle")
    glp.lines[1].symbol = makeMarker("FilledCircle")
    glp.lines[1].symbol = makeMarker("FilledCircle")
    drawing.add(glp)
    # Adicionar rótulos com os valores de y em cada junção (x, y)
    deslocamento_x = 2
    deslocamento_y = 2
    for linha in dados:
        for x, y in linha:
            label = String(
                glp.x
                + (x - glp.xValueAxis.valueMin)
                * glp.width
                / (glp.xValueAxis.valueMax - glp.xValueAxis.valueMin)
                + deslocamento_x,
                glp.y
                + (y - glp.yValueAxis.valueMin)
                * glp.height
                / (glp.yValueAxis.valueMax - glp.yValueAxis.valueMin),
                #  + deslocamento_y,
                str(y),
                fontSize=6,
                fillColor=colors.black,
            )
            drawing.add(label)
    # Criar e adicionar o título do gráfico
    titulo = Label()
    titulo.setOrigin(cmp(105), cmp(55))  # Centralizar o título no desenho
    titulo.setText("Estatísticas últimos 40 dias.")
    titulo.fontName = "DejaVuSans"
    titulo.fontSize = 10
    titulo.fillColor = colors.black
    titulo.textAnchor = "middle"  # Ancorar o texto no meio
    drawing.add(titulo)
    # Adicionar a legenda
    legenda = Legend()
    legenda.x = 330
    legenda.y = 150
    legenda.dx = 8
    legenda.dy = 8
    legenda.boxAnchor = "nw"
    legenda.columnMaximum = 10
    legenda.fontName = "DejaVuSans"
    legenda.fontSize = 6
    legenda.strokeWidth = 1
    legenda.strokeColor = colors.black
    legenda.deltax = 75
    legenda.deltay = 10
    legenda.autoXPadding = 5
    legenda.yGap = 0
    legenda.dxTextSpace = 5
    legenda.alignment = "right"
    legenda.dividerLines = 1 | 2 | 4
    legenda.dividerOffsY = 4.5
    legenda.subCols.rpad = 30
    # Definir os nomes das legendas e suas cores
    color_linha_0 = glp.lines[0].strokeColor
    color_linha_1 = glp.lines[1].strokeColor
    legenda.colorNamePairs = [
        (color_linha_0, "Veículos"),
        (color_linha_1, "Notas"),
    ]
    drawing.add(legenda)
    return drawing


def teste():
    drawing = Drawing(cmp(18), cmp(12))
    #  Criar o gráfico de barras
    bc = VerticalBarChart()
    bc.x = (cmp(210) - cmp(150)) / 2
    bc.y = cmp(55)
    bc.height = cmp(30)
    bc.width = cmp(150)
    bc.data = qtde_y
    bc.strokeColor = colors.black
    #  Configurar os eixos
    bc.valueAxis.valueMin = 0
    bc.categoryAxis.labels.boxAnchor = "ne"
    bc.categoryAxis.labels.dx = 4
    bc.categoryAxis.labels.dy = -2
    bc.categoryAxis.labels.angle = 0
    bc.categoryAxis.categoryNames = dias_x

    drawing.add(bc)
    # Cria Título
    titulo2 = Label()
    titulo2.setOrigin(cmp(105), cmp(90))  # Define a posição do título
    titulo2.setText(f"Estatistica do mês: {lista_mes_ano[2]}")
    titulo2.fontName = "DejaVuSans"
    titulo2.fontSize = 10
    titulo2.fillColor = colors.black
    drawing.add(titulo2)

    lista_qtde = [
        item["quantidade"] for item in dados_por_mes[lista_mes_ano[1]]
    ]
    tupla_qtde = tuple(lista_qtde)
    qtde_y = []
    qtde_y.append(tupla_qtde)
    dias_x = [
        datetime.date.strftime(item["data"], "%d")
        for item in dados_por_mes[lista_mes_ano[1]]
    ]

    #  drawing = Drawing(cmp(18), cmp(12))
    #  Criar o gráfico de barras
    bc2 = HorizontalLineChart()
    bc2.x = (cmp(210) - cmp(150)) / 2
    bc2.y = cmp(10)
    bc2.height = cmp(30)
    bc2.width = cmp(150)
    bc2.data = qtde_y
    bc2.strokeColor = colors.black
    #  Configurar os eixos
    bc2.valueAxis.valueMin = 0
    bc2.categoryAxis.labels.boxAnchor = "ne"
    bc2.categoryAxis.labels.dx = 4
    bc2.categoryAxis.labels.dy = -2
    bc2.categoryAxis.labels.angle = 0
    bc2.categoryAxis.categoryNames = dias_x

    drawing.add(bc2)
    # Cria Título
    titulo = Label()
    titulo.setOrigin(cmp(105), cmp(45))  # Define a posição do título
    titulo.setText(f"Estatistica do mês: {lista_mes_ano[1]}")
    titulo.fontName = "DejaVuSans"
    titulo.fontSize = 10
    titulo.fillColor = colors.black
    drawing.add(titulo)
