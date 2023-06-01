from decimal import Decimal
import os
from datetime import datetime
from io import BytesIO
from turtle import color

from django.core.files.base import ContentFile
from django.http import HttpResponse
from minutas.facade import nome_curto
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from reportlab.platypus import Paragraph
from transefetiva.settings.settings import STATIC_ROOT
from website.facade import valor_ponto_milhar
from website.models import FileUpload

from romaneios.models import NotasOcorrencias


def cmp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def print_romaneio(contexto):
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
    header(pdf, contexto)
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
    response["Content-Disposition"] = f'filename="RELATÓRIO - NOTAS: {status_nota}.pdf'
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    header(pdf, contexto)
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


def header(pdf, contexto):
    url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
    nom_empresa = "TRANSEFETIVA TRANSPORTE - EIRELLI - ME"
    end_empresa = "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010"
    fon_empresa = "(11) 2305-0582 - WHATSAPP (11) 94167-0583"
    ema_empresa = "e-mail: transefetiva@terra.com.br - operacional.efetiva@terra.com.br"
    pdf.roundRect(cmp(10), cmp(10), cmp(190), cmp(277), 10)
    pdf.drawImage(url, cmp(12), cmp(265), cmp(40), cmp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawCentredString(cmp(126), cmp(279), nom_empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(273), end_empresa)
    pdf.setFont("Times-Roman", 12)
    pdf.drawCentredString(cmp(126), cmp(268), fon_empresa)
    pdf.drawCentredString(cmp(126), cmp(263), ema_empresa)
    pdf.line(cmp(10), cmp(260), cmp(200), cmp(260))
    pdf.setFillColor(HexColor("#B0C4DE"))
    pdf.setStrokeColor(HexColor("#B0C4DE"))
    pdf.rect(cmp(10), cmp(254.1), cmp(190), cmp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 12)
    return pdf


def header_nota_status(pdf, contexto):
    agora = datetime.now()
    data_hora = agora.strftime("%d/%m/%Y %H:%M")
    status_nota = contexto["sort_status"]
    pdf.drawCentredString(cmp(105), cmp(255.8), f"NOTAS {status_nota} - {data_hora}HS")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    return pdf


def header_romaneio(pdf, contexto):
    rom_numero = str(contexto["romaneio"].Romaneio).zfill(5)
    rom_data_romaneio = contexto["romaneio"].DataRomaneio.strftime("%d/%m/%Y")
    rom_motorista = nome_curto(contexto["romaneio"].idMotorista.Nome)
    rom_placa = contexto["romaneio"].idVeiculo
    pdf.drawString(cmp(12), cmp(255.8), f"ROMANEIO Nº: {rom_numero}")
    pdf.drawCentredString(cmp(105), cmp(255.8), f"{rom_motorista} - {rom_placa}")
    pdf.drawRightString(cmp(198), cmp(255.8), f"{rom_data_romaneio}")
    pdf.line(cmp(10), cmp(254.1), cmp(200), cmp(254.1))
    return pdf


def header_cliente(pdf, contexto):
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
    styles_claro = ParagraphStyle(
        "claro", fontName="Times-Roman", fontSize=7, leading=9, alignment=TA_JUSTIFY
    )
    linha = 242.8
    total_romaneio = Decimal(0.00)
    peso_romaneio = Decimal(0.00)
    for indice, x in enumerate(contexto["notas"]):
        if x.idNotasClientes.LocalColeta == "DESTINATÁRIO":
            coleta = "COLETA"
            local = x.idNotasClientes.Emitente
            cnpj = "00000000000000"
            endereco = x.idNotasClientes.Endereco_emi
            bairro = x.idNotasClientes.Bairro_emi
            if x.idNotasClientes.CEP_emi:
                cep = f"{x.idNotasClientes.CEP_emi[0:5]}-{x.idNotasClientes.CEP_emi[5:]}"
            else:
                cep = "00000-000"
            cidade = x.idNotasClientes.Cidade_emi
            estado = x.idNotasClientes.Estado_emi
            end_compl = f"{endereco} - {bairro} - CEP: {cep} - {cidade} - {estado}"
        else:
            coleta = "ENTREGA"
            local = x.idNotasClientes.Destinatario
            cnpj = x.idNotasClientes.CNPJ
            endereco = x.idNotasClientes.Endereco
            bairro = x.idNotasClientes.Bairro
            if x.idNotasClientes.CEP:
                cep = f"{x.idNotasClientes.CEP[0:5]}-{x.idNotasClientes.CEP[5:]}"
            else:
                cep = "00000-000"
            cidade = x.idNotasClientes.Cidade
            estado = x.idNotasClientes.Estado
            end_compl = f"{endereco} - {bairro} - CEP: {cep} - {cidade} - {estado}"
        id_not = x.idNotasClientes.idNotasClientes
        emitente = nome_curto(x.idNotasClientes.Emitente)
        data_nota = datetime.strftime(x.idNotasClientes.DataColeta, "%d/%m/%Y")
        serie = x.idNotasClientes.SerieNota
        numero = x.idNotasClientes.NumeroNota
        # Cliente não quer que coloca pontos e traços no CNPJ - 29/03/2023
        # cnpj = f"{cnpj[0:2]}.{cnpj[2:5]}.{cnpj[5:8]}/{cnpj[8:12]}-{cnpj[12:15]}"
        volume = x.idNotasClientes.Volume
        peso = f"{valor_ponto_milhar(x.idNotasClientes.Peso)}"
        valor = f"{valor_ponto_milhar(x.idNotasClientes.Valor)}"
        vol_compl = f"VOLUME: {volume} - PESO: {peso} - VALOR: R$ {valor}"
        status_nota = x.idNotasClientes.StatusNota
        contato = x.idNotasClientes.Contato
        informa = x.idNotasClientes.Informa
        con_compl = None
        peso_romaneio += x.idNotasClientes.Peso
        total_romaneio += x.idNotasClientes.Valor
        if contato and informa:
            con_compl = f"{contato} {informa}"
        else:
            if contato:
                con_compl = f"{contato}"
            if informa:
                con_compl = f"{informa}"
        pdf.setFont("Times-Roman", 9)
        pdf.drawString(
            cmp(12), cmp(linha), f"NOTA: {numero} - SÉRIE {serie} - {data_nota}   {emitente}"
        )
        pdf.drawCentredString(cmp(125), cmp(linha), f"{coleta}")
        pdf.setFillColor(HexColor("#FF0000"))
        pdf.drawRightString(cmp(198), cmp(linha), f"{status_nota}")
        pdf.setFillColor(HexColor("#000000"))
        linha -= 2.5
        pdf.setFont("Times-Roman", 7)
        pdf.drawString(cmp(12), cmp(linha), f"{local} - CNPJ: {cnpj}")
        linha -= 2.5
        pdf.drawString(cmp(12), cmp(linha), f"{end_compl}")
        linha -= 2.5
        pdf.drawString(cmp(12), cmp(linha), f"{vol_compl}")
        if con_compl:
            para = Paragraph(con_compl, style=styles_claro)
            para.wrapOn(pdf, cmp(186), cmp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, cmp(12), cmp(linha))
        linha -= 1
        pdf, linha = ocorrencia_nota(id_not, status_nota, pdf, linha)
        pdf.line(cmp(12), cmp(linha), cmp(198), cmp(linha))
        linha -= 3
        if not indice == len(contexto["notas"]) - 1:
            if linha < 50:
                pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
                notas = str(len(contexto["notas"])).zfill(2)
                entregas = str(int(contexto["quantidade_entregas"])).zfill(2)
                total_romaneio_str = f"{valor_ponto_milhar(total_romaneio)}"
                peso_romaneio_str = f"{valor_ponto_milhar(peso_romaneio)}"
                pagina = str(pdf.getPageNumber()).zfill(2)
                pdf.drawString(
                    cmp(20),
                    cmp(11),
                    f"{notas} NOTAS - {entregas} ENTREGAS",
                ),
                pdf.drawCentredString(
                    cmp(105),
                    cmp(11),
                    f"R$ {total_romaneio_str} - PESO {peso_romaneio_str}",
                )
                pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
                pdf.showPage()
                header(pdf, contexto)
                header_romaneio(pdf, contexto)
                header_cliente(pdf, contexto)
                linha = 242.8
    pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
    notas = str(len(contexto["notas"])).zfill(2)
    entregas = str(int(contexto["quantidade_entregas"])).zfill(2)
    total_romaneio_str = f"{valor_ponto_milhar(total_romaneio)}"
    peso_romaneio_str = f"{valor_ponto_milhar(peso_romaneio)}"
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.drawString(cmp(20), cmp(11), f"{notas} NOTAS - {entregas} ENTREGAS"),
    pdf.drawCentredString(
        cmp(105), cmp(11), f"R$ {total_romaneio_str} - PESO {peso_romaneio_str}"
    )
    pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")


def ocorrencia_nota(id_not, status, pdf, linha):
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
    styles_claro = ParagraphStyle(
        "claro",
        fontName="Times-Roman",
        fontSize=7,
        leading=9,
        alignment=TA_JUSTIFY,
        textColor=HexColor("#FF0000"),
    )
    linha = 242.8
    for x in contexto["notas"]:
        data_nota = datetime.strftime(x["data_nota"], "%d/%m/%Y")
        if x["serie_nota"]:
            serie = x["serie_nota"]
        else:
            serie = "NÃO INFORMADA"
        numero = x["numero_nota"]
        destinatario = x["destinatario"]
        if x["cnpj"]:
            cnpj = x["cnpj"]
        else:
            cnpj = "NÃO INFORMADO"
        endereco = x["endereco"]
        bairro = x["bairro"]
        cep = x["cep"]
        cidade = x["cidade"]
        valor = (
            f"{x['valor']:,.2f}".replace(",", "*").replace(".", ",").replace("*", ".")
        )
        if x["placa_motorista"]:
            placa = x["placa_motorista"][0]["placa"]
            motorista = x["placa_motorista"][0]["motorista"]
        else:
            placa = "NÃO INFORMADA"
            motorista = "NÃO INFORMADO"
        pdf.setFont("Times-Roman", 9)
        pdf.drawString(
            cmp(12),
            cmp(linha),
            f"{numero} - {destinatario[0:9]}... - {endereco[0:30]} - {bairro} - CEP: {cep} - {cidade[0:9]}",
        )
        if contexto["sort_status"] == "EM ROTA":
            linha -= 3
            pdf.drawString(
                cmp(12),
                cmp(linha),
                f"{data_nota} - {serie} - VALOR: R$ {valor} - CNPJ: {cnpj} - {motorista} - {placa}",
            )
        if x["ocorrencia"]:
            for y in x["ocorrencia"]:
                data_ocorrencia = y.DataOcorrencia
                ocorrencia = f"{data_ocorrencia} - {y.Ocorrencia}"
                if ocorrencia:
                    para = Paragraph(ocorrencia, style=styles_claro)
                    para.wrapOn(pdf, cmp(186), cmp(297))
                    linha -= para.height * 0.352777
                    para.drawOn(pdf, cmp(12), cmp(linha))
        linha -= 1
        pdf.line(cmp(12), cmp(linha), cmp(198), cmp(linha))
        linha -= 3
        if linha < 20:
            pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
            notas = str(len(contexto["notas"])).zfill(3)
            pagina = str(pdf.getPageNumber()).zfill(2)
            pdf.drawString(cmp(20), cmp(11), f"{notas} NOTAS")
            pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
            pdf.showPage()
            header(pdf, contexto)
            header_nota_status(pdf, contexto)
            header_cliente(pdf, contexto)
            linha = 242.8
    pdf.line(cmp(10), cmp(14), cmp(200), cmp(14))
    notas = str(len(contexto["notas"])).zfill(3)
    pagina = str(pdf.getPageNumber()).zfill(2)
    pdf.drawString(cmp(20), cmp(11), f"{notas} NOTAS")
    pdf.drawRightString(cmp(190), cmp(11), f"PÁGINA {pagina}")
    pdf.showPage()
    return pdf
