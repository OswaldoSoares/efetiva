from django.http import JsonResponse
from django.template.loader import render_to_string

from .models import Orcamento
from clientes.models import TabelaVeiculo, TabelaPerimetro, Tabela
from website import facade


def create_orcamento_context():
    orcamento = get_orcamento_all()
    context = {'orcamento': orcamento}
    return context


def get_orcamento_all():
    """

    :return:
    """
    return Orcamento.objects.all()


def get_orcamento(idorcamento):
    """

    :return:
    """
    return Orcamento.objects.filter(idOrcamento=idorcamento)


def get_valor_veiculo(request):
    valor = 0
    idcliente = facade.get_tabela_padrao()
    idcliente = idcliente[0].Valor
    idcategoriaveiculo = request.GET.get('idCategoriaVeiculo')
    if idcategoriaveiculo:
        tabela = TabelaVeiculo.objects.filter(idCategoriaVeiculo=idcategoriaveiculo, idCliente=idcliente)
        if tabela:
            valor = tabela[0].SaidaCobra
    data = {'valor': valor}
    return JsonResponse(data)


def get_porcentagem_perimetro(request):
    porcentagem = 0
    idcliente = facade.get_tabela_padrao()
    idcliente = idcliente[0].Valor
    KMs = request.GET.get('KMs')
    tabela = TabelaPerimetro.objects.filter(idCliente=idcliente, PerimetroInicial__lte=KMs, PerimetroFinal__gte=KMs)
    if tabela:
        porcentagem = tabela[0].PerimetroCobra
    data = {'porcentagem': porcentagem}
    return JsonResponse(data)


def get_valor_ajudante(request):
    valor = 0
    idcliente = facade.get_tabela_padrao()
    idcliente = idcliente[0].Valor
    tabela = Tabela.objects.filter(idCliente=idcliente)
    if tabela:
        valor = tabela[0].AjudanteCobra
    data = {'valor': valor}
    return JsonResponse(data)


def form_orcamento(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    if c_idobj:
        c_instance = Orcamento.objects.get(idOrcamento=c_idobj)
    if request.method == 'POST':
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
    else:
        form = c_form(instance=c_instance)
    context = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view}
    data['html_form'] = render_to_string('orcamentos/formorcamentos.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_orcamento(request, c_idobj, c_url, c_view):
    data = dict()
    c_queryset = Orcamento.objects.get(idOrcamento=c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {'c_url': c_url, 'c_view': c_view, 'c_queryset': c_queryset}
    data['html_form'] = render_to_string('orcamentos/formorcamentos.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return