"""
Este módulo contém filtros personalizados para uso com o sistema de
templates do Django.

Os filtros ajudam a manipular e exibir dados em templates de forma
personalizada.
"""
from django import template

register = template.Library()


@register.filter(name="default_if_zero")
def default_if_zero(valor, digitos_decimais=2):
    """
    Formata um valor numérico, retornando um número formatado com um
    número específico de casas decimais.

    Se o valor for None ou uma string vazia, retorna '0' formatado com
    o número de casas decimais especificado.
    Caso contrário, retorna o valor original, que deve ser um número ou
    uma string que representa um número.

    Args:
        valor (float or str): O valor a ser formatado. Pode ser um número
                              ou uma string.
        digitos_decimais (int, opcional): Número de casas decimais a ser
                                          exibido. O padrão é 2.

    Returns:
        str: O valor formatado com o número especificado de casas decimais,
        ou o valor original se não for None ou vazio.
    """
    if valor in (None, ""):
        return f"{0:.{digitos_decimais}f}"
    else:
        return valor
