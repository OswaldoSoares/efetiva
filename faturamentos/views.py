from django.shortcuts import render, redirect
from django.db.models import Sum, Max, Count
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Fatura
from minutas.models import Minuta, MinutaItens
from clientes.models import Cliente, Tabela
from datetime import date, timedelta


def index_faturamento(request):
    fatura = Cliente.objects.values('idCliente',
                                    'Fantasia').filter(minuta__idFatura=None,  minuta__Valor__gt='0.00').annotate(
        Valor=Sum('minuta__Valor'), Quantidade=Count('minuta__Minuta'))
    return render(request, 'faturamentos/index.html', {'fatura': fatura})


def minutas_faturar_cliente(request, idcli):
    minutas_faturar = Minuta.objects.values('Minuta', 'DataMinuta', 'Valor').filter(idCliente=idcli, idFatura=None,
                                                                                    Valor__gt='0.00')
    minuta = Minuta.objects.filter(idCliente=idcli, StatusMinuta='FECHADA')
    minutaitens = MinutaItens.objects.filter(RecebePaga='R').order_by('-TipoItens')
    ultima_fatura = Fatura.objects.aggregate(UltimaFatura=Max('Fatura'))
    if ultima_fatura == None:
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
    context = {'minuta': minuta, 'minutaitens': minutaitens}
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
        obj.StatusFatura = 'ABERTA'
        obj.save()
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
                obj.Obs = minuta.Obs
                obj.StatusMinuta = 'FATURADA'
                obj.Valor = minuta.Valor
                obj.Comentarios = minuta.Comentarios
                obj.idFatura_id = numero_fatura
                obj.idCliente = minuta.idCliente
                obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
                obj.idVeiculo = minuta.idVeiculo
                obj.save()
    return redirect('index_faturamento')
