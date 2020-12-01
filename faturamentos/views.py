from django.shortcuts import render
from django.db.models import Sum, Max, Count, F
from django.http import JsonResponse
from django.template.loader import render_to_string
from .models import Fatura
from minutas.models import Minuta, MinutaItens


def index_faturamento(request):
    fatura = Minuta.objects.values('idCliente', 'idCliente__Fantasia').filter(
        idFatura=None, Valor__gt='0.00').annotate(somaminutas=Sum('Valor'), quantidademinutas=Count('idMinuta'))
    return render(request, 'faturamentos/index.html', {'fatura': fatura})



def minutas_faturar_cliente(request, idcli):
    minutas_faturar = Minuta.objects.values('Minuta', 'DataMinuta', 'Valor').filter(idCliente=idcli, idFatura=None,
                                                                                    Valor__gt='0.00')
    minuta = Minuta.objects.filter(idCliente=idcli, StatusMinuta='FECHADA')
    minutaitens = MinutaItens.objects.filter(RecebePaga='R').order_by('-TipoItens')
    ultima_fatura = Fatura.objects.aggregate(UltimaFatura=Max('Fatura'))
    print(ultima_fatura)
    return render(request, 'faturamentos/minutasfaturarcliente.html', {'minuta': minuta, 'minutaitens': minutaitens,
                                                                       'minutas_faturar': minutas_faturar,
                                                                       'ultima_fatura': ultima_fatura})


def cria_div_selecionada(request):
    data = dict()
    numero_minuta = request.GET.get('minuta')
    minuta = Minuta.objects.get(Minuta=numero_minuta)
    minutaitens = MinutaItens.objects.filter(idMinuta_id=minuta.idMinuta, RecebePaga='R').order_by('-TipoItens')
    context = {'minuta': minuta, 'minutaitens': minutaitens}
    data['html_minuta'] = render_to_string('criadivselecionada.html', context, request=request)
    return JsonResponse(data)
