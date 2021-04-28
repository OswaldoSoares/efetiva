from django.http import JsonResponse
from django.template.loader import render_to_string

from pessoas import facade
from pessoas.models import ContraCheque


meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO',
         'NOVEMBRO', 'DEZEMBRO']


def create_context(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    folha = {}
    referencia = {'MesReferencia': mesreferencia, 'AnoReferencia': anoreferencia}
    totalfolha = 0.00
    for itens in mensalistas:
        folha[itens.Nome] = {'Salario': '0,00', 'Liquido': '0,00', 'ContraCheque': False, 'CartaoPonto': False}
        salario = facade.get_salario(itens.idPessoal)
        folha[itens.Nome]['Salario'] = salario[0].Salario
        contracheque = facade.get_contrachequereferencia(mesreferencia, anoreferencia, itens.idPessoal)
        if contracheque:
            totais = facade.saldo_contracheque(contracheque[0].idContraCheque)
            folha[itens.Nome]['Liquido'] = totais['Liquido']
            totalfolha += float(totais['Liquido'])
        if facade.busca_contracheque(meses[int(mesreferencia)-1], anoreferencia, itens.idPessoal):
            folha[itens.Nome]['ContraCheque'] = True
        if facade.busca_cartaoponto_referencia(mesreferencia, anoreferencia, itens.idPessoal):
            folha[itens.Nome]['CartaoPonto'] = True
    totalfolha = '{0:.2f}'.format(totalfolha).replace('.', ',')
    contexto = {'folha': folha, 'referencia': referencia, 'totalfolha': totalfolha}
    return contexto


def context_contracheque():
    formcontracheque = facade.CadastraContraCheque()
    contexto = {'formcontracheque': formcontracheque}
    return contexto


def create_folha(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    for itens in mensalistas:
        facade.create_contracheque(mesreferencia, anoreferencia, '0.00', itens.idPessoal)
        facade.create_cartaoponto(mesreferencia, anoreferencia, itens.idPessoal)


def lista_mensaalista_ativos():
    return facade.get_pessoal_mensalista_ativo()


def seleciona_folha(request, mesreferencia, anoreferencia):
    data = dict()
    contexto = create_context(mesreferencia, anoreferencia)
    data['html_folha'] = render_to_string('pagamentos/folhapgto.html', contexto, request=request)
    c_return = JsonResponse(data)
    return c_return
