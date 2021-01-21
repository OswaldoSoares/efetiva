from typing import List
from clientes.models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca, Tabela, TabelaVeiculo, \
    TabelaPerimetro, TabelaCapacidade
# TODO EXPORTAR FROM FACADE VEICULOS
from veiculos.models import CategoriaVeiculo


def create_cliente_context(idcliente: int):
    """
    
    :param idcliente: 
    :return: 
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


def list_cliente_all() -> List[Cliente]:
    """
    List Clientes
    :return: List of Clientes
    """
    return list(Cliente.objects.all())


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

    :param idcliente:
    :return:
    """
    veiculos_categoria = get_cliente_tabela_veiculo(idcliente)
    veiculos_categoria_existe = [itens.idCategoriaVeiculo_id for itens in veiculos_categoria]
    return veiculos_categoria_existe


def get_categoria_veiculo():
    categoria_veiculo = CategoriaVeiculo.objects.all()
    return categoria_veiculo