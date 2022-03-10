from django.shortcuts import render, redirect
from django.db.models import Sum, Max, Count
from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from rolepermissions.decorators import has_permission_decorator

from faturamentos.facade import FaturaSelecionada, delete_arquivo, form_fatura, retorna_json
from website.models import FileUpload
from .models import Fatura
from .forms import PagaFatura
from minutas.models import Minuta, MinutaItens, MinutaColaboradores
from clientes.models import Cliente, Tabela, EMailContatoCliente
from pessoas.models import Pessoal
from datetime import date, timedelta
from .imprime import imprime_fatura_pdf


@has_permission_decorator('modulo_faturamento')
def index_faturamento(request):
    fatura = Cliente.objects.values('idCliente', 'Fantasia').filter(
        minuta__StatusMinuta='FECHADA', minuta__Valor__gt='0.00').annotate(Valor=Sum(
        'minuta__Valor'), Quantidade=Count('minuta__Minuta'))
    total_fatura = Minuta.objects.filter(StatusMinuta='FECHADA').aggregate(
        ValorTotal=Sum('Valor'), Quantidade=Count('Minuta'))
    faturada = Fatura.objects.filter(StatusFatura='ABERTA').annotate(TotalMinutas=Count('minuta')).exclude(
        TotalMinutas=0).values('minuta__idCliente__Fantasia', 'idFatura', 'Fatura', 'VencimentoFatura',
                               'ValorFatura', 'TotalMinutas').order_by('VencimentoFatura')
    total_faturada = Fatura.objects.filter(StatusFatura='ABERTA').aggregate(
        ValorTotal=Sum('ValorFatura'), Quantidade=Count('Fatura'))
    paga = Cliente.objects.filter(minuta__idFatura__StatusFatura='PAGA').values(
        'minuta__idFatura__Fatura', 'Fantasia', 'minuta__idFatura__ValorPagamento',
        'minuta__idFatura__DataPagamento', 'minuta__idFatura__idFatura'). annotate(minutas=Count(
        'minuta__idFatura__Fatura')).order_by('-minuta__idFatura__Fatura')
    return render(request, 'faturamentos/index.html', {'fatura': fatura, 'faturada': faturada, 'total_fatura':
        total_fatura, 'total_faturada': total_faturada, 'paga': paga})


def minutas_faturar_cliente(request, idcli):
    minutas_faturar = Minuta.objects.values('Minuta', 'DataMinuta', 'Valor').filter(idCliente=idcli,
                                                                                    StatusMinuta='FECHADA',
                                                                                    Valor__gt='0.00')
    minuta = Minuta.objects.filter(idCliente=idcli, StatusMinuta='FECHADA')
    minutaitens = MinutaItens.objects.filter(RecebePaga='R').order_by('-TipoItens')
    ultima_fatura = Fatura.objects.aggregate(UltimaFatura=Max('Fatura'))
    if ultima_fatura['UltimaFatura'] == None:
        ultima_fatura['UltimaFatura'] = 1
    else:
        ultima_fatura['UltimaFatura'] += 1
    tabela = Tabela.objects.get(idCliente=idcli)
    dia_vencimento = (date.today() + timedelta(days=tabela.idFormaPagamento.Dias)).strftime('%Y-%m-%d')
    return render(request, 'faturamentos/minutasfaturarcliente.html', {'minuta': minuta, 'minutaitens': minutaitens,
                                                                       'minutas_faturar': minutas_faturar,
                                                                       'ultima_fatura': ultima_fatura, 'dia_vencimento':
                                                                           dia_vencimento})


def cria_div_selecionada(request):
    data = dict()
    numero_minuta = request.GET.get('minuta')
    minuta = Minuta.objects.get(Minuta=numero_minuta)
    minutaitens = MinutaItens.objects.filter(idMinuta_id=minuta.idMinuta, RecebePaga='R').order_by('-TipoItens')
    motorista = MinutaColaboradores.objects.filter(idMinuta_id=minuta.idMinuta, Cargo='MOTORISTA')
    if motorista:
        motorista = Pessoal.objects.get(idPessoal=motorista[0].idPessoal_id)
    context = {'minuta': minuta, 'minutaitens': minutaitens, 'motorista': motorista}
    data['html_minuta'] = render_to_string('criadivselecionada.html', context, request=request)
    return JsonResponse(data)


def cria_fatura(request):
    if request.POST.get('valor-fatura') != 'R$ 0,00':
        numero_fatura = request.POST.get('numero-fatura')[10:]
        valor_fatura = request.POST.get('valor-fatura')[3:].replace(',','.')
        vencimento_fatura = request.POST.get('vencimento-fatura')
        minutas_faturadas = request.POST.getlist('numero-minuta')
        obj = Fatura()
        obj.Fatura = numero_fatura
        obj.DataFatura = date.today()
        obj.ValorFatura = valor_fatura
        obj.VencimentoFatura = vencimento_fatura
        obj.DataPagamento = '2020-01-01'
        obj.StatusFatura = 'ABERTA'
        obj.save()
        fatura = Fatura.objects.get(Fatura=numero_fatura)
        for itens in minutas_faturadas:
            minuta = Minuta.objects.get(Minuta=itens)
            if minuta:
                obj = Minuta()
                obj.idMinuta = minuta.idMinuta
                obj.Minuta = minuta.Minuta
                obj.DataMinuta = minuta.DataMinuta
                obj.HoraInicial = minuta.HoraInicial
                obj.HoraFinal = minuta.HoraFinal
                obj.Coleta = minuta.Coleta
                obj.Entrega = minuta.Entrega
                obj.KMInicial = minuta.KMInicial
                obj.KMFinal = minuta.KMFinal
                obj.Obs = minuta.Obs
                obj.StatusMinuta = 'FATURADA'
                obj.Valor = minuta.Valor
                obj.Comentarios = minuta.Comentarios
                obj.idFatura_id = fatura.idFatura
                obj.idCliente = minuta.idCliente
                obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
                obj.idVeiculo = minuta.idVeiculo
                obj.save()
    return redirect('index_faturamento')


