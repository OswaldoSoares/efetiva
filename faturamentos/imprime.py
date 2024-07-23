from decimal import Decimal
from datetime import timedelta
from io import BytesIO

from clientes.models import Cliente, TabelaPerimetro
from django.core.files.base import ContentFile
from django.http import HttpResponse
from minutas.facade import MinutaSelecionada
from minutas.models import (
    Minuta,
    MinutaColaboradores,
    MinutaItens,
    MinutaNotas,
)
from minutas.views import convertemp
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from romaneios.models import RomaneioNotas
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import nome_curto, valor_ponto_milhar
from website.models import FileUpload

from .models import Fatura


def format_timedelta(td):
    total_seconds = int(td.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{hours:02}:{minutes:02}HS"


def textos_tipo_recebe():
    """
        Cria uma lista com os tipo_recebe(MinutaItens Models Field) e gera
        os textos em forma f-string que serão mostrados na fatura com seu
        respectivos valores após inseridos
    Returns:
        textos: list dict

    """
    textos = [
        {
            "TAXA DE EXPEDIÇÃO": {
                "texto": lambda item: "&#x2713 TAXA DE EXPEDICAO &#x27BA "
                f"R$ {item[0]}",
                "item": ["valor"],
            },
        },
        {
            "SEGURO": {
                "texto": lambda item: f"&#x2713 SEGURO {item[0]}% DO VALOR "
                f"DA(S) NOTA(S) R$ {item[1]} &#x27BA R$ {item[2]}",
                "item": ["porcento", "base", "valor"],
            }
        },
        {
            "PORCENTAGEM DA NOTA": {
                "texto": lambda item: f"&#x2713 {item[0]}% DO VALOR "
                f"DA(S) NOTA(S) R$ {item[1]} &#x27BA R$ {item[2]}",
                "item": ["porcento", "base", "valor"],
            }
        },
        {
            "HORAS": {
                "texto": lambda item: f"&#x2713 {item[0]} HORAS "
                f"MINIMAS &#x27BA R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "HORAS EXCEDENTE": {
                "texto": lambda item: f"&#x2713 {item[0]} HORAS EXCEDENTE "
                f"&#x27BA R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "KILOMETRAGEM": {
                "texto": lambda item: f"&#x2713 {item[0]} KMS &#x27BA "
                f"R$ {item[1]}",
                "item": ["quantidade", "valor"],
            }
        },
        {
            "KILOMETRAGEM HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "ENTREGAS": {
                "texto": lambda item: f"&#x2713 {item[0]} ENTREGA(S) "
                f"&#x27BA R$ {item[1]}",
                "item": ["quantidade", "valor"],
            }
        },
        {
            "ENTREGAS HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "ENTREGAS KG": {
                "texto": lambda item: f"&#x2713 {item[0]} KGS "
                f"&#x27BA R$ {item[1]}",
                "item": ["peso", "valor"],
            }
        },
        {
            "ENTREGAS KG HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "ENTREGAS VOLUME": {
                "texto": lambda item: f"&#x2713 {item[0]} "
                f"VOLUME &#x27BA R$ {item[1]}",
                "item": ["quantidade", "valor"],
            }
        },
        {
            "ENTREGAS VOLUME HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "SAIDA": {
                "texto": lambda item: f"&#x2713 SAÍDA &#x27BA "
                f"R$ {item[0]}",
                "item": ["valor"],
            }
        },
        {
            "SAIDA NORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "CAPACIDADE PESO": {
                "texto": lambda item: f"&#x2713 CAPACIDADE "
                f"PESO &#x27BA R$ {item[0]}",
                "item": ["valor"],
            }
        },
        {
            "CAPACIDADE PESO HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "PERIMETRO": {
                "texto": lambda item: f" &#x2713 PERIMETRO "
                f"{item[0]}% (DE {item[1]} KMS ATÉ {item[2]} "
                f"KMS) &#x27BA R$ {item[3]}",
                "item": ["porcento", "inicial", "final", "valor"],
            }
        },
        {
            "PERIMETRO HORA EXTRA": {
                "texto": lambda item: f"- EXTRA {item[0]} &#x27BA "
                f"R$ {item[1]}",
                "item": ["tempo", "valor"],
            }
        },
        {
            "PERNOITE": {
                "texto": lambda item: f"&#x2713 PERNOITE "
                f"{item[0]}% &#x27BA R$ {item[1]}",
                "item": ["porcento", "valor"],
            }
        },
        {
            "AJUDANTE": {
                "texto": lambda item: f"&#x2713 {item[0]} "
                f"AJUDANTE(S) &#x27BA R$ {item[1]}",
                "item": ["quantidade", "valor"],
            }
        },
        {
            "AJUDANTE HORA EXTRA": {
                "texto": lambda item: f"&#x2713 {item[0]} "
                f"AJUDANTE(S) &#x27BA R$ {item[1]} - EXTRA &#x27BA "
                f"R$ {item[2]}",
                "item": ["quantidade", "valor", "extra"],
            }
        },
    ]
    return textos


