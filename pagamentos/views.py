from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from minutas.models import MinutaItens, MinutaColaboradores
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField


def index_pagamento(request):
    qs_colaboradores = MinutaColaboradores.objects.values('idPessoal__Nome').filter(Pago=False).order_by(
        'idPessoal__Nome').annotate(registros=Sum('idPessoal'))
    colaboradores = []
    for index, itens_cr in enumerate(qs_colaboradores):
        colaboradores.append({'Nome': itens_cr['idPessoal__Nome'], 'Total': 0})
        nome = itens_cr['idPessoal__Nome']
        qs_colaborador = MinutaColaboradores.objects.filter(idPessoal__Nome=nome, Pago=False)
        for itens_colaborador in qs_colaborador:
            if itens_colaborador.Cargo == 'AJUDANTE':
                base_valor_ajudante = ExpressionWrapper(F('Valor') / F('Quantidade'), output_field=DecimalField())
                qs_ajudante = MinutaItens.objects.values(ValorAjudante=base_valor_ajudante).filter(
                    TipoItens='PAGA', idMinuta=itens_colaborador.idMinuta, Descricao='AJUDANTE')
                # if qs_ajudante[0]['ValorAjudante']:
                #     valor_ajudante = colaboradores[index]['Total']
                #     valor_adicionar_ajudante = qs_ajudante[0]['ValorAjudante']
                #     colaboradores[index]['Total'] = valor_ajudante + valor_adicionar_ajudante
            elif itens_colaborador.Cargo == 'MOTORISTA':
                qs_motorista = MinutaItens.objects.filter(idMinuta=itens_colaborador.idMinuta).exclude(
                    Descricao='AJUDANTE').exclude(TipoItens='RECEBE').exclude(TipoItens='DESPESA').aggregate(
                    ValorMotorista=Sum('Valor'))
                # if qs_motorista['ValorMotorista']:
                #     valor_motorista = colaboradores[index]['Total']
                #     valor_adicionar_motorista = qs_motorista['ValorMotorista']
                #     colaboradores[index]['Total'] = valor_motorista + valor_adicionar_motorista
    return render(request, 'pagamentos/index.html', {'colaboradores': colaboradores})


def teste(request):
    nome = request.GET.get('nome')
    qs_colaborador = MinutaColaboradores.objects.filter(idPessoal__Nome=nome, Pago=False).exclude(
                idMinuta__StatusMinuta='ABERTA').exclude(idMinuta__StatusMinuta='CONCLUIDA')
    lista_itens_pagar = []
    for index, itens_colaborador in enumerate(qs_colaborador):
        if itens_colaborador.Cargo == 'AJUDANTE':
            base_valor_ajudante = ExpressionWrapper(F('Valor') / F('Quantidade'), output_field=DecimalField())
            qs_ajudante = MinutaItens.objects.values(
                'idMinuta__Minuta', 'Descricao', ValorAjudante=base_valor_ajudante).filter(
                TipoItens='PAGA', idMinuta=itens_colaborador.idMinuta, Descricao='AJUDANTE')
            if qs_ajudante:
                itens_pagar = {}
                itens_pagar['Minuta'] = qs_ajudante[0]['idMinuta__Minuta']
                itens_pagar['Descricao'] = qs_ajudante[0]['Descricao']
                itens_pagar['Valor'] = qs_ajudante[0]['ValorAjudante']
                if itens_pagar:
                    lista_itens_pagar.append(itens_pagar)
        elif itens_colaborador.Cargo == 'MOTORISTA':
            qs_motorista = MinutaItens.objects.values(
                'idMinuta__Minuta', 'Descricao', 'Valor').filter(idMinuta=itens_colaborador.idMinuta).exclude(
                Descricao='AJUDANTE').exclude(TipoItens='RECEBE').exclude(TipoItens='DESPESA')
            if qs_motorista:
                for index_motorista, itens_motorista in enumerate(qs_motorista):
                    itens_pagar = {}
                    itens_pagar['Minuta'] = qs_motorista[index_motorista]['idMinuta__Minuta']
                    itens_pagar['Descricao'] = qs_motorista[index_motorista]['Descricao']
                    itens_pagar['Valor'] = qs_motorista[index_motorista]['Valor']
                    if itens_pagar:
                        lista_itens_pagar.append(itens_pagar)
    data = dict()
    data['html_form'] = render_to_string('pagamentos/pagamentominutas.html', {'qs_ajudante': lista_itens_pagar},
                                         request=request)
    return JsonResponse(data)
