from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string

from minutas.models import MinutaItens, MinutaColaboradores
from pessoas.models import Pessoal
from pagamentos import facade
from django.db.models import Count, Sum, F, ExpressionWrapper, DecimalField


def index_pagamento(request):
    contexto = facade.create_context_formcontracheque()
    # qs_colaboradores = MinutaColaboradores.objects.values('idPessoal__Nome').filter(Pago=False).order_by(
    #     'idPessoal__Nome').annotate(registros=Sum('idPessoal')).exclude(idPessoal__TipoPgto='MENSAL - BANCO DE HORAS')
    # qs_mensalistas = Pessoal.objects.filter(TipoPgto='MENSAL - BANCO DE HORAS').order_by('Nome')
    # colaboradores = []
    # for index, itens_cr in enumerate(qs_colaboradores):
    #     colaboradores.append({'Nome': itens_cr['idPessoal__Nome'], 'Total': 0})
    #     nome = itens_cr['idPessoal__Nome']
    #     qs_colaborador = MinutaColaboradores.objects.filter(idPessoal__Nome=nome, Pago=False)
    #     for itens_colaborador in qs_colaborador:
    #         if itens_colaborador.Cargo == 'AJUDANTE':
    #             base_valor_ajudante = ExpressionWrapper(F('Valor') / F('Quantidade'), output_field=DecimalField())
    #             qs_ajudante = MinutaItens.objects.values(ValorAjudante=base_valor_ajudante).filter(
    #                 TipoItens='PAGA', idMinuta=itens_colaborador.idMinuta, Descricao='AJUDANTE')
    #             if qs_ajudante:
    #                 valor_ajudante = colaboradores[index]['Total']
    #                 valor_adicionar_ajudante = qs_ajudante[0]['ValorAjudante']
    #                 colaboradores[index]['Total'] = valor_ajudante + valor_adicionar_ajudante
    #         elif itens_colaborador.Cargo == 'MOTORISTA':
    #             qs_motorista = MinutaItens.objects.filter(idMinuta=itens_colaborador.idMinuta).exclude(
    #                 Descricao='AJUDANTE').exclude(TipoItens='RECEBE').exclude(TipoItens='DESPESA').aggregate(
    #                 ValorMotorista=Sum('Valor'))
    #             if qs_motorista['ValorMotorista']:
    #                 valor_motorista = colaboradores[index]['Total']
    #                 valor_adicionar_motorista = qs_motorista['ValorMotorista']
    #                 colaboradores[index]['Total'] = valor_motorista + valor_adicionar_motorista
    # contexto2 = {'colaboradores': colaboradores, 'qs_mensalistas': qs_mensalistas}
    # contexto.update(contexto2)
    return render(request, 'pagamentos/index.html', contexto)


def teste(request):
    nome = request.GET.get('nome')
    qs_colaborador = MinutaColaboradores.objects.filter(idPessoal__Nome=nome, Pago=False).exclude(
        idMinuta__StatusMinuta='ABERTA').exclude(idMinuta__StatusMinuta='CONCLUIDA')
    lista_itens_pagar = []
    for index, itens_colaborador in enumerate(qs_colaborador):
        if itens_colaborador.Cargo == 'AJUDANTE':
            base_valor_ajudante = ExpressionWrapper(F('Valor') / F('Quantidade'), output_field=DecimalField())
            qs_ajudante = MinutaItens.objects.values(
                'idMinutaItens', 'idMinuta__Minuta', 'Descricao', ValorAjudante=base_valor_ajudante).filter(
                TipoItens='PAGA', idMinuta=itens_colaborador.idMinuta, Descricao='AJUDANTE')
            if qs_ajudante:
                itens_pagar = {}
                itens_pagar['idMinutaItens'] = qs_ajudante[0]['idMinutaItens']
                itens_pagar['Minuta'] = qs_ajudante[0]['idMinuta__Minuta']
                itens_pagar['Descricao'] = qs_ajudante[0]['Descricao']
                itens_pagar['Valor'] = qs_ajudante[0]['ValorAjudante']
                if itens_pagar:
                    lista_itens_pagar.append(itens_pagar)
        elif itens_colaborador.Cargo == 'MOTORISTA':
            qs_motorista = MinutaItens.objects.values(
                'idMinutaItens', 'idMinuta__Minuta', 'Descricao', 'Valor').filter(
                idMinuta=itens_colaborador.idMinuta).exclude(
                Descricao='AJUDANTE').exclude(TipoItens='RECEBE').exclude(TipoItens='DESPESA')
            if qs_motorista:
                for index_motorista, itens_motorista in enumerate(qs_motorista):
                    itens_pagar = {}
                    itens_pagar['idMinutaItens'] = qs_motorista[index_motorista]['idMinutaItens']
                    itens_pagar['Minuta'] = qs_motorista[index_motorista]['idMinuta__Minuta']
                    itens_pagar['Descricao'] = qs_motorista[index_motorista]['Descricao']
                    itens_pagar['Valor'] = qs_motorista[index_motorista]['Valor']
                    if itens_pagar:
                        lista_itens_pagar.append(itens_pagar)
    data = dict()
    data['html_form'] = render_to_string('pagamentos/pagamentominutas.html', {'lista_itens_pagar': lista_itens_pagar},
                                         request=request)
    return JsonResponse(data)


def cria_folha(request):
    c_mes = request.GET.get('MesReferencia')
    c_ano = request.GET.get('AnoReferencia')
    facade.create_folha(c_mes, c_ano)
    data = facade.seleciona_folha(request, c_mes, c_ano)
    return data


def cria_contrachequeitens(request):
    c_descricao = request.POST.get('Descricao')
    c_valor = request.POST.get('Valor')
    c_registro = request.POST.get('Registro')
    c_idcontracheque = request.POST.get('idContraCheque')
    facade.facade.create_contracheque_itens(c_descricao, c_valor, c_registro, c_idcontracheque)
    c_mes = request.POST.get('MesReferencia')
    c_ano = request.POST.get('AnoReferencia')
    c_idpesssoal = request.POST.get('idPessoal')
    data = seleciona_folha(request)
    # data += facade.seleciona_contracheque(request, c_mes, c_ano, c_idpesssoal)
    return data


def seleciona_folha(request):
    c_mes = request.POST.get('MesReferencia')
    c_ano = request.POST.get('AnoReferencia')
    data = facade.seleciona_folha(request, c_mes, c_ano)
    return data


def seleciona_contracheque(request):
    c_mes = request.GET.get('MesReferencia')
    c_ano = request.GET.get('AnoReferencia')
    c_idpesssoal = request.GET.get('idPessoal')
    facade.atualiza_cartaoponto(c_mes, c_ano, c_idpesssoal)
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpesssoal)
    return data


def manutencao(request):
    contracheque = facade.ContraCheque.objects.all()
    contrachequeitens = facade.ContraChequeItens.objects.all()
    cartaoponto = facade.CartaoPonto.objects.all()
    contexto = {'contracheque': contracheque, 'contrachequeitens': contrachequeitens, 'cartaoponto': cartaoponto}
    return render(request, 'pagamentos/manutencao.html', contexto)


def apagar_tudo(request):
    contracheque = facade.ContraCheque.objects.all()
    contrachequeitens = facade.ContraChequeItens.objects.all()
    cartaoponto = facade.CartaoPonto.objects.all()
    contracheque.delete()
    cartaoponto.delete()
    contexto = {'contracheque': contracheque, 'contrachequeitens': contrachequeitens, 'cartaoponto': cartaoponto}
    return render(request, 'pagamentos/manutencao.html', contexto)