def itens_cobrado(minuta):
    textos = textos_tipo_recebe()
    textos_dict = {
        descricao: info for tipo in textos for descricao, info in tipo.items()
    }
    itens = MinutaItens.objects.filter(
        idMinuta_id=minuta["idminuta"], RecebePaga="R"
    )
    cobrados = []
    for item in itens:
        descricao = item.Descricao
        valores = {
            "base": item.ValorBase,
            "peso": item.Peso,
            "porcento": item.Porcento,
            "quantidade": item.Quantidade,
            "tempo": format_timedelta(item.Tempo),
            "valor": item.Valor,
        }
        if descricao in textos_dict:
            texto_info = textos_dict[descricao]
            if descricao == "AJUDANTE":
                if minuta["recebe"]["t_exce"] > 0:
                    descricao = "AJUDANTE HORA EXTRA"
                    texto_info = textos_dict[descricao]
                    valor_ajudantes = (
                        Decimal(minuta["tabela"][0]["AjudanteCobra"])
                        * item.Quantidade
                    )
                    valores = {
                        "quantidade": item.Quantidade,
                        "valor": valor_ajudantes,
                        "extra": item.Valor - valor_ajudantes,
                    }
            texto_formatado = texto_info["texto"](
                [valores.get(campo, 0) for campo in texto_info["item"]]
            )
            cobrados.append(texto_formatado)
    for item in itens:
        if item.TipoItens == "DESPESA":
            cobrados.append(
                f"&#x2713 {item.Descricao} &#x27BA R$ {item.Valor} "
                f"- {item.Obs}"
            )
    return cobrados


def paragrafo_itens_cobrado(pdf, linha, estilo, minuta):
    cobrados = itens_cobrado(minuta)
    paragrafo = " ".join(cobrados)
    para = Paragraph(paragrafo, style=estilo)
    para.wrapOn(pdf, convertemp(186), convertemp(297))
    linha -= para.height * 0.352777
    para.drawOn(pdf, convertemp(12), convertemp(linha))
    linha -= 1
    pdf.line(
        convertemp(10), convertemp(linha), convertemp(200), convertemp(linha)
    )
    return pdf, linha


