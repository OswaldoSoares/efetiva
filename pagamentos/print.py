import decimal

from django.http import HttpResponse
from io import BytesIO

from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas


def convertemp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def print_contracheque(contexto, tipoimpressao):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'flename="CONTRACHEQUE {}.pdf'.format('A')
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    linha = 297
    for x in range(1):
        pdf.setFillColor(HexColor("#000000"))
        pdf.rect(convertemp(5), convertemp(linha-18.5), convertemp(173), convertemp(13.5), fill=0)
        pdf.rect(convertemp(5), convertemp(linha-28.3), convertemp(173), convertemp(9.3), fill=0)
        pdf.rect(convertemp(5), convertemp(linha-36), convertemp(173), convertemp(4.8), fill=0)
        pdf.rect(convertemp(5), convertemp(linha-116.3), convertemp(173), convertemp(79.8), fill=0)
        pdf.rect(convertemp(5), convertemp(linha-134.1), convertemp(111.1), convertemp(17.3), fill=0)
        pdf.rect(convertemp(5), convertemp(linha-144.8), convertemp(173), convertemp(10.2), fill=0)
        pdf.rect(convertemp(116.1), convertemp(linha-125.2), convertemp(61.9), convertemp(8.4), fill=0)
        pdf.rect(convertemp(116.1), convertemp(linha-134.1), convertemp(61.9), convertemp(8.4), fill=0)
        pdf.rect(convertemp(180.9), convertemp(linha-144.8), convertemp(24.1), convertemp(139.8), fill=0)
        pdf.line(convertemp(16.7), convertemp(linha-36), convertemp(16.7), convertemp(linha-31.2))
        pdf.line(convertemp(95.9), convertemp(linha-36), convertemp(95.9), convertemp(linha-31.2))
        pdf.line(convertemp(116.1), convertemp(linha-36), convertemp(116.1), convertemp(linha-31.2))
        pdf.line(convertemp(147.8), convertemp(linha-36), convertemp(147.8), convertemp(linha-31.2))
        pdf.line(convertemp(16.7), convertemp(linha-116.3), convertemp(16.7), convertemp(linha-36.5))
        pdf.line(convertemp(95.9), convertemp(linha-116.3), convertemp(95.9), convertemp(linha-36.5))
        pdf.line(convertemp(116.1), convertemp(linha-116.3), convertemp(116.1), convertemp(linha-36.5))
        pdf.line(convertemp(147.8), convertemp(linha-116.3), convertemp(147.8), convertemp(linha-36.5))
        pdf.line(convertemp(147.8), convertemp(linha-125.2), convertemp(147.8), convertemp(linha-116.8))
        pdf.line(convertemp(147.8), convertemp(linha-134.1), convertemp(147.8), convertemp(linha-125.7))
        pdf.setFillColor(HexColor("#808080"))
        pdf.setFont("Times-Roman", 14)
        pdf.drawString(convertemp(101.6), convertemp(linha-11), '{}'.format('Recibo de Pagamento de Salário'))
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(convertemp(5.8), convertemp(linha-22.9), '{}'.format('Código'))
        pdf.drawString(convertemp(20.2), convertemp(linha-22.9), '{}'.format('Nome do Funcioonário'))
        pdf.drawString(convertemp(102.6), convertemp(linha-22.9), '{}'.format(
            'CBO    Emp.   Local   Dept.  Setor   Seção   Fl.'))
        pdf.drawCentredString(convertemp(10.85), convertemp(linha - 35), '{}'.format('Cód.'))
        pdf.drawCentredString(convertemp(56.3), convertemp(linha - 35), '{}'.format('Descrição'))
        pdf.drawCentredString(convertemp(106), convertemp(linha - 35), '{}'.format('Referência'))
        pdf.drawCentredString(convertemp(131.95), convertemp(linha - 35), '{}'.format('Vencimentos'))
        pdf.drawCentredString(convertemp(162.9), convertemp(linha - 35), '{}'.format('Descontos'))
        pdf.setFont("Times-Roman", 9)
        pdf.drawCentredString(convertemp(131.95), convertemp(linha - 119.7), '{}'.format('Total de Vencimentos'))
        pdf.drawCentredString(convertemp(162.9), convertemp(linha - 119.7), '{}'.format('Total de Descontos'))
        pdf.drawCentredString(convertemp(131.95), convertemp(linha - 132), '{} {}'.format('Valor Líquido', '\u279C'))
        pdf.setFillColor(HexColor("#000000"))
        pdf.setFont("Times-Roman", 11)
        pdf.drawString(convertemp(6), convertemp(linha-13.8), '{}'.format('TRANSEFETIVA TRANSPORTES - EIRELLI - ME'))
        pdf.drawString(convertemp(6), convertemp(linha-17.7), '{}'.format('CNPJ: 21.602.117/0001-15'))
        pdf.drawString(convertemp(122.8), convertemp(linha-17.7), '{}'.format(contexto['contracheque'][0]))
        pdf.setFont("Times-Roman", 10)
        pdf.drawString(convertemp(5.8), convertemp(linha-27.2), '{}'.format(
            contexto['colaborador'][0].idPessoal).zfill(4))
        pdf.drawString(convertemp(20.2), convertemp(linha-27.4), '{}'.format(contexto['colaborador'][0].Nome))
        pdf.drawString(convertemp(102.6), convertemp(linha-27.2), '{}'.format(contexto['colaborador'][0].Categoria))
        pdf.setFont("Times-Roman", 11)
        linhaitens = 0
        for itens in contexto['contrachequeitens']:
            if tipoimpressao == 'CONTRACHEQUE':
                pdf.drawString(convertemp(17.5), convertemp(linha - 41.2 - linhaitens), '{}'.format(itens.Descricao))
                pdf.drawCentredString(convertemp(106), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                    itens.Referencia))
                if itens.Registro == 'C':
                    pdf.drawRightString(convertemp(142.6), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Valor).replace('.', ','))
                else:
                    pdf.drawRightString(convertemp(171.7), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Valor).replace('.', ','))
                linhaitens += 4.1
            else:
                if tipoimpressao == 'ADIANTAMENTO' and itens.Descricao == 'ADIANTAMENTO':
                    pdf.drawString(convertemp(17.5), convertemp(linha - 41.2 - linhaitens),
                                   '{}'.format(itens.Descricao))
                    pdf.drawCentredString(convertemp(106), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Referencia))
                    pdf.drawRightString(convertemp(142.6), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Valor).replace('.', ','))
                    linhaitens += 4.1
                if tipoimpressao == 'VALE TRANSPORTE' and itens.Descricao == 'VALE TRANSPORTE':
                    pdf.drawString(convertemp(17.5), convertemp(linha - 41.2 - linhaitens),
                                   '{}'.format(itens.Descricao))
                    pdf.drawCentredString(convertemp(106), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Referencia))
                    pdf.drawRightString(convertemp(142.6), convertemp(linha - 41.2 - linhaitens), '{}'.format(
                        itens.Valor).replace('.', ','))
                    linhaitens += 4.1
        pdf.drawRightString(convertemp(142.6), convertemp(linha - 124), '{}'.format(
            contexto['totais']['Credito']).replace('.', ','))
        pdf.drawRightString(convertemp(171.7), convertemp(linha - 124), '{}'.format(
            contexto['totais']['Debito']).replace('.', ','))
        pdf.drawRightString(convertemp(171.7), convertemp(linha - 132), '{}'.format(
            contexto['totais']['Liquido']).replace('.', ','))
        # linha = 148
    # pdf.drawString(convertemp(5), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawString(convertemp(70), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawRightString(convertemp(140), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.drawRightString(convertemp(205), convertemp(147.4), '{}'.format('\u2702'))
    # pdf.setLineWidth(0.5)
    if tipoimpressao == 'CONTRACHEQUE':
        if contexto['minutas']:
            linha = 135
            numerominutas = len(contexto['minutas'])
            pdf.setFont("Times-Roman", 9)
            pdf.rect(convertemp(5), convertemp(linha), convertemp(200), convertemp(6), fill=0)
            pdf.drawCentredString(convertemp(105), convertemp(linha + 1.5), '{} - {}'.format(
                len(contexto['minutas']), 'MINUTAS'))
            linha -= 4
            pdf.setFont("Times-Roman", 9)
            pdf.drawCentredString(convertemp(15), convertemp(linha), '{}'.format('DATA'))
            pdf.drawCentredString(convertemp(40), convertemp(linha), '{}'.format('MINUTA'))
            pdf.drawCentredString(convertemp(90), convertemp(linha), '{}'.format('CLIENTE'))
            pdf.drawCentredString(convertemp(165), convertemp(linha), '{}'.format('INICIO'))
            pdf.drawCentredString(convertemp(180), convertemp(linha), '{}'.format('FIM'))
            pdf.drawCentredString(convertemp(195), convertemp(linha), '{}'.format('EXTRA'))
            pdf.line(convertemp(5), convertemp(linha - 1), convertemp(205), convertemp(linha - 1))
            linha -= 4
            for minutas in contexto['minutas']:
                pdf.drawCentredString(convertemp(15), convertemp(linha), '{}'.format(
                    minutas['idMinuta_id__DataMinuta'].strftime("%d/%m/%Y")))
                pdf.drawCentredString(convertemp(40), convertemp(linha), '{}'.format(
                    minutas['idMinuta_id__Minuta']))
                pdf.drawCentredString(convertemp(90), convertemp(linha), '{}'.format(
                    minutas['idMinuta_id__idCliente__Fantasia']))
                pdf.drawCentredString(convertemp(165), convertemp(linha), '{}'.format(
                    minutas['idMinuta_id__HoraInicial']))
                pdf.drawCentredString(convertemp(180), convertemp(linha), '{}'.format(
                    minutas['idMinuta_id__HoraFinal']))
                if minutas['Extra'] != '00:00':
                    pdf.drawCentredString(convertemp(195), convertemp(linha), '{}'.format(minutas['Extra']))
                linha -= 4
            # linha += 3
            pdf.rect(convertemp(5), convertemp(linha + 3), convertemp(200), convertemp(numerominutas * 4 + 5), fill=0)
    pdf.setFont("Times-Roman", 9)
    pdf.setFillColor(HexColor("#808080"))
    pdf.line(convertemp(0), convertemp(148.5), convertemp(210), convertemp(148.5))
    pdf.rotate(90)
    linha = 297
    for x in range(1):
        pdf.drawString(convertemp(linha - 138), convertemp(-186), 'DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA '
                                                                  'DISCRIMINADA NESTE RECIBO')
        pdf.drawString(convertemp(linha - 133), convertemp(-197), '_____/_____/_____')
        pdf.drawString(convertemp(linha - 133), convertemp(-201), '          DATA       ')
        pdf.drawString(convertemp(linha - 83), convertemp(-197), '_______________________________')
        pdf.drawString(convertemp(linha - 83), convertemp(-201), 'ASSINATURA DO FUNCIONÁRIO')
        # linha = 148.5
    pdf.setTitle('contracheque.pdf')
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response


