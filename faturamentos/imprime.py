from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.colors import HexColor
from reportlab.platypus import Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_JUSTIFY
from io import BytesIO
from minutas.views import convertemp
from minutas.models import Minuta, MinutaColaboradores, MinutaItens


def decricao_servico(dict_servicos):
    servicos = None
    print(dict_servicos)
    for itens in dict_servicos:
        print(itens['Descricao'])
        if itens['Descricao'] == 'TAXA DE EXPEDIÇÃO':
            servicos = 'TAXA DE EXPEDICAO R$ {},'.format(itens['Valor'])
        if itens['Descricao'] == 'HORAS':
            servicos = '{} {} HORAS NO VALOR DE R$ {} TOTAL R$ {},'.format(servicos, itens['Tempo'],
                                                                           itens['ValorBase'], itens['Valor'])
        if itens['Descricao'] == 'HORAS EXCEDENTE':
            servicos = '{} {} HORAS EXCEDENTE NO VALOR DE R$ {} TOTAL R$ {},'.format(servicos, itens['Tempo'],
                                                                           itens['ValorBase'], itens['Valor'])
        if itens['Descricao'] == 'ENTREGAS':
            servicos = '{} {} ENTREGAS NO VALOR DE R$ {} TOTAL R$ {},'.format(servicos, itens['Quantidade'],
                                                                              itens['Valor'], itens['Valor'])
        if itens['Descricao'] == 'ENTREGAS VOLUME':
            servicos = '{} {} VOLUME NO VALOR DE R$ {} TOTAL R$ {},'.format(servicos, itens['Quantidade'],
                                                                              itens['ValorBase'], itens['Valor'])
        if itens['Descricao'] == 'SAIDA':
            servicos = '{} SAÍDA R$ {},'.format(servicos, itens['Valor'])
    return servicos


def imprime_cabecalho(pdf):
    pdf.roundRect(convertemp(10), convertemp(10), convertemp(190), convertemp(277), 10)
    pdf.drawImage('website/static/website/img/transportadora.jpg', convertemp(12), convertemp(265), convertemp(40),
                  convertemp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawString(convertemp(56), convertemp(279), 'TRANSEFETIVA TRANSPORTE - EIRELLI - ME')
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(57), convertemp(273), 'RUA GUARATINGUETÁ, 276 - MOOCA - SÃO PAULO - SP - CEP 03112-080')
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(70), convertemp(268), '(11) 2305-0582 - (11) 2305-0583 - WHATSAPP (11) 94167-0583')
    pdf.drawString(convertemp(67), convertemp(263), 'e-mail: transefetiva@terra.com.br - '
                                                    'operacional.efetiva@terra.com.br')
    pdf.line(convertemp(10), convertemp(260), convertemp(200), convertemp(260))
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.setStrokeColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(10), convertemp(254.1), convertemp(190), convertemp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(12), convertemp(255.8), 'FATURA Nº: ' + str())
    pdf.drawCentredString(convertemp(105), convertemp(255.8), 'VENCIMENTO: ' + '')
    pdf.drawRightString(convertemp(198), convertemp(255.8), 'VALOR: ' + '')
    pdf.line(convertemp(10), convertemp(254.1), convertemp(200), convertemp(254.1))


def imprime_fatura_my(request, fatura):
    minutas = Minuta.objects.filter(idFatura=fatura)
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    styles_claro = ParagraphStyle('claro', fontName='Times-Roman', fontSize=8, leading=9, alignment=TA_JUSTIFY)
    styles_escuro = ParagraphStyle('escuro', fontName='Times-Roman', fontSize=8, leading=9, alignment=TA_JUSTIFY,
                                   backColor='#c1c1c1')
    imprime_cabecalho(pdf)
    linha = 250.8
    for index, itens in enumerate(minutas):
        minuta_colaboradores = MinutaColaboradores.objects.filter(idMinuta=minutas[index].idMinuta, Cargo='MOTORISTA')
        minuta_numero = minutas[index].Minuta
        minuta_data = minutas[index].DataMinuta.strftime("%d/%m/%Y")
        minuta_motorista = None
        if minuta_colaboradores:
            minuta_motorista = minuta_colaboradores[0].idPessoal
        minuta_veiculo = minutas[index].idCategoriaVeiculo
        minuta_marca_modelo = None
        minuta_placa = None
        if minutas[index].idVeiculo:
            minuta_marca_modelo = minutas[index].idVeiculo.Marca + ' ' + minutas[index].idVeiculo.Modelo
            minuta_placa = minutas[index].idVeiculo
        minuta_valor = minutas[index].Valor
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(convertemp(12), convertemp(linha), 'MINUTA: {}'.format(minuta_numero))
        pdf.drawCentredString(convertemp(105), convertemp(linha), 'DATA: {} '.format(minuta_data))
        pdf.drawRightString(convertemp(198), convertemp(linha), 'VALOR: R$ {:.2f}'.format(minuta_valor).replace('.',
                                                                                                                ','))
        linha -= 3
        pdf.setFont("Times-Roman", 8)
        if minuta_motorista:
            pdf.drawString(convertemp(12), convertemp(linha), '{}'.format(minuta_motorista))
        if minuta_veiculo:
            pdf.drawCentredString(convertemp(105), convertemp(linha), 'SOLICITADO: {}'.format(minuta_veiculo))
        if minuta_placa:
            pdf.drawRightString(convertemp(198), convertemp(linha), '{} - {}'.format(minuta_marca_modelo, minuta_placa))
        coleta_entrega = None
        if minutas[index].Coleta and minutas[index].Entrega:
            coleta_entrega = 'COLETA: {} - ENTREGA: {}'.format(minutas[index].Coleta, minutas[index].Entrega)
        elif minutas[index].Coleta:
            coleta_entrega = 'COLETA: {}'.format(minutas[index].Coleta)
        elif minutas[index].Entrega:
            coleta_entrega = 'ENTREGA: {}'.format(minutas[index].Entrega)
        if coleta_entrega:
            linha -= 1
            para = Paragraph(coleta_entrega, style=styles_claro)
            para.wrapOn(pdf, convertemp(186), convertemp(297))
            linha -= para.height * 0.352777
            para.drawOn(pdf, convertemp(12), convertemp(linha))
        linha -= 1
        pdf.line(convertemp(12), convertemp(linha), convertemp(198), convertemp(linha))
        linha -= 1
        minuta_itens = MinutaItens.objects.values().filter(idMinuta=minutas[index].idMinuta, RecebePaga='R')
        serviços = decricao_servico(minuta_itens)
        para = Paragraph(serviços, style=styles_escuro)
        para.wrapOn(pdf, convertemp(186), convertemp(297))
        linha -= para.height * 0.352777
        para.drawOn(pdf, convertemp(12), convertemp(linha))
        linha -= 1
        pdf.line(convertemp(12), convertemp(linha), convertemp(198), convertemp(linha))
        linha -= 3
        if linha < 200:
            pdf.showPage()
            imprime_cabecalho(pdf)
            linha = 250.8

    pdf.setTitle('Fatura.pdf')
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)

    return response