def decricao_servico(
    dict_servicos, perimetro_inicial, perimetro_final, s_minuta
):
    servicos = ""
    texto_taxa = ""
    texto_seguro = ""
    texto_ajudante = ""
    texto_desconto = ""
    for itens in dict_servicos:
        if itens["TipoItens"] == "RECEBE":
            if itens["Descricao"] == "TAXA DE EXPEDIÇÃO":
                texto_taxa = "&#x2713 TAXA DE EXPEDICAO &#x27BA R$ {} ".format(
                    itens["Valor"]
                )
            if itens["Descricao"] == "SEGURO":
                texto_seguro = f"&#x2713 SEGURO {itens['Porcento']:,.3f}% DO VALOR DA(S) NOTA(S) R$ {itens['ValorBase']} &#x27BA R$ {itens['Valor']}"
            if itens["Descricao"] == "PORCENTAGEM DA NOTA":
                servicos = "{} &#x2713 {}% DO VALOR DA(S) NOTA(S) R$ {} &#x27BA R$ {} ".format(
                    servicos,
                    itens["Porcento"],
                    itens["ValorBase"],
                    itens["Valor"],
                )
            if itens["Descricao"] == "HORAS":
                servicos = "{} &#x2713 {} HORAS MINIMAS &#x27BA R$ {} ".format(
                    servicos, itens["Tempo"], itens["Valor"]
                )
            if itens["Descricao"] == "HORAS EXCEDENTE":
                servicos = (
                    "{} &#x2713 {} HORAS EXCEDENTE &#x27BA R$ {} ".format(
                        servicos, itens["Tempo"], itens["Valor"]
                    )
                )
            if itens["Descricao"] == "KILOMETRAGEM":
                servicos = "{} &#x2713 {} KMS &#x27BA R$ {} ".format(
                    servicos, itens["Quantidade"], itens["Valor"]
                )
            if itens["Descricao"] == "ENTREGAS":
                servicos = "{} &#x2713 {} ENTREGA(S) &#x27BA R$ {} ".format(
                    servicos, itens["Quantidade"], itens["Valor"]
                )
            if itens["Descricao"] == "ENTREGAS KG":
                servicos = "{} &#x2713 {} KGS &#x27BA R$ {} ".format(
                    servicos, itens["Peso"], itens["Valor"]
                )
            if itens["Descricao"] == "ENTREGAS VOLUME":
                servicos = "{} &#x2713 {} VOLUME &#x27BA R$ {} ".format(
                    servicos, itens["Quantidade"], itens["Valor"]
                )
            if itens["Descricao"] == "SAIDA":
                servicos = "{} &#x2713 SAÍDA &#x27BA R$ {} ".format(
                    servicos, itens["Valor"]
                )
            if itens["Descricao"] == "CAPACIDADE PESO":
                servicos = "{} &#x2713 CAPACIDADE VEÍCULO (KGS) &#x27BA R$ {} ".format(
                    servicos, itens["Valor"]
                )
            if itens["Descricao"] == "PERIMETRO":
                servicos = "{} &#x2713 SUBTOTAL {} ".format(
                    servicos, itens["ValorBase"]
                )
                servicos = "{} &#x2713 PERIMETRO {}% (DE {} KMS ATÉ {} KMS) &#x27BA R$ {} ".format(
                    servicos,
                    itens["Porcento"],
                    perimetro_inicial,
                    perimetro_final,
                    itens["Valor"],
                )
            if itens["Descricao"] == "PERNOITE":
                servicos = "{} &#x2713 PERNOITE {}% &#x27BA R$ {} ".format(
                    servicos, itens["Porcento"], itens["Valor"]
                )
            if itens["Descricao"] == "AJUDANTE":
                # TODO Melhorar este código
                if s_minuta["recebe"]["t_exce"] > 0:
                    ajudantes = itens["Quantidade"]
                    total_ajudantes = Decimal(s_minuta["recebe"]["t_ajud"])
                    valor_ajudantes = (
                        Decimal(s_minuta["tabela"][0]["AjudanteCobra"])
                        * ajudantes
                    )
                    extra_ajudantes = total_ajudantes - valor_ajudantes
                    texto_ajudante = "&#x2713 {} AJUDANTE(S) &#x27BA R$ {} EXTRA R$ {}".format(
                        itens["Quantidade"], valor_ajudantes, extra_ajudantes
                    )
                else:
                    texto_ajudante = (
                        "&#x2713 {} AJUDANTE(S) &#x27BA R$ {} ".format(
                            itens["Quantidade"], itens["Valor"]
                        )
                    )
            if itens["Descricao"] == "DESCONTO":
                texto_desconto = "&#x2713 DESCONTO &#x27BA R$ {}".format(
                    itens["Valor"]
                )
    servicos = "{} {} {} {} {}".format(
        servicos, texto_taxa, texto_seguro, texto_ajudante, texto_desconto
    )
    for itens in dict_servicos:
        if itens["TipoItens"] == "DESPESA":
            servicos = "{} &#x2713 {} &#x27BA R$ {} - {},".format(
                servicos, itens["Descricao"], itens["Valor"], itens["Obs"]
            )
    return servicos


def imprime_cabecalho(pdf, fatura_selecionada):
    fatura_numero = fatura_selecionada[0].Fatura
    fatura_vemcimento = fatura_selecionada[0].VencimentoFatura.strftime(
        "%d/%m/%Y"
    )
    fatura_valor = "R$ {}".format(fatura_selecionada[0].ValorFatura).replace(
        ".", ","
    )
    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    pdf.roundRect(
        convertemp(10), convertemp(10), convertemp(190), convertemp(277), 10
    )
    pdf.drawImage(
        url, convertemp(12), convertemp(265), convertemp(40), convertemp(20)
    )
    # pdf.drawImage('efetiva/site/public/static/website/img/transportadora.jpg', convertemp(12), convertemp(265),
    #               convertemp(40), convertemp(20))
    tamanho_font = 18
    pdf.setFont("Times-Bold", tamanho_font)
    pdf.drawString(
        convertemp(54),
        convertemp(279),
        "TRANSEFETIVA TRANSPORTE - EIRELLI - ME",
    )
    tamanho_font = 12
    pdf.setFont("Times-Roman", tamanho_font)
    pdf.drawString(
        convertemp(53),
        convertemp(273),
        "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010",
    )
    pdf.drawString(
        convertemp(68),
        convertemp(268),
        "(11) 2305-0582 - WHATSAPP (11) 94167-0583",
    )
    pdf.drawString(
        convertemp(65),
        convertemp(263),
        "e-mail: transefetiva@terra.com.br - operacional.efetiva@terra.com.br",
    )
    pdf.line(convertemp(10), convertemp(260), convertemp(200), convertemp(260))
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(
        convertemp(10),
        convertemp(254.1),
        convertemp(190),
        convertemp(5.6),
        fill=1,
        stroke=1,
    )
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawString(
        convertemp(12),
        convertemp(255.8),
        "FATURA Nº: {}".format(fatura_numero),
    )
    pdf.drawCentredString(
        convertemp(105),
        convertemp(255.8),
        "VENCIMENTO: {}".format(fatura_vemcimento),
    )
    pdf.drawRightString(
        convertemp(198), convertemp(255.8), "VALOR: {}".format(fatura_valor)
    )
    pdf.line(
        convertemp(10), convertemp(254.1), convertemp(200), convertemp(254.1)
    )


