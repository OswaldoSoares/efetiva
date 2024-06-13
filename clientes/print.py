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
from website.facade import cmp
from website.print import header
from transefetiva.settings.settings import STATIC_ROOT


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
    veiculos_cliente(pdf, veiculos, tabela)
    perimetro_cliente(pdf, perimetros)
    capacidades_cliente(pdf, capacidades)
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
    linha -= 3
    pdf.setFont("DejaVuSans", 5)
    asteristico_1 = "Aqui você pode descrever sobre o que você quiser"
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


def veiculos_cliente(pdf, veiculos, tabela):
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
        categoria = veiculo["idCategoriaVeiculo__Categoria"]
        valor_porcentagem = veiculo["PorcentagemCobra"]
        valor_hora = veiculo["HoraCobra"]
        minimo_hora = datetime.time.strftime(veiculo["HoraMinimo"], "%H")
        valor_kilometragem = veiculo["KMCobra"]
        valor_entrega = veiculo["EntregaCobra"]
        valor_entrega_kg = veiculo["EntregaKGCobra"]
        valor_entrega_volume = veiculo["EntregaVolumeCobra"]
        valor_saida = veiculo["SaidaCobra"]
        pdf.drawString(cmp(12), cmp(linha), f"{categoria}")
        pdf.drawRightString(cmp(66), cmp(linha), f"R$ {valor_porcentagem}")
        pdf.drawRightString(
            cmp(88), cmp(linha), f"({minimo_hora}) R$ {valor_hora}"
        )
        pdf.drawRightString(cmp(110), cmp(linha), f"R$ {valor_kilometragem}")
        pdf.drawRightString(cmp(132), cmp(linha), f"R$ {valor_entrega}")
        pdf.drawRightString(cmp(154), cmp(linha), f"R$ {valor_entrega_kg}")
        pdf.drawRightString(cmp(176), cmp(linha), f"R$ {valor_entrega_volume}")
        pdf.drawRightString(cmp(198), cmp(linha), f"R$ {valor_saida}")
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
