"""
Tests do modulo facade.py do app pessoas
"""
from dateutil.relativedelta import relativedelta
import pytest
from pessoas.models import Pessoal


@pytest.mark.django_db
def test_primeiro_aquisitivo(gera_aquisitivo):
    """
        Test: Se existe o primeiro aquisitivo do colaborador,
        a data inicial do aquisitibo tem que ser a mesma da
        admissão do colabotador e a data final tem que ser
        ao completar um ano.
    Args:
        gera_aquisitivo:

    """
    aquisitivo, colaborador = gera_aquisitivo
    data_completa_um_ano = colaborador.DataAdmissao + relativedelta(
        years=+1, days=-1
    )
    assert aquisitivo.DataInicial == colaborador.DataAdmissao
    assert aquisitivo.DataFinal == data_completa_um_ano
    assert aquisitivo.idPessoal == colaborador


@pytest.mark.django_db
def test_aquisitivo_colaborador_admitido_mais_de_um_ano(
    gera_varios_aquisitivos,
):
    """
        Test:
    Args:
        gera_aquisitivo:

    """
    aquisitivo, colaborador = gera_varios_aquisitivos
    assert colaborador
    assert len(aquisitivo) > 1


@pytest.mark.django_db
def test_inexistente_aquisitivo_para_colaborador_no_banco_de_dados(
    busca_aquisitivo,
):
    """
        Test: Verifica se existe aquisitivo para o colaborador
        selecionado no banco de dados.
    Args:
        busca_aquisitivo:

    """
    aquisitivo = busca_aquisitivo
    assert not aquisitivo