def imprime_fatura_pdf(fatura):
    fatura_selecionada = Fatura.objects.filter(idFatura=fatura)
    descricao_arquivo = (
        f"Fatura_{str(fatura_selecionada[0].Fatura).zfill(6)}_fatura.pdf"
    )
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    if not arquivo:
        obj = FileUpload()
        obj.DescricaoUpload = descricao_arquivo
        obj.save()
        arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    minutas = Minuta.objects.filter(idFatura=fatura).order_by("DataMinuta")
    tabelaperimetro = TabelaPerimetro.objects.filter(
        idCliente=minutas[0].idCliente_id
    )
    perimetro_inicial = 0
    perimetro_final = 0
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f"filename={descricao_arquivo}"
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    # Start writing the PDF here - Aqui começa a escrita do PDF
    styles_claro = ParagraphStyle(
        "claro",
        fontName="Times-Roman",
        fontSize=8,
        leading=9,
        alignment=TA_JUSTIFY,
    )
    styles_escuro = ParagraphStyle(
        "escuro",
        fontName="Times-Roman",
        fontSize=8,
        leading=9,
        alignment=TA_JUSTIFY,
        backColor="#EEE9E9",
    )
    cliente = Cliente.objects.filter(idCliente=minutas[0].idCliente_id)
    cliente_nome = cliente[0].Nome
    cliente_endereco = "{} - {} - {} - {} - {}".format(
        cliente[0].Endereco,
        cliente[0].Bairro,
        cliente[0].CEP,
        cliente[0].Cidade,
        cliente[0].Estado,
    )
    cliente_docs = None
    if cliente[0].CNPJ and cliente[0].IE:
        cliente_docs = "CNPJ {} - IE {}".format(cliente[0].CNPJ, cliente[0].IE)
    elif cliente[0].CNPJ:
        cliente_docs = "CNPJ {}".format(cliente[0].CNPJ)
    elif cliente[0].IE:
        cliente_docs = "IR {}".format(cliente[0].IE)
    imprime_cabecalho(pdf, fatura_selecionada)
    linha = 250.8
    tamanho_font = 10
    pdf.setFont("Times-Roman", tamanho_font)
    pdf.setFillColor(HexColor("#483D8B"))
    pdf.drawString(
        convertemp(12), convertemp(linha), "{}".format(cliente_nome)
    )
    if cliente_docs:
        pdf.drawRightString(
            convertemp(198), convertemp(linha), "{}".format(cliente_docs)
        )
    linha = 247.3
    pdf.drawString(
        convertemp(12), convertemp(linha), "{}".format(cliente_endereco)
    )
    pdf.setFillColor(HexColor("#000000"))
    linha = 246.3
    pdf.line(
        convertemp(10), convertemp(linha), convertemp(200), convertemp(linha)
    )
    linha = 242.8
    # Inicio da impressão de cada minuta
    for index, itens in enumerate(minutas):
        s_minuta = MinutaSelecionada(minutas[index].idMinuta).__dict__
        romaneios = s_minuta["romaneio"]
        romaneios_pesos = s_minuta["romaneio_pesos"]
        lista_romaneios = " - ".join(
            f"{str(e['romaneio'])}  {str(e['peso'])} Kg"
            for e in romaneios_pesos
        )
        inicialkm = minutas[index].KMInicial
        finalkm = minutas[index].KMFinal
        totalkm = finalkm - inicialkm
        for x in tabelaperimetro:
            if totalkm >= x.PerimetroInicial:
                if totalkm <= x.PerimetroFinal:
                    perimetro_inicial = x.PerimetroInicial
                    perimetro_final = x.PerimetroFinal
                    break
        minuta_colaboradores = MinutaColaboradores.objects.filter(
            idMinuta=minutas[index].idMinuta, Cargo="MOTORISTA"
        )
        minuta_numero = minutas[index].Minuta
        minuta_data = minutas[index].DataMinuta.strftime("%d/%m/%Y")
        minuta_hora_inicial = minutas[index].HoraInicial.strftime("%H:%M")
        minuta_hora_final = minutas[index].HoraFinal.strftime("%H:%M")
        minuta_motorista = None
        if minuta_colaboradores:
            minuta_motorista = nome_curto(
                minuta_colaboradores[0].idPessoal.Nome
            )
        minuta_veiculo = minutas[index].idCategoriaVeiculo
        minuta_placa = None
        if minutas[index].idVeiculo:
            minuta_placa = minutas[index].idVeiculo
        minuta_valor = minutas[index].Valor
        pdf.setFillColor(HexColor("#FAF3CF"))
        pdf.setStrokeColor(HexColor("#FAF3CF"))
        pdf.rect(
            convertemp(12),
            convertemp(linha - 3),
            convertemp(186),
            convertemp(5.6),
            fill=1,
            stroke=1,
        )
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        tamanho_font = 8
        pdf.setFont("Times-Roman", tamanho_font)
        pdf.setFillColor(HexColor("#FF0000"))
        # Draw Data e Minutas - Romaneio
        pdf.drawString(
            convertemp(12), convertemp(linha), "DATA: {}".format(minuta_data)
        )
        if romaneios:
            pdf.drawRightString(
                convertemp(198), convertemp(linha), f"MINUTA: {minuta_numero}"
            )
        else:
            pdf.drawCentredString(
                convertemp(105),
                convertemp(linha),
                "MINUTA: {}".format(minuta_numero),
            )
        linha -= 3
        pdf.setFillColor(HexColor("#0000FF"))
        tamanho_font = 8
        pdf.setFont("Times-Roman", tamanho_font)
        # Draw Motorista Veiculo Placa - Horario - Valor Minuta
        if minuta_motorista:
            if minuta_placa:
                pdf.drawString(
                    convertemp(12),
                    convertemp(linha),
                    f"{minuta_motorista} - {minuta_veiculo} - {minuta_placa}",
                )
            else:
                pdf.drawString(
                    convertemp(12),
                    convertemp(linha),
                    f"{minuta_motorista}",
                )
        pdf.drawCentredString(
            convertemp(105),
            convertemp(linha),
            "HORARIO: {} HS ATÉ AS {} HS".format(
                minuta_hora_inicial, minuta_hora_final
            ),
        )
        pdf.setFont("Times-Roman", 8)
        pdf.drawRightString(
            convertemp(198),
            convertemp(linha),
            "VALOR: R$ {:.2f}".format(minuta_valor).replace(".", ","),
        )
        pdf.setFillColor(HexColor("#000000"))
        linha -= 1
        pdf.line(
            convertemp(12),
            convertemp(linha),
            convertemp(198),
            convertemp(linha),
        )
        coleta_entrega = None
        if minutas[index].Coleta and minutas[index].Entrega:
            coleta_entrega = "COLETA: {} - ENTREGA: {}".format(
                minutas[index].Coleta, minutas[index].Entrega
            )
        elif minutas[index].Coleta:
            coleta_entrega = "COLETA: {}".format(minutas[index].Coleta)
        elif minutas[index].Entrega:
            coleta_entrega = "ENTREGA: {}".format(minutas[index].Entrega)
        # Draw Coleta e Entrega
        if coleta_entrega:
            linha -= 1
            para = Paragraph(coleta_entrega, style=styles_claro)
            para.wrapOn(pdf, convertemp(186), convertemp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, convertemp(12), convertemp(linha))
        observacao = None
        if minutas[index].Obs:
            observacao = "OBSERVAÇÕES: {}".format(minutas[index].Obs)
        # Draw Observações
        if observacao:
            linha -= 1
            para = Paragraph(observacao, style=styles_claro)
            para.wrapOn(pdf, convertemp(186), convertemp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, convertemp(12), convertemp(linha))
        if romaneios:
            notas_romaneio = RomaneioNotas.objects.filter(
                idRomaneio__in=romaneios
            )
            soma_peso = sum([i.idNotasClientes.Peso for i in notas_romaneio])
            soma_valor = sum([i.idNotasClientes.Valor for i in notas_romaneio])
            if soma_valor > 0:
                custo = minuta_valor / soma_valor * 100
            else:
                custo = None
            # f"{i.idNotasClientes.Endereco} - {i.idNotasClientes.Bairro}"
            enderecos = []
            for i in notas_romaneio:
                if i.idNotasClientes.LocalColeta == "DESTINATÁRIO":
                    enderecos.append(
                        f"{i.idNotasClientes.Endereco_emi} - {i.idNotasClientes.Bairro_emi}"
                    )
                else:
                    enderecos.append(
                        f"{i.idNotasClientes.Endereco} - {i.idNotasClientes.Bairro}"
                    )
            entregas = list(set(enderecos))
            romaneios_separados = list(
                set([x.idRomaneio.Romaneio for x in notas_romaneio])
            )
            romaneios_separados.sort()
            notas_dados = [
                {
                    "Romaneio": x.idRomaneio.Romaneio,
                    "Nota": x.idNotasClientes.NumeroNota,
                    "ValorNota": x.idNotasClientes.Valor,
                    "Peso": x.idNotasClientes.Peso,
                    "Volume": x.idNotasClientes.Volume,
                    "Bairro": x.idNotasClientes.Bairro,
                    "CEP": x.idNotasClientes.CEP,
                    "Cidade": x.idNotasClientes.Cidade,
                    "Estado": x.idNotasClientes.Estado,
                    "Nome": x.idNotasClientes.Destinatario,
                    "Endereco": x.idNotasClientes.Endereco,
                    "Bairro_emi": x.idNotasClientes.Bairro_emi,
                    "CEP_emi": x.idNotasClientes.CEP_emi,
                    "Cidade_emi": x.idNotasClientes.Cidade_emi,
                    "Estado_emi": x.idNotasClientes.Estado_emi,
                    "Emitente": x.idNotasClientes.Emitente,
                    "Endereco_emi": x.idNotasClientes.Endereco_emi,
                    "LocalColeta": x.idNotasClientes.LocalColeta,
                    "StatusNota": x.idNotasClientes.StatusNota,
                    "Contato": x.idNotasClientes.Contato,
                }
                for x in notas_romaneio
            ]
            idminuta = minutas[index].idMinuta
            notas = "NOTA(S): "
            # Draw Notas Miinuta
            if notas_dados:
                for romaneio in romaneios_pesos:
                    pdf.setFillColor(HexColor("#FAF3CF"))
                    pdf.setStrokeColor(HexColor("#FAF3CF"))
                    pdf.rect(
                        convertemp(12),
                        convertemp(linha - 3),
                        convertemp(186),
                        convertemp(2),
                        fill=1,
                        stroke=1,
                    )
                    pdf.setStrokeColor(HexColor("#000000"))
                    pdf.setFillColor(HexColor("#FF0000"))
                    linha -= 3
                    pdf.drawCentredString(
                        convertemp(105),
                        convertemp(linha),
                        f"ROMANEIO: {romaneio['romaneio']} - PESO: {romaneio['peso']}",
                    )
                    pdf.setFillColor(HexColor("#000000"))
                    filtro = [
                        item
                        for item in notas_dados
                        if item["Romaneio"] == romaneio["romaneio"]
                    ]
                    linha, pdf = print_notas_da_minuta_unidade(
                        filtro,
                        idminuta,
                        notas,
                        pdf,
                        styles_claro,
                        linha,
                        fatura_selecionada,
                    )
                    linha -= 1
                    pdf.line(
                        convertemp(12),
                        convertemp(linha),
                        convertemp(198),
                        convertemp(linha),
                    )
            linha -= 3
            #  pdf.line(
            #  convertemp(12),
            #  convertemp(linha),
            #  convertemp(198),
            #  convertemp(linha),
            #  )
            #  linha -= 3
            pdf.setFillColor(HexColor("#FF0000"))
            pdf.drawCentredString(
                convertemp(105),
                convertemp(linha),
                f"{len(entregas):0>2} ENTREGAS - PESO: {valor_ponto_milhar(soma_peso, 3)} - VALOR: {valor_ponto_milhar(soma_valor, 2)}",
            )
            if soma_valor > 0:
                pdf.drawRightString(
                    convertemp(198), convertemp(linha), f"{custo:,.3f}%"
                )
            pdf.setFillColor(HexColor("#000000"))
            linha -= 1
            pdf.line(
                convertemp(12),
                convertemp(linha),
                convertemp(198),
                convertemp(linha),
            )
        else:
            notas_dados = (
                MinutaNotas.objects.values(
                    "Nota",
                    "ValorNota",
                    "Peso",
                    "Volume",
                    "Bairro",
                    "Cidade",
                    "Nome",
                    "NotaGuia",
                )
                .filter(idMinuta=minutas[index].idMinuta, NotaGuia="0")
                .exclude(Nota="PERIMETRO")
            )
            idminuta = minutas[index].idMinuta
            notas = "NOTA(S): "
            if notas_dados:
                linha, pdf = print_notas_da_minuta_paragrafo(
                    notas_dados,
                    idminuta,
                    notas,
                    pdf,
                    styles_claro,
                    linha,
                    fatura_selecionada,
                )
        # TODO Código abaixo removido a pedido de Mauricio em 11/10/2022 para não mostrar mais
        #      Bairro e Cidade
        # notas_perimetro = (
        #     MinutaNotas.objects.values("Cidade")
        #     .filter(idMinuta=minutas[index].idMinuta)
        #     .exclude(Cidade="SÃO PAULO")
        # )
        # cidades = "CIDADE(S):"
        # if notas_perimetro:
        #     for itensperimetro in notas_perimetro:
        #         cidades = "{} &#x2713 {} ".format(cidades, itensperimetro["Cidade"])
        #     para = Paragraph(cidades, style=styles_claro)
        #     para.wrapOn(pdf, convertemp(186), convertemp(297))
        #     linha -= para.height * 0.352777
        #     para.drawOn(pdf, convertemp(12), convertemp(linha))
        # notas_bairro = (
        #     MinutaNotas.objects.values("Bairro")
        #     .filter(idMinuta=minutas[index].idMinuta)
        #     .exclude(Bairro__isnull=True)
        #     .exclude(Bairro__exact="")
        # )
        # bairros = "BAIRRO(S):"
        # if notas_bairro:
        #     for itensbairro in notas_bairro:
        #         bairros = "{} &#x2713 {} ".format(bairros, itensbairro["Bairro"])
        #     para = Paragraph(bairros, style=styles_claro)
        #     para.wrapOn(pdf, convertemp(186), convertemp(297))
        #     linha -= para.height * 0.352777
        #     para.drawOn(pdf, convertemp(12), convertemp(linha))
        if totalkm > 0:
            linha -= 3
            tamanho_font = 8
            pdf.setFont("Times-Roman", tamanho_font)
            pdf.drawString(
                convertemp(12),
                convertemp(linha),
                "TOTAL {} KMS".format(totalkm),
            )
            linha -= 1
            pdf.line(
                convertemp(12),
                convertemp(linha),
                convertemp(198),
                convertemp(linha),
            )
        if minutas[index].Comentarios:
            para = Paragraph(minutas[index].Comentarios, style=styles_claro)
            para.wrapOn(pdf, convertemp(186), convertemp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, convertemp(12), convertemp(linha))
            linha -= 1
        pdf, linha = paragrafo_itens_cobrado(
            pdf, linha, styles_claro, s_minuta
        )
        linha -= 3.5
        if not index == len(minutas) - 1:
            if linha < 50:
                tamanho_font_atual = tamanho_font
                pagina = pdf.getPageNumber()
                pdf.drawCentredString(
                    convertemp(105), convertemp(11), "PÁGINA {}".format(pagina)
                )
                pdf.showPage()
                imprime_cabecalho(pdf, fatura_selecionada)
                linha = 250.8
                pdf.setFont("Times-Roman", tamanho_font_atual)
    pagina = pdf.getPageNumber()
    pdf.drawCentredString(
        convertemp(105), convertemp(11), "PÁGINA {}".format(pagina)
    )
    # End writing the PDF here - Aqui termina a escrita do PDF
    pdf.setTitle(descricao_arquivo)
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    obj = FileUpload.objects.get(idFileUpload=arquivo[0].idFileUpload)
    obj.uploadFile.save(descricao_arquivo, ContentFile(pdf))
    response.write(pdf)
    return [response, pdf]


