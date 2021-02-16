from typing import List

from django.db.models import Max
from django.http import JsonResponse
from django.shortcuts import redirect
from django.template.loader import render_to_string

from clientes.models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca, Tabela, TabelaVeiculo, \
    TabelaPerimetro, TabelaCapacidade
# TODO IMPORTAR FROM FACADE VEICULOS
from veiculos.models import CategoriaVeiculo


def create_cliente_context(idcliente: int):
    """
    Create context queryset with all models Cliente
    :param idcliente:
    :return: dict with queryset
    """
    cliente = get_cliente(idcliente)
    fone_cliente = get_cliente_telefone(idcliente)
    email_cliente = get_cliente_email(idcliente)
    cobranca_cliente = get_cliente_cobranca(idcliente)
    tabela_cliente = get_cliente_tabela(idcliente)
    tabela_veiculo_cliente = get_cliente_tabela_veiculo(idcliente)
    tabela_perimetro_cliente = get_cliente_tabela_perimetro(idcliente)
    tabela_capacidade_cliente = get_cliente_tabela_capacidade(idcliente)
    list_categoria_cliente = list_categoria_tabela_veiculo_cliente(idcliente)
    context = {'cliente': cliente, 'fone_cliente': fone_cliente, 'email_cliente': email_cliente,
               'cobranca_cliente': cobranca_cliente, 'tabela_cliente': tabela_cliente,
               'tabela_veiculo_cliente': tabela_veiculo_cliente, 'tabela_perimetro_cliente': tabela_perimetro_cliente,
               'tabela_capacidade_cliente': tabela_capacidade_cliente, 'list_categoria_cliente': list_categoria_cliente}
    return context


def create_cliente_filter_context(request):
    meufiltrofantasia = request.GET.get('filtrofantasia', None)
    meufiltronome = request.GET.get('filtronome', None)
    cliente = get_cliente_all()
    if meufiltrofantasia:
        cliente = cliente.filter(Fantasia__icontains=meufiltrofantasia)
    elif meufiltronome:
        cliente = cliente.filter(Nome__icontains=meufiltronome)
    context = {'cliente': cliente}
    return context


def list_cliente_all() -> List[Cliente]:
    """
    List Clientes
    :return: List of Clientes
    """
    return list(Cliente.objects.all())


def get_cliente_all():
    """
    Get all Clientes in Models
    :return: queryset
    """
    return Cliente.objects.all()


def get_cliente(idcliente: int) -> Cliente:
    """
    Get the Cliente in Models
    :param idcliente:
    :return: queryset
    """
    cliente = Cliente.objects.filter(idCliente=idcliente)
    return cliente


def get_cliente_telefone(idcliente: int):
    """
    Get the FoneContatoCliente in models
    :param idcliente:
    :return: queryset
    """
    fonecontatocliente = FoneContatoCliente.objects.filter(idCliente=idcliente)
    return fonecontatocliente


def get_cliente_email(idcliente: int):
    """
    Get the EmailContatoCliente in models
    :param idcliente:
    :return: queryset
    """
    emailcontatocliente = EMailContatoCliente.objects.filter(idCliente=idcliente)
    return emailcontatocliente


def get_cliente_cobranca(idcliente: int):
    """
    Get the CobrancaCliente in models
    :param idcliente:
    :return: queryset
    """
    cobrancacliente = Cobranca.objects.filter(idCliente=idcliente)
    return cobrancacliente


def get_cliente_tabela(idcliente: int):
    """
    Get the Tabela in models
    :param idcliente:
    :return: queryset
    """
    tabela = Tabela.objects.filter(idCliente=idcliente)
    return tabela


def get_cliente_tabela_veiculo(idcliente: int):
    """
    Get the TabelaVeiculo in models
    :param idcliente:
    :return: queryset
    """
    tabelaveiculo = TabelaVeiculo.objects.filter(idCliente=idcliente)
    return tabelaveiculo


def get_cliente_tabela_perimetro(idcliente: int):
    """
    Get the TabelaPerimetro in models
    :param idcliente:
    :return: queryset
    """
    tabelaperimetro = TabelaPerimetro.objects.filter(idCliente=idcliente)
    return tabelaperimetro


def get_cliente_tabela_capacidade(idcliente: int):
    """
    Get the TabelaCapacidade in models
    :param idcliente:
    :return: queryset
    """
    tabelacapacidade = TabelaCapacidade.objects.filter(idCliente=idcliente)
    return tabelacapacidade


def list_categoria_tabela_veiculo_cliente(idcliente: int):
    """
    List Categoria of Veiculos registered
    :param idcliente:
    :return: list of Categorias
    """
    veiculos_categoria = get_cliente_tabela_veiculo(idcliente)
    veiculos_categoria_existe = [itens.idCategoriaVeiculo_id for itens in veiculos_categoria]
    return veiculos_categoria_existe


def get_categoria_veiculo():
    categoria_veiculo = CategoriaVeiculo.objects.all()
    return categoria_veiculo


def create_select_cliente():
    """
    Create a Select com id e fantasia
    :return:
    """
    return [('0', 'SELECIONE UM ITEM')] + [(i.idCliente, i.Fantasia) for i in get_cliente_all()]


