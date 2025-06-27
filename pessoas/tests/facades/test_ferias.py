""" Testes do módulo ferias.py """
import pytest
from decimal import Decimal
from datetime import date

from pessoas.facades.ferias import (
    calcular_dias_ferias_proporcionais,
    meses_proporcionais_ferias,
    calcula_valores_ferias,
)