def print_notas_da_minuta_paragrafo(
    notas_dados,
    idminuta,
    notas,
    pdf,
    styles_claro,
    linha,
    fatura_selecionada,
):
    for itensnotas in notas_dados:
        notas_valor = ""
        if itensnotas["ValorNota"] > 0.00:
            notas_valor = " VALOR {}".format(itensnotas["ValorNota"])
        notas_peso = ""
        if itensnotas["Peso"] > 0.00:
            notas_peso = " PESO {}".format(itensnotas["Peso"])
        notas_volume = ""
        if itensnotas["Volume"] > 0:
            notas_volume = " VOLUME {}".format(itensnotas["Volume"])
        notasguia_dados = MinutaNotas.objects.values(
            "Nota", "NotaGuia", "ValorNota", "Peso", "Volume"
        ).filter(idMinuta=idminuta, NotaGuia=itensnotas["Nota"])
        notasguia = ""
        if notasguia_dados:
            for itensnotasguia in notasguia_dados:
                notasguia_valor = ""
                notasguia_peso = ""
                notasguia_volume = ""
                notasguia_nota = " &#x271B NOTA: {}".format(
                    itensnotasguia["Nota"]
                )
                if itensnotasguia["ValorNota"] > 0.00:
                    notasguia_valor = " VALOR {}".format(
                        itensnotasguia["ValorNota"]
                    )
                if itensnotasguia["Peso"] > 0.00:
                    notasguia_peso = " PESO {}".format(itensnotasguia["Peso"])
                if itensnotasguia["Volume"] > 0:
                    notasguia_volume = " VOLUME {}".format(
                        itensnotasguia["Volume"]
                    )
                notasguia = notasguia + "{}{}{}{}".format(
                    notasguia_nota,
                    notasguia_valor,
                    notasguia_peso,
                    notasguia_volume,
                )
        notas_bairro = ""
        if itensnotas["Bairro"]:
            notas_bairro = " - {}".format(itensnotas["Bairro"])
        if itensnotas["Nome"]:
            notas = "{} &#x2713 NOTA: {}{}{}{}{}{} - {} - {}".format(
                notas,
                itensnotas["Nota"],
                notas_valor,
                notas_peso,
                notas_volume,
                notasguia,
                notas_bairro,
                itensnotas["Cidade"],
                itensnotas["Nome"],
            )
        else:
            notas = "{} &#x2713 NOTA: {}{}{}{}{}{} - {} ".format(
                notas,
                itensnotas["Nota"],
                notas_valor,
                notas_peso,
                notas_volume,
                notasguia,
                notas_bairro,
                itensnotas["Cidade"],
            )
    para = Paragraph(notas, style=styles_claro)
    para.wrapOn(pdf, convertemp(186), convertemp(297))
    linha -= para.height * 0.352777
    para.drawOn(pdf, convertemp(12), convertemp(linha))
    if linha < 25:
        pagina = pdf.getPageNumber()
        pdf.drawCentredString(
            convertemp(105), convertemp(11), "PÁGINA {}".format(pagina)
        )
        pdf.showPage()
        imprime_cabecalho(pdf, fatura_selecionada)
        linha = 250.8
    return linha, pdf


