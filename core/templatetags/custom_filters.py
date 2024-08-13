"""
Este módulo contém filtros personalizados para uso com o sistema de
templates do Django.

Os filtros ajudam a manipular e exibir dados em templates de forma
personalizada.
"""
from django import template

register = template.Library()


@register.filter(name="default_if_zero")
def default_if_zero(value, arg):
    """
    Retorna um valor padrão se o valor fornecido for zero.

    Este filtro é utilizado em templates para exibir um valor alternativo
    quando o valor original é zero.

    Args:
        value (int or float): O valor a ser verificado.
        arg (any): O valor a ser retornado se o valor for zero.

    Returns:
        any: O valor original se não for zero, caso contrário, o valor
        padrão fornecido.
    """
    return arg if value == 0 else value
