import pytest
from pagamentos.models import Recibo
from pessoas.models import Pessoal


def test_oi(client):
    response = client.get("/website/index.html")
    assert response.status_code == 200
    assert response.content == "OI MUNDO"


@pytest.mark.django_db
class TestRecibo:
    def test_recibo_create(self, client) -> None:
        assert Recibo.objects.count() == 0
        pessoa: Pessoal = Pessoal.objects.create(Nome="Oswaldo")
        response = client.post(
            "/pagamentos/criapagamento",
            {
                "Recibo": 1500,
                "DataRecibo": "13/04/2022",
                "ValorRecibo": "10.00",
                "StatusRecibo": "ABERTA",
                "DataPagamento": "01/01/2020",
                "Comentario": "Qualquer comentário",
                "idPessoal": pessoa.idPessoal,
            },
        )
        assert response.status_code == 200, response.data
        assert Recibo.objects.count() == 1
