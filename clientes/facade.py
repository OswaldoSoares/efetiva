from typing import List

from django.http import JsonResponse
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
    cliente = qet_cliente_all()
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


def qet_cliente_all():
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


def form_cliente(request, c_form, idcliente, c_view):
    cliente = None
    data = dict()
    if idcliente:
        cliente = Cliente.objects.get(idCliente=idcliente)
    if request.method == 'POST':
        if idcliente:
            form = c_form(request.POST, instance=cliente)
        else:
            form = c_form(request.POST or None)
        if form.is_valid():
            save_id = form.save()
            data['save_id'] = save_id.idCliente
    else:
        if idcliente:
            form = c_form(instance=cliente)
        else:
            form = c_form()
    context = {'form': form, 'c_url': request.get_full_path(), 'idcliente': idcliente, 'c_view': c_view}
    data['html_form'] = render_to_string('clientes/formcliente.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_cliente(request, idcliente, c_view):
    data = dict()
    cliente = Cliente.objects.get(idCliente=idcliente)
    if request.method == "POST":
        cliente.delete()
    context = {'c_url': request.get_full_path(), 'idcliente': idcliente, 'c_view': c_view, 'cliente': cliente}
    data['html_form'] = render_to_string('clientes/formcliente.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return
