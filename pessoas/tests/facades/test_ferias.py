""" Testes do módulo ferias.py """
import pytest
from decimal import Decimal
from datetime import date

from pessoas.facades.ferias import (
    calcular_dias_ferias_proporcionais,
    meses_proporcionais_ferias,
    calcula_valores_ferias,
)


@pytest.mark.parametrize(
    "faltas, dozeavos, esperado",
    [
        (0, 12, 30.0),  # até 5 faltas = 2.5 * 12
        (5, 12, 30.0),
        (6, 12, 24.0),  # 6 a 14 faltas = 2.0 * 12
        (14, 12, 24.0),
        (15, 12, 18.0),  # 15 a 23 faltas = 1.5 * 12
        (23, 12, 18.0),
        (24, 12, 12.0),  # 24 a 32 faltas = 1.0 * 12
        (32, 12, 12.0),
        (33, 12, 0.0),  # acima de 32 faltas = 0
    ],
)
def test_calcular_dias_ferias_proporcionais(faltas, dozeavos, esperado):
    resultado = calcular_dias_ferias_proporcionais(faltas, dozeavos)
    assert resultado == esperado


def test_meses_proporcionais_com_15_dias():
    data_inicio = date(2024, 1, 1)
    data_final = date(2024, 2, 15)
    resultado = meses_proporcionais_ferias(data_inicio, data_final)
    assert resultado == 2  # 1 mês completo + 15 dias → conta como 2


def test_meses_proporcionais_menos_de_15_dias():
    data_inicio = date(2024, 1, 1)
    data_final = date(2024, 2, 14)
    resultado = meses_proporcionais_ferias(data_inicio, data_final)
    assert resultado == 1


def test_calcula_valores_ferias():
    salario = Decimal("3000.00")
    faltas = 5
    data_inicio = date(2024, 1, 1)
    data_final = date(2024, 12, 31)

    dias, valor, um_terco, total = calcula_valores_ferias(
        salario, faltas, data_inicio, data_final
    )

    assert dias == Decimal("30.0")
    assert valor == Decimal("3000.00")
    assert um_terco == Decimal("1000.00")
    assert total == Decimal("4000.00")