def estorna_fatura(request, idfatura):
    novo_status = ''
    fatura = Fatura.objects.get(idFatura=idfatura)
    if fatura.StatusFatura == 'ABERTA':
        minutas = Minuta.objects.filter(idFatura=fatura.idFatura)
        for itens in minutas:
            minuta = Minuta.objects.get(idMinuta=itens.idMinuta)
            if minuta:
                obj = Minuta()
                obj.idMinuta = minuta.idMinuta
                obj.Minuta = minuta.Minuta
                obj.DataMinuta = minuta.DataMinuta
                obj.HoraInicial = minuta.HoraInicial
                obj.HoraFinal = minuta.HoraFinal
                obj.Coleta = minuta.Coleta
                obj.Entrega = minuta.Entrega
                obj.KMInicial = minuta.KMInicial
                obj.KMFinal = minuta.KMFinal
                obj.Obs = minuta.Obs
                obj.StatusMinuta = 'FECHADA'
                obj.Valor = minuta.Valor
                obj.Comentarios = minuta.Comentarios
                obj.idFatura_id = None
                obj.idCliente = minuta.idCliente
                obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
                obj.idVeiculo = minuta.idVeiculo
                obj.save()
        novo_status = 'CANCEL'
    if fatura.StatusFatura == 'PAGA':
        novo_status = 'ABERTA'
    if fatura:
        obj = Fatura(fatura)
        obj.idFatura = fatura.idFatura
        obj.Fatura = fatura.Fatura
        obj.DataFatura = fatura.DataFatura
        obj.ValorFatura = fatura.ValorFatura
        obj.VencimentoFatura = fatura.VencimentoFatura
        obj.DataPagamento = '2020-01-01'
        obj.StatusFatura = novo_status
        obj.save()
    return redirect('index_faturamento')


def paga_fatura(request, idfatura):
    data = dict()
    fatura = Fatura.objects.get(Fatura=idfatura)
    if request.method == 'POST':
        form = PagaFatura(request.POST, instance=fatura)
        if form.is_valid():
            form.save()
            return redirect('index_faturamento')
    else:
        form = PagaFatura(initial={'ValorPagamento': fatura.ValorFatura, 'DataPagamento': date.today(),
                                   'StatusFatura': 'PAGA'}, instance=fatura)
    contexto = {'form': form, 'idfatura': idfatura}
    data['html_form'] = render_to_string('faturamentos/pagafatura.html', contexto, request=request)
    return JsonResponse(data)


def imprime_fatura(request, idfatura):
    response = imprime_fatura_pdf(idfatura)[0]
    return response


def email_fatura(request, idfatura):
    fatura = Fatura.objects.filter(idFatura=idfatura)
    numero_fatura = [item.Fatura for item in fatura]
    numero_fatura = numero_fatura[0]
    cliente = Cliente.objects.filter(minuta__idFatura=idfatura)
    idcliente = [item.idCliente for item in cliente]
    idcliente = idcliente[0]
    emails_to = EMailContatoCliente.objects.filter(idCliente_id=idcliente, RecebeFatura=1)
    lista_emails = [item.EMail for item in emails_to]
    contexto = {'numero_fatura': str(numero_fatura)}
    subject = 'Fatura nº {}'.format(numero_fatura)
    html_message = render_to_string('faturamentos/emailfatura.html', contexto)
    from_email = 'Transefetiva Transportes <financeiro.efetiva@terra.com.br>'
    to = lista_emails
    email = EmailMessage(subject, html_message, from_email, to)
    email.content_subtype = 'html'
    fatura_pdf = imprime_fatura_pdf(idfatura)[1]
    nome_arquivo = 'FATURA {}.pdf'.format(numero_fatura)
    email.attach(nome_arquivo, fatura_pdf)
    email.send()
    return redirect('index_faturamento')


def fatura(request, idfatura):
    text_mensagem = None
    type_mensagem = None
    if request.method == 'POST':
        if request.FILES:
            if request.POST.get('tipo') == 'NOTA':
                v_descricao = f'fatura_{str(idfatura).zfill(6)}_nf'
            elif request.POST.get('tipo') == 'BOLETO':
                v_descricao = f'fatura_{str(idfatura).zfill(6)}_boleto'
            ext_file = request.FILES['uploadFile'].name.split(".")[-1]
            name_file = f'{v_descricao}.{ext_file}'
            request.FILES['uploadFile'].name = name_file
            obj = FileUpload()
            obj.DescricaoUpload = v_descricao
            obj.uploadFile = request.FILES['uploadFile']
            try:
                obj.save()
                text_mensagem = 'Arquivo enviado ao servidor com sucesso'
                type_mensagem = 'SUCESSO'
            except:
                text_mensagem = 'Falha ao salvar seu arquivo, tente novamente'
                type_mensagem = 'ERROR'
        else:
            text_mensagem = 'Arquivo não selecionado'
            type_mensagem = 'ERROR'
    s_fatura = FaturaSelecionada(idfatura).__dict__
    contexto = {'s_fatura': s_fatura, 'text_mensagem': text_mensagem, 'type_mensagem': type_mensagem,}
    return render(request, 'faturamentos/fatura.html', contexto)


def print_file(request):
    pass


def delete_file(request):
    v_idobj = request.GET.get('idobj')
    v_idfatura = request.GET.get('idfatura')
    data = delete_arquivo(request, v_idobj, v_idfatura)
    return data    
