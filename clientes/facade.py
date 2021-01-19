from typing import List
from clientes.models import Cliente

def list_cliente_all() -> List[Cliente]:
    """
    List Clientes
    :return: List of Clientes
    """
    return list(Cliente.objects.all())


def get_cliente_idcliente(idcliente: int) -> Cliente:
    """

    :param idcliente:
    :return:
    """
    return Cliente.objects.get(idCliente=idcliente)
