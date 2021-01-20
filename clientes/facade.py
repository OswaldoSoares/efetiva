from typing import List
from clientes.models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca

def list_cliente_all() -> List[Cliente]:
    """
    List Clientes
    :return: List of Clientes
    """
    return list(Cliente.objects.all())


def get_cliente_idcliente(idcliente: int) -> Cliente:
    """
    Get the Cliente in Models
    :param idcliente:
    :return: queryset
    """
    cliente = Cliente.objects.filter(idCliente=idcliente)
    fonecontatocliente = FoneContatoCliente.objects.filter(idCliente=idcliente)
    emailcontatocliente = EMailContatoCliente.objects.filter(idCliente=idcliente)
    cobrancacliente = Cobranca.objects.filter(idCliente=idcliente)
    return cliente, fonecontatocliente, emailcontatocliente, cobrancacliente
