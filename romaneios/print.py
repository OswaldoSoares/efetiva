"""
    Modulo impressões de relátorios
"""
import os
from datetime import datetime
from decimal import Decimal
from io import BytesIO

from django.core.files.base import ContentFile
from django.http import HttpResponse
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import nome_curto, valor_ponto_milhar
from website.models import FileUpload

from romaneios.models import NotasOcorrencias


def cmp(milimetros):
    """

    Args:
        milimetros:

    Returns:


    """
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param milimetros: milimetros
    :return: pontos
    """
    return milimetros / 0.352777


def print_romaneio(contexto):
    """

    Args:
        contexto:

    Returns:


    """
    rom_numero = str(contexto["romaneio"].Romaneio).zfill(5)
    descricao_arquivo = f"Romaneio_{str(rom_numero).zfill(5)}.pdf"
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    if not arquivo:
        obj = FileUpload()
        obj.DescricaoUpload = descricao_arquivo
        obj.save()
        arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    else:
        if arquivo[0].uploadFile:
            try:
                os.remove(arquivo[0].uploadFile.path)
            except FileNotFoundError:
                print("ARQUIVO NÃO ENCONTRADO")
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = f'filename="ROMANEIO {rom_numero}.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    header_romaneio(pdf, contexto)
    header_cliente(pdf, contexto)
    notas_romaneio(pdf, contexto)
    pdf.setTitle(f"ROMANEIO {rom_numero}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    obj = FileUpload.objects.get(idFileUpload=arquivo[0].idFileUpload)
    obj.uploadFile.save(descricao_arquivo, ContentFile(pdf))
    buffer.close()
    response.write(pdf)
    return response


def print_notas_status(contexto):
    """

    Args:
        contexto:

    Returns:


    """
    status_nota = contexto["sort_status"]
    descricao_arquivo = f"Notas {status_nota}.pdf"
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    if not arquivo:
        obj = FileUpload()
        obj.DescricaoUpload = descricao_arquivo
        obj.save()
        arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    else:
        if arquivo[0].uploadFile:
            try:
                os.remove(arquivo[0].uploadFile.path)
            except FileNotFoundError:
                print("OK")
    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f"filename='RELATÓRIO' " f"- NOTAS: {status_nota}.pdf"
    )
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf)
    header_nota_status(pdf, contexto)
    header_cliente(pdf, contexto)
    notas_status(pdf, contexto)
    pdf.setTitle(f"NOTAS {status_nota}.pdf")
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    obj = FileUpload.objects.get(idFileUpload=arquivo[0].idFileUpload)
    obj.uploadFile.save(descricao_arquivo, ContentFile(pdf))
    buffer.close()
    response.write(pdf)
    return response


def header(pdf):
    """

    Args:
        pdf:

    Returns:


    """
    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    empresa = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    rua = "RUA OLIMPIO PORTUGAL, 245 - MOOCA"
    cidade = "SÃO PAULO - SP - CEP 03112-010"
    endereco = f"{rua} - {cidade}"
    telefone = "(11) 2305-0582 - WHATSAPP (11) 94167-0583"
    email_1 = "transefetiva@terra.com.br"
    email_2 = "operacional.efetiva@terra.com.br"
    email = f"e-mail: {email_1} - {email_2}"
    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)
    pdf.drawImage(url, cmp(12), cmp(265), cmp(40), cmp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawCentredString(cmp(126), cmp(279), empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(273), endereco)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(268), telefone)
    pdf.drawCentredString(cmp(126), cmp(263), email)
    pdf.line(cmp(10), cmp(260), cmp(200), cmp(260))
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(254.1), cmp(190), cmp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 12)
    return pdf


def header_nota_status(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    Returns:


    """
    agora = datetime.now()
    data_hora = agora.strftime("%d/%m/%Y %H:%M")
    status_nota = contexto["sort_status"]
    pdf.drawCentredString(
        cmp(105),
        cmp(255.8),
        f"NOTAS {status_nota} - {data_hora}HS",
    )
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    return pdf