def print_notas_da_minuta_unidade(
    notas_dados,
    idminuta,
    notas,
    pdf,
    styles_claro,
    linha,
    fatura_selecionada,
):
    styles_claro = ParagraphStyle(
        "claro",
        fontName="Times-Roman",
        fontSize=7,
        leading=7,
        alignment=TA_JUSTIFY,
    )
    linha -= 3
    for index, x in enumerate(notas_dados):
        if x["LocalColeta"] == "DESTINATÁRIO":
            coleta = "COLETA"
            destinatario = x["Emitente"]
            endereco = x["Endereco_emi"]
            bairro = x["Bairro_emi"]
            cep = f'{x["CEP_emi"][0:5]}-{x["CEP_emi"][5:]}'
            cidade = x["Cidade_emi"]
            estado = x["Estado_emi"]
        else:
            coleta = "ENTREGA"
            destinatario = x["Nome"]
            endereco = x["Endereco"]
            bairro = x["Bairro"]
            cep = f'{x["CEP"][0:5]}-{x["CEP"][5:]}'
            cidade = x["Cidade"]
            estado = x["Estado"]
        numero = x["Nota"]
        volume = x["Volume"]
        peso = x["Peso"]
        valor = x["ValorNota"]
        status_nota = x["StatusNota"]
        contato = x["Contato"]
        end_compl = f"{endereco} - {bairro} - CEP: {cep} - {cidade} - {estado}"
        vol_compl = f"VOLUME: {volume} - PESO: {valor_ponto_milhar(peso, 3)} - VALOR: R$ {valor_ponto_milhar(valor, 2)} - {status_nota} - {contato}"
        para_compl = f"{end_compl} - {vol_compl}"
        tamanho_font = 7
        pdf.setFont("Times-Roman", tamanho_font)
        pdf.drawString(
            convertemp(12),
            convertemp(linha),
            f"NOTA: {numero} - {coleta} - {destinatario}",
        )
        if para_compl:
            para = Paragraph(para_compl, style=styles_claro)
            para.wrapOn(pdf, convertemp(186), convertemp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, convertemp(12), convertemp(linha))
        if index != len(notas_dados) - 1:
            linha -= 1
            pdf.line(
                convertemp(12),
                convertemp(linha),
                convertemp(198),
                convertemp(linha),
            )
            linha -= 3
        if linha < 25:
            tamanho_font_atual = tamanho_font
            pagina = pdf.getPageNumber()
            pdf.drawCentredString(
                convertemp(105), convertemp(11), "PÁGINA {}".format(pagina)
            )
            pdf.showPage()
            imprime_cabecalho(pdf, fatura_selecionada)
            linha = 250.8
            pdf.setFont("Times-Roman", tamanho_font_atual)
    return linha, pdf