def print_recibo(contexto):
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'flename="CONTRACHEQUE {}.pdf'.format('A')
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.setFont("Times-Roman", 10)
    linha = 297
    pdf.setFillColor(HexColor("#000000"))
    pdf.rect(convertemp(5), convertemp(linha - 16.5), convertemp(200), convertemp(12), fill=0)
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(6), convertemp(linha - 10), '{}'.format('TRANSEFETIVA TRANSPORTES - EIRELLI - ME'))
    pdf.drawString(convertemp(6), convertemp(linha - 14), '{}'.format('CNPJ: 21.602.117/0001-15'))
    pdf.drawRightString(convertemp(204), convertemp(linha - 10), '{}: {}'.format('RECIBO', str(contexto[
        'recibo'].Recibo).zfill(6)))
    pdf.drawRightString(convertemp(204), convertemp(linha - 14), 'R$ {:.2f}'.format(contexto[
        'recibo'].ValorRecibo).replace('.', ','))
    pdf.rect(convertemp(5), convertemp(linha - 23.5), convertemp(200), convertemp(5), fill=0)
    pdf.drawCentredString(convertemp(105), convertemp(linha - 22.5), '{}'.format(contexto['colaborador']))
    pdf.setFillColor(HexColor("#808080"))
    pdf.setFont("Times-Roman", 14)
    pdf.drawString(convertemp(6), convertemp(linha - 28), '{}'.format('Minuta'))
    pdf.drawCentredString(convertemp(32), convertemp(linha - 28), '{}'.format('Data'))
    pdf.drawString(convertemp(45), convertemp(linha - 28), '{}'.format('Cliente'))
    pdf.drawString(convertemp(90), convertemp(linha - 28), '{}'.format('Descricao'))
    pdf.drawRightString(convertemp(204), convertemp(linha - 28), '{}'.format('Valor'))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 11)
    linhaitens = 0
    total_vencimentos = decimal.Decimal(0.00)
    for itens in contexto['reciboitens']:
        pdf.drawString(convertemp(6), convertemp(linha - 33 - linhaitens), '{}'.format(str(itens['Minuta']).zfill(6)))
        pdf.drawCentredString(convertemp(32), convertemp(linha - 33 - linhaitens), '{}'.format(
            itens['Data'].strftime("%d/%m/%Y")))
        pdf.drawString(convertemp(45), convertemp(linha - 33 - linhaitens), '{}'.format(itens['Cliente']))
        if itens['Descricao'] == 'AJUDANTE':
            pdf.drawString(convertemp(90), convertemp(linha - 33 - linhaitens), '{} DE {}'.format(
                itens['Descricao'], str(itens['Motorista'])[0:30]))
        else:
            pdf.drawString(convertemp(90), convertemp(linha - 33 - linhaitens), '{}'.format(itens['Descricao']))
        pdf.drawRightString(convertemp(204), convertemp(linha - 33 - linhaitens), 'R$ {:.2f}'.format(
            itens['Valor']).replace('.', ','))
        total_vencimentos += itens['Valor']
        linhaitens += 4.1
    pdf.drawRightString(convertemp(204), convertemp(linha - 36 - linhaitens), 'Total: R$ {}'.format(
        total_vencimentos).replace('.', ','))
    pdf.rect(convertemp(5), convertemp(linha - 37 - linhaitens), convertemp(200), convertemp(13.5 + linhaitens), fill=0)
    pdf.rect(convertemp(5), convertemp(linha - 43.5 - linhaitens), convertemp(200), convertemp(5), fill=0)
    marca = linha - 43.5 - linhaitens
    pdf.drawCentredString(convertemp(105), convertemp(linha - 42.5 - linhaitens), '{}'.format('DESCONTOS'))
    pdf.setFillColor(HexColor("#808080"))
    pdf.setFont("Times-Roman", 14)
    pdf.drawString(convertemp(6), convertemp(linha - 48 - linhaitens), '{}'.format('Data'))
    pdf.drawString(convertemp(45), convertemp(linha - 48 - linhaitens), '{}'.format('Descricao'))
    pdf.drawRightString(convertemp(204), convertemp(linha - 48 - linhaitens), '{}'.format('Valor'))
    pdf.setFillColor(HexColor("#000000"))
    pdf.setFont("Times-Roman", 11)
    total_vales = decimal.Decimal(0.00)
    for itens in contexto['vales']:
        pdf.drawString(convertemp(6), convertemp(linha - 53 - linhaitens), '{}'.format(
            itens.Data.strftime("%d/%m/%Y")))
        pdf.drawString(convertemp(45), convertemp(linha - 53 - linhaitens), '{}'.format(itens.Descricao))
        pdf.drawRightString(convertemp(204), convertemp(linha - 53 - linhaitens), 'R$ {}'.format(
            itens.Valor).replace('.', ','))
        total_vales += itens.Valor
        linhaitens += 4.1
    pdf.drawRightString(convertemp(204), convertemp(linha - 56 - linhaitens), 'Total: R$ {:.2f}'.format(
        total_vales).replace('.', ','))
    pdf.rect(convertemp(5), convertemp(linha - 57 - linhaitens), convertemp(200), convertemp(
        marca - (linha - 57 - linhaitens)), fill=0)
    pdf.rect(convertemp(5), convertemp(5), convertemp(200), convertemp(15), fill=0)
    pdf.setFont("Times-Roman", 9)
    pdf.setFillColor(HexColor("#808080"))
    pdf.drawString(convertemp(6), convertemp(16.5), 'DECLARO TER RECEBIDO A IMPORTÂNCIA LÍQUIDA DISCRIMINADA NESTE '
                                                    'RECIBO')
    pdf.drawCentredString(convertemp(40), convertemp(10), '_____/_____/_____')
    pdf.drawCentredString(convertemp(40), convertemp(6), 'DATA')
    pdf.drawCentredString(convertemp(170), convertemp(10), '_______________________________')
    pdf.drawCentredString(convertemp(170), convertemp(6), 'ASSINATURA')
    pdf.setTitle('recibo.pdf')
    pdf.save()
    buffer.seek(0)
    pdf = buffer.getvalue()
    buffer.close()
    response.write(pdf)
    return response
