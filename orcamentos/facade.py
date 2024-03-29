from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
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
    kms = request.GET.get('KMs')
    tabela = TabelaPerimetro.objects.filter(idCliente=idcliente, PerimetroInicial__lte=kms, PerimetroFinal__gte=kms)
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


def get_valor_taxa_expedicao(request):
    valor = 0
    formapgto = ''
    idcliente = facade.get_tabela_padrao()
    idcliente = idcliente[0].Valor
    tabela = Tabela.objects.filter(idCliente=idcliente)
    if tabela:
        valor = tabela[0].TaxaExpedicao
        formapgto = tabela[0].idFormaPagamento_id
    data = {'valor': valor, 'formapgto': formapgto}
    return JsonResponse(data)


def altera_status_orcamento(novo_status, idorcamento):
    orcamento = Orcamento.objects.get(idOrcamento=idorcamento)
    orcamento.StatusOrcamento = novo_status
    orcamento.save(update_fields=['StatusOrcamento'])
    return True


def create_email(idorcamento):
    orcamento = get_orcamento(idorcamento)
    perimetro = round(orcamento[0].ValorTabela * orcamento[0].Perimetro / 100, 2)
    contexto = {'orcamento': orcamento, 'perimetro': perimetro}
    subject = 'Orçamento'
    html_message = render_to_string('orcamentos/emailorcamento.html', contexto)
    from_email = 'Transefetiva Transportes <operacional.efetiva@terra.com.br>'
    to = [orcamento[0].Email, 'ml.efetiva@terra.com.br']
    email = EmailMessage(subject, html_message, from_email, to)
    email.content_subtype = 'html'
    if email.send():
        altera_status_orcamento('ENVIADO', idorcamento)
    data = redirect('indexorcamento')
    return data


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
