"""
"""
import pytest
from pessoas.models import Pessoal


@pytest.mark.django_db
def test_altera_status():
    """ """
    colaborador = Pessoal.objects.create(StatusPessoal=True)
    colaborador.StatusPessoal ^= True
    colaborador.save()
    colaborador.refresh_from_db()
    assert colaborador.StatusPessoal is False
    colaborador.StatusPessoal ^= True
    colaborador.save()
    colaborador.refresh_from_db()
    assert colaborador.StatusPessoal is True
