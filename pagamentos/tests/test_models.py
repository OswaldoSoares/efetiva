"""
    Testes models do app pagamentos
"""
import pytest
from pagamentos.models import Recibo
from pessoas.models import Pessoal


@pytest.mark.django_db
def test_recibo_create():
    """
    Testa inclusão de um novo registro no db recibo
    """
    pessoa = Pessoal.objects.create(Nome="Oswaldo")
    Recibo.objects.create(
        Recibo=1500,
        DataRecibo="2023-10-06",
        ValorRecibo="10.00",
        StatusRecibo="ABERTA",
        DataPagamento="2023-10-06",
        Comentario="Qualquer comentário",
        idPessoal=pessoa,
    )
