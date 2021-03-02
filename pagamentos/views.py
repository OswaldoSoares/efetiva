from django.shortcuts import render
from minutas.models import MinutaItens, Minuta
from pessoas.models import Pessoal
from django.db.models import Count, Sum


def index_pagamento(request):
    itens = MinutaItens.objects.filter(TipoItens='PAGA').exclude(Descricao='AJUDANTE').order_by('idMinuta')
    teste = MinutaItens.objects.all().exclude


    nome = 'idMinuta__minutacolaboradores__idPessoal__Nome'
    a = MinutaItens.objects.values(nome).exclude(Descricao='AJUDANTE').annotate(valor=Sum('Valor')).order_by(
        nome).filter(TipoItens='PAGA')
    b = a.exclude(idMinuta_id__StatusMinuta='ABERTA', idMinuta__minutacolaboradores__Cargo='AJUDANTE')
    print(b)


    z = MinutaItens.objects.filter(TipoItens='PAGA',
                                   idMinuta__minutacolaboradores__idPessoal__Nome='ADRIANO CASTELANI MAGALHÃES')
    c = z.exclude(idMinuta_id__StatusMinuta='ABERTA').exclude(idMinuta__minutacolaboradores__Cargo='AJUDANTE').exclude(
                  Descricao='AJUDANTE').values('Descricao', 'Valor', 'idMinuta__Minuta')
    print(c.query)


    return render(request, 'pagamentos/index.html', {'itens': itens, 'b': b, 'c': c})



    # fatura = Cliente.objects.values('idCliente', 'Fantasia').filter(minuta__StatusMinuta='FECHADA', minuta__Valor__gt='0.00').annotate( Valor=Sum('minuta__Valor'), Quantidade=Count('minuta__Minuta'))

    # total_fatura = Minuta.objects.filter(StatusMinuta='FECHADA').aggregate(ValorTotal=Sum('Valor'),
    #                                                                        Quantidade=Count('Minuta'))

    # faturada = Fatura.objects.filter(StatusFatura='ABERTA').annotate(TotalMinutas=Count('minuta')).exclude(
    #     TotalMinutas=0).values('minuta__idCliente__Fantasia', 'idFatura', 'Fatura', 'VencimentoFatura',
    #                            'ValorFatura', 'TotalMinutas')

    # total_faturada = Fatura.objects.filter(StatusFatura='ABERTA').aggregate(ValorTotal=Sum('ValorFatura'),
    #                                                                         Quantidade=Count('Fatura'))

    # paga = Cliente.objects.filter(minuta__idFatura__StatusFatura='PAGA').values('minuta__idFatura__Fatura', 'Fantasia',
    #                                                                             'minuta__idFatura__ValorPagamento',
    #                                                                             'minuta__idFatura__DataPagamento',
    #                                                                             'minuta__idFatura__idFatura'). \
    #        annotate(minutas=Count('minuta__idFatura__Fatura')).order_by('-minuta__idFatura__Fatura')

    # return render(request, 'faturamentos/index.html', {'fatura': fatura, 'faturada': faturada, 'total_fatura':
    #     total_fatura, 'total_faturada': total_faturada, 'paga': paga})