def header_romaneio(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    Returns:


    """
    rom_numero = str(contexto["romaneio"].Romaneio).zfill(5)
    rom_data_romaneio = contexto["romaneio"].DataRomaneio.strftime("%d/%m/%Y")
    rom_motorista = nome_curto(contexto["romaneio"].idMotorista.Nome)
    rom_placa = contexto["romaneio"].idVeiculo
    pdf.drawString(cmp(12), cmp(255.8), f"ROMANEIO Nº: {rom_numero}")
    pdf.drawCentredString(
        cmp(105),
        cmp(255.8),
        f"{rom_motorista} - {rom_placa}",
    )
    pdf.drawRightString(cmp(198), cmp(255.8), f"{rom_data_romaneio}")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    return pdf


def header_cliente(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    Returns:


    """
    cli_nome = contexto["cliente"].Nome
    cli_cnpj = contexto["cliente"].CNPJ
    endereco = contexto["cliente"].Endereco
    bairro = contexto["cliente"].Bairro
    cidade = contexto["cliente"].Cidade
    estado = contexto["cliente"].Estado
    cep = contexto["cliente"].CEP
    cli_ende = f"{endereco} - {bairro} - CEP: {cep} - {cidade} - {estado}"
    linha = 250.8
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#483D8B"))
    pdf.drawString(cmp(12), cmp(linha), f"{cli_nome}")
    if cli_cnpj:
        pdf.drawRightString(cmp(198), cmp(linha), f"CNPJ: {cli_cnpj}")
    linha = 247.3
    pdf.drawString(cmp(12), cmp(linha), f"{cli_ende}")
    pdf.setFillColor(HexColor("#000000"))
    linha = 246.3
    pdf.line(cmp(10), cmp(linha), cmp(200), cmp(linha))
    return pdf


def notas_romaneio(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    """
    linha = 242.8
    total_romaneio = Decimal(0.00)
    peso_romaneio = Decimal(0.00)
    for indice, item in enumerate(contexto["notas"]):
        local_endereco = local_servico(item)
        id_not = item.idNotasClientes.idNotasClientes
        data_nota = datetime.strftime(
            item.idNotasClientes.DataColeta,
            "%d/%m/%Y",
        )
        nota_fical = (
            f"NOTA: {item.idNotasClientes.NumeroNota} "
            f"- SÉRIE {item.idNotasClientes.SerieNota} "
            f"- {data_nota}   {nome_curto(item.idNotasClientes.Emitente)}"
        )
        vol_compl = (
            f"VOLUME: {item.idNotasClientes.Volume} "
            f"- PESO: {valor_ponto_milhar(item.idNotasClientes.Peso, 3)} "
            f"- VALOR: R$ {valor_ponto_milhar(item.idNotasClientes.Valor, 2)}"
        )
        status_nota = item.idNotasClientes.StatusNota
        peso_romaneio += item.idNotasClientes.Peso
        total_romaneio += item.idNotasClientes.Valor
        contato_compl = contato_completo(
            item.idNotasClientes.Contato,
            item.idNotasClientes.Informa,
        )
        pdf.setFont("Times-Roman", 9)
        pdf.drawString(cmp(12), cmp(linha), f"{nota_fical}")
        pdf.drawCentredString(
            cmp(125),
            cmp(linha),
            f"{local_endereco['coleta']}",
        )
        pdf.setFillColor(HexColor("#FF0000"))
        pdf.drawRightString(cmp(198), cmp(linha), f"{status_nota}")
        pdf.setFillColor(HexColor("#000000"))
        linha -= 2.5
        pdf.setFont("Times-Roman", 7)
        pdf.drawString(
            cmp(12),
            cmp(linha),
            f"{local_endereco['local']} - CNPJ: {local_endereco['cnpj']}",
        )
        linha -= 2.5
        pdf.drawString(
            cmp(12),
            cmp(linha),
            f"{local_endereco['endereco']} - {local_endereco['bairro']} "
            f"- CEP: {local_endereco['cep']} - {local_endereco['cidade']} "
            f"- {local_endereco['estado']}",
        )
        linha -= 2.5
        pdf.drawString(cmp(12), cmp(linha), f"{vol_compl}")
        if contato_compl:
            para = Paragraph(contato_compl, style=styles_claro())
            para.wrapOn(pdf, cmp(186), cmp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, cmp(12), cmp(linha))
        linha -= 1
        pdf, linha = ocorrencia_nota(id_not, status_nota, pdf, linha)
        pdf.line(cmp(12), cmp(linha), cmp(198), cmp(linha))
        linha -= 3
        if not indice == len(contexto["notas"]) - 1:
            if linha < 50:
                notas_romaneio_fim_pagina(
                    pdf,
                    contexto,
                    total_romaneio,
                    peso_romaneio,
                )
                pdf.showPage()
                header(pdf)
                header_romaneio(pdf, contexto)
                header_cliente(pdf, contexto)
                linha = 242.8
    notas_romaneio_fim_pagina(
        pdf,
        contexto,
        total_romaneio,
        peso_romaneio,
    )


def ocorrencia_nota(id_not, status, pdf, linha):
    """

    Args:
        id_not:
        status:
        pdf:
        linha:

    Returns:


    """
    ocorrencia = NotasOcorrencias.objects.filter(
        idNotasClientes_id=id_not, TipoOcorrencia=status
    ).latest("Ocorrencia")
    if not ocorrencia.TipoOcorrencia == "EM ROTA":
        if ocorrencia.Ocorrencia:
            linha -= 1
            ocorrencia = ocorrencia.Ocorrencia
            pdf.setFillColor(HexColor("#FF0000"))
            pdf.drawString(cmp(12), cmp(linha), f"{ocorrencia}")
            pdf.setFillColor(HexColor("#000000"))
            linha -= 1.5
    return pdf, linha


def notas_status(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    Returns:


    """
    linha = 242.8
    for item_x in contexto["notas"]:
        serie = "NÃO INFORMADA"
        cnpj = "NÃO INFORMADO"
        placa = "NÃO INFORMADA"
        motorista = "NÃO INFORMADO"
        data_nota = datetime.strftime(item_x["data_nota"], "%d/%m/%Y")
        if item_x["serie_nota"]:
            serie = item_x["serie_nota"]
        if item_x["cnpj"]:
            cnpj = item_x["cnpj"]
        valor = (
            f"{item_x['valor']:,.2f}".replace(
                ",",
                "*",
            )
            .replace(
                ".",
                ",",
            )
            .replace(
                "*",
                ".",
            )
        )
        if item_x["placa_motorista"]:
            placa = item_x["placa_motorista"][0]["placa"]
            motorista = item_x["placa_motorista"][0]["motorista"]
        pdf.setFont("Times-Roman", 9)
        if item_x["local_coleta"] == "DESTINATÁRIO":
            pdf.drawString(
                cmp(12),
                cmp(linha),
                (
                    f"{item_x['numero_nota']} "
                    f"- {item_x['emitente'][0:9]}... "
                    f"- {item_x['endereco_emi'][0:30]} "
                    f"- {item_x['bairro_emi']} "
                    f"- CEP: {item_x['cep_emi']} "
                    f"- {item_x['cidade_emi'][0:9]}"
                ),
            )
        else:
            pdf.drawString(
                cmp(12),
                cmp(linha),
                (
                    f"{item_x['numero_nota']} "
                    f"- {item_x['destinatario'][0:9]}... "
                    f"- {item_x['endereco'][0:30]} "
                    f"- {item_x['bairro']} "
                    f"- CEP: {item_x['cep']} "
                    f"- {item_x['cidade'][0:9]}"
                ),
            )
        if contexto["sort_status"] == "EM ROTA":
            linha -= 3
            pdf.drawString(
                cmp(12),
                cmp(linha),
                f"{data_nota} - {serie} - VALOR: R$ {valor} - CNPJ: {cnpj} - {motorista} - {placa}",
            )
        if item_x["ocorrencia"]:
            for item_y in item_x["ocorrencia"]:
                data_ocorrencia = item_y.DataOcorrencia
                ocorrencia = f"{data_ocorrencia} - {item_y.Ocorrencia}"
                if ocorrencia:
                    para = Paragraph(ocorrencia, style=styles_claro())
                    para.wrapOn(pdf, cmp(186), cmp(297))
                    linha -= para.height * 0.352777
                    para.drawOn(pdf, cmp(12), cmp(linha))
        linha -= 1
        pdf.line(cmp(12), cmp(linha), cmp(198), cmp(linha))
        linha -= 3
        if linha < 20:
            notas_status_fim_pagina(pdf, contexto)
            header(pdf)
            header_nota_status(pdf, contexto)
            header_cliente(pdf, contexto)
            linha = 242.8
    notas_status_fim_pagina(pdf, contexto)
    return pdf


def notas_status_fim_pagina(pdf, contexto):
    """

    Args:
        pdf:
        contexto:

    """
    pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
    notas = str(len(contexto["notas"])).zfill(3)
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.drawString(cmp(20), cmp(11), f"{notas} NOTAS")
    pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
    pdf.showPage()


def notas_romaneio_fim_pagina(pdf, contexto, total_romaneio, peso_romaneio):
    """

    Args:
        pdf:
        contexto:
        total_romaneio:
        peso_romaneio:

    """
    pdf.line(
        cmp(10),
        cmp(14),
        cmp(200),
        cmp(14),
    )
    notas = str(len(contexto["notas"])).zfill(2)
    entregas = str(int(contexto["quantidade_entregas"])).zfill(2)
    total_romaneio_str = f"{valor_ponto_milhar(total_romaneio, 2)}"
    peso_romaneio_str = f"{valor_ponto_milhar(peso_romaneio, 3)}"
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.drawString(
        cmp(20),
        cmp(11),
        f"{notas} NOTAS - {entregas} ENTREGAS",
    )
    pdf.drawCentredString(
        cmp(105),
        cmp(11),
        f"R$ {total_romaneio_str} - PESO {peso_romaneio_str}",
    )
    pdf.drawRightString(
        cmp(190),
        cmp(11),
        f"PÁGINA {pagina}",
    )


def styles_claro():
    """

    Returns:


    """
    style = ParagraphStyle(
        "claro",
        fontName="Times-Roman",
        fontSize=7,
        leading=9,
        alignment=TA_JUSTIFY,
    )
    return style


def contato_completo(contato, informa):
    """

    Args:
        contato:
        informa:

    Returns:


    """
    contato_compl = None
    if contato and informa:
        contato_compl = f"{contato} {informa}"
    else:
        if contato:
            contato_compl = f"{contato}"
        if informa:
            contato_compl = f"{informa}"
    return contato_compl


def local_servico(item):
    """

    Args:
        item:

    Returns:


    """
    coleta = None
    local = None
    cnpj = "00000000000000"
    endereco = None
    bairro = None
    cep = "00000-000"
    cidade = None
    estado = None
    if item.idNotasClientes.LocalColeta == "DESTINATÁRIO":
        coleta = "COLETA"
        local = item.idNotasClientes.Emitente
        endereco = item.idNotasClientes.Endereco_emi
        bairro = item.idNotasClientes.Bairro_emi
        if item.idNotasClientes.CEP_emi:
            cep = (
                f"{item.idNotasClientes.CEP_emi[0:5]}"
                f"-{item.idNotasClientes.CEP_emi[5:]}"
            )
        cidade = item.idNotasClientes.Cidade_emi
        estado = item.idNotasClientes.Estado_emi
    else:
        coleta = "ENTREGA"
        local = item.idNotasClientes.Destinatario
        cnpj = item.idNotasClientes.CNPJ
        endereco = item.idNotasClientes.Endereco
        bairro = item.idNotasClientes.Bairro
        if item.idNotasClientes.CEP:
            cep = (
                f"{item.idNotasClientes.CEP[0:5]}"
                f"-{item.idNotasClientes.CEP[5:]}"
            )
        cidade = item.idNotasClientes.Cidade
        estado = item.idNotasClientes.Estado
    return {
        "coleta": coleta,
        "local": local,
        "cnpj": cnpj,
        "endereco": endereco,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
    }
