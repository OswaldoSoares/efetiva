from io import BytesIO

from django.http import HttpResponse
from django.utils.formats import date_format, number_format
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table
from reportlab.platypus import TableStyle

from despesas.print import cmp, header

COR_CABECALHO = HexColor("#B0C4DE")
COR_ZEBRA = HexColor("#F2F5F9")


def _numero(valor, casas=2):
    if valor is None:
        return "-"
    return number_format(valor, casas, use_l10n=True, force_grouping=True)


def _tabela(linhas, larguras, linha_total=False, numeros_desde=3):
    tabela = Table(linhas, colWidths=[cmp(w) for w in larguras], repeatRows=1)
    estilo = [
        ("FONT", (0, 0), (-1, -1), "Times-Roman", 9),
        ("FONT", (0, 0), (-1, 0), "Times-Bold", 9),
        ("BACKGROUND", (0, 0), (-1, 0), COR_CABECALHO),
        ("ALIGN", (numeros_desde, 0), (-1, -1), "RIGHT"),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, COR_ZEBRA]),
        ("LINEBELOW", (0, 0), (-1, 0), 0.5, colors.black),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if linha_total:
        estilo += [
            ("FONT", (0, -1), (-1, -1), "Times-Bold", 9),
            ("LINEABOVE", (0, -1), (-1, -1), 0.5, colors.black),
            ("BACKGROUND", (0, -1), (-1, -1), colors.white),
        ]
    tabela.setStyle(TableStyle(estilo))
    return tabela


def _pagina(titulo):
    def desenha(pdf, doc):
        pdf.saveState()
        header(pdf)
        pdf.setFont("Times-Bold", 11)
        pdf.drawCentredString(cmp(105), cmp(255.6), titulo)
        pdf.setFont("Times-Roman", 8)
        pdf.drawRightString(cmp(198), cmp(12), f"PÁGINA {doc.page}")
        pdf.restoreState()

    return desenha


def print_abastecimentos(contexto):
    mes = contexto["mes_abastecimento"]
    titulo = f"RELATÓRIO DE ABASTECIMENTOS - {date_format(mes, 'F/Y').upper()}"
    nome_arquivo = f"ABASTECIMENTOS {mes.strftime('%Y-%m')}.pdf"

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        title=nome_arquivo,
        leftMargin=cmp(12),
        rightMargin=cmp(12),
        topMargin=cmp(45),
        bottomMargin=cmp(16),
    )
    subtitulo = ParagraphStyle(
        "subtitulo", fontName="Times-Bold", fontSize=10, spaceAfter=4
    )
    texto = ParagraphStyle("texto", fontName="Times-Roman", fontSize=10)

    elementos = [
        Paragraph(
            f"TOTAL GASTO: R$ {_numero(contexto['total_valor'])} &nbsp;&nbsp; "
            f"LITROS: {_numero(contexto['total_litros'])} &nbsp;&nbsp; "
            f"PREÇO MÉDIO: R$ {_numero(contexto['media_litro'], 3)} &nbsp;&nbsp; "
            f"ABASTECIMENTOS: {len(contexto['abastecimentos'])}",
            texto,
        ),
        Spacer(1, cmp(4)),
        Paragraph("ABASTECIMENTOS DO MÊS", subtitulo),
    ]

    linhas = [["DATA", "PLACA", "COMBUSTÍVEL", "LITROS", "R$/L", "TOTAL"]]
    for item in contexto["abastecimentos"]:
        linhas.append(
            [
                item.DataAbastecimento.strftime("%d/%m/%Y"),
                item.idVeiculo.Placa,
                item.get_TipoCombustivel_display(),
                _numero(item.LitrosAbastecidos),
                _numero(item.ValorCombustivel, 3),
                f"R$ {_numero(item.ValorAbastecido)}",
            ]
        )
    linhas.append(
        [
            "TOTAL",
            "",
            "",
            _numero(contexto["total_litros"]),
            _numero(contexto["media_litro"], 3),
            f"R$ {_numero(contexto['total_valor'])}",
        ]
    )
    elementos.append(_tabela(linhas, [28, 30, 40, 30, 28, 30], True))

    if contexto["resumo_placas"]:
        elementos += [
            Spacer(1, cmp(6)),
            Paragraph("RESUMO POR PLACA", subtitulo),
        ]
        linhas = [
            ["PLACA", "ABAST.", "KM", "LITROS", "KM/L", "R$/L", "TOTAL"]
        ]
        for item in contexto["resumo_placas"]:
            consumo = _numero(item["consumo"]) if item["consumo"] else "-"
            if item["verificar"]:
                consumo += " *"
            linhas.append(
                [
                    item["placa"],
                    item["quantidade"],
                    _numero(item["km"], 0) if item["km"] else "-",
                    _numero(item["litros"]),
                    consumo,
                    _numero(item["media"], 3),
                    f"R$ {_numero(item['valor'])}",
                ]
            )
        elementos.append(
            _tabela(linhas, [26, 18, 28, 28, 24, 28, 34], numeros_desde=1)
        )
        elementos.append(
            Paragraph(
                "KM obtido das minutas do mês. Consumo = km rodados no mês ÷ "
                "litros abastecidos no mês. * Consumo fora do esperado, "
                "conferir.",
                ParagraphStyle(
                    "nota", fontName="Times-Italic", fontSize=8, spaceBefore=4
                ),
            )
        )

    pagina = _pagina(titulo)
    doc.build(elementos, onFirstPage=pagina, onLaterPages=pagina)

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'inline; filename="{nome_arquivo}"'
    response.write(buffer.getvalue())
    buffer.close()
    return response