def form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente):
    data = dict()
    c_instance = None
    if c_view == 'edita_cliente' or c_view == 'exclui_cliente':
        if c_idobj:
            c_instance = Cliente.objects.get(idCliente=c_idobj)
    elif c_view == 'cria_email_cliente' or c_view == 'edita_email_cliente':
        if c_idobj:
            c_instance = EMailContatoCliente.objects.get(idEmailContatoCliente=c_idobj)
    elif c_view == 'cria_fone_cliente' or c_view == 'edita_fone_cliente':
        if c_idobj:
            c_instance = FoneContatoCliente.objects.get(idFoneContatoCliente=c_idobj)
    elif c_view == 'cria_cobranca_cliente' or c_view == 'edita_cobranca_cliente':
        if c_idobj:
            c_instance = Cobranca.objects.get(idCobranca=c_idobj)
    elif c_view == 'cria_tabela_cliente' or c_view == 'edita_tabela_cliente':
        if c_idobj:
            c_instance = Tabela.objects.get(idTabela=c_idobj)
    elif c_view == 'cria_tabela_veiculo' or c_view == 'edita_tabela_veiculo':
        if c_idobj:
            c_instance = TabelaVeiculo.objects.get(idTabelaVeiculo=c_idobj)
    elif c_view == 'cria_tabela_capacidade' or c_view == 'edita_tabela_capacidade':
        if c_idobj:
            c_instance = TabelaCapacidade.objects.get(idTabelaCapacidade=c_idobj)
    elif c_view == 'cria_tabela_perimetro' or c_view == 'edita_tabela_perimetro':
        if c_idobj:
            c_instance = TabelaPerimetro.objects.get(idTabelaPerimetro=c_idobj)
    if request.method == 'POST':
        if c_view == 'edita_tabela_capacidade':
            request_copy = request.POST.copy()
            request_copy['CapacidadeFinal'] = c_instance.CapacidadeFinal
            form = c_form(request_copy, instance=c_instance)
        elif c_view == 'edita_tabela_perimetro':
            request_copy = request.POST.copy()
            request_copy['PerimetroFinal'] = c_instance.PerimetroFinal
            form = c_form(request_copy, instance=c_instance)
        else:
            form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            save_id = form.save()
            if c_view == 'cria_cliente' or c_view == 'edita_cliente':
                data['save_id'] = save_id.idCliente
            else:
                data['save_id'] = save_id.idCliente_id
        else:
            print(form)
    else:
        if c_view == 'cria_tabela_capacidade':
            peso = TabelaCapacidade.objects.filter(idCliente=idcliente).aggregate(peso=Max('CapacidadeFinal'))
            form = c_form(initial={'CapacidadeInicial': peso['peso']+1, 'CapacidadeFinal': peso['peso']+2})
        elif c_view == 'cria_tabela_perimetro':
            km = TabelaPerimetro.objects.filter(idCliente=idcliente).aggregate(km=Max('PerimetroFinal'))
            form = c_form(initial={'PerimetroInicial': km['km']+1, 'PerimetroFinal': km['km']+2})
        else:
            form = c_form(instance=c_instance)
    context = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view, 'idcliente': idcliente,
               'idcategoriaveiculo': request.GET.get('idcategoriaveiculo')}
    data['html_form'] = render_to_string('clientes/formcliente.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente):
    data = dict()
    c_queryset = None
    if c_view == 'exclui_cliente':
        c_queryset = Cliente.objects.get(idCliente=c_idobj)
    elif c_view == 'exclui_email_cliente':
        c_queryset = EMailContatoCliente.objects.get(idEmailContatoCliente=c_idobj)
    elif c_view == 'exclui_fone_cliente':
        c_queryset = FoneContatoCliente.objects.get(idFoneContatoCliente=c_idobj)
    elif c_view == 'exclui_cobranca_cliente':
        c_queryset = Cobranca.objects.get(idCobranca=c_idobj)
    elif c_view == 'exclui_tabela_capacidade':
        c_queryset = TabelaCapacidade.objects.get(idTabelaCapacidade=c_idobj)
    elif c_view == 'exclui_tabela_perimetro':
        c_queryset = TabelaPerimetro.objects.get(idTabelaPerimetro=c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {'c_url': c_url, 'c_view': c_view, 'c_queryset': c_queryset, 'idcliente': idcliente}
    data['html_form'] = render_to_string('clientes/formcliente.html', context, request=request)
    data['c_view'] = c_view
    data['save_id'] = idcliente
    c_return = JsonResponse(data)
    return c_return


def phkesc(switchdict):
    phkesc = {'porcentagem-cobra': '0', 'hora-cobra': '0', 'kilometragem-cobra': '0', 'entrega-cobra': '0',
              'saida-cobra': '0', 'capacidade-cobra': '0', 'entregakg-cobra': '0', 'entregavolume-cobra': '0',
              'porcentagem-paga': '0', 'hora-paga': '0', 'kilometragem-paga': '0', 'entrega-paga': '0',
              'saida-paga': '0', 'capacidade-paga': '0', 'entregakg-paga': '0', 'entregavolume-paga': '0'}
    for itens in phkesc:
        if itens in switchdict['switch']:
            phkesc[itens] = '1'
    valor_phkesc = ''
    for itens in phkesc:
        valor_phkesc += phkesc[itens]
    phkesc_cobra = valor_phkesc[0:8]
    phkesc_paga = valor_phkesc[8:16]
    return phkesc_cobra, phkesc_paga


def save_phkesc(idtabelacliente, phkesc_cobra, phkesc_paga):
    tabela = Tabela.objects.get(idTabela=idtabelacliente)
    obj = Tabela()
    obj.idTabela = tabela.idTabela
    obj.Comissao = tabela.Comissao
    obj.TaxaExpedicao = tabela.TaxaExpedicao
    obj.AjudanteCobra = tabela.AjudanteCobra
    obj.AjudantePaga = tabela.AjudantePaga
    obj.phkescCobra = phkesc_cobra
    obj.phkescPaga = phkesc_paga
    obj.idFormaPagamento = tabela.idFormaPagamento
    obj.idCliente = tabela.idCliente
    obj.save()
    c_return = redirect('consultacliente', tabela.idCliente_id)
    return c_return
