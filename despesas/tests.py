import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from despesas.forms import ID_PROPRIETARIO_FROTA, CadastraAbastecimento
from despesas.models import Abastecimento
from pessoas.models import Pessoal
from veiculos.models import CategoriaVeiculo, Veiculo


@pytest.fixture
def veiculo():
    proprietario = Pessoal.objects.create(
        idPessoal=ID_PROPRIETARIO_FROTA, Nome="TRANSEFETIVA"
    )
    categoria = CategoriaVeiculo.objects.create(Categoria="VUC")
    return Veiculo.objects.create(
        Marca="VW",
        Modelo="DELIVERY",
        Placa="ABC1D23",
        Capacidade=0,
        MedidaAltura=0,
        MedidaComprimento=0,
        MedidaLargura=0,
        Proprietario=proprietario,
        Motorista=proprietario,
        Categoria=categoria,
    )


@pytest.fixture
def client_logado(client):
    User.objects.create_superuser(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")
    return client


@pytest.fixture
def dados(veiculo):
    return {
        "DataAbastecimento": datetime.date.today().strftime("%Y-%m-%d"),
        "idVeiculo": veiculo.pk,
        "TipoCombustivel": "DIESEL",
        "LitrosAbastecidos": "45.70",
        "ValorCombustivel": "6.199",
        "ValorAbastecido": "283.29",
    }


@pytest.mark.django_db
def test_form_abastecimento_valido(dados):
    assert CadastraAbastecimento(data=dados).is_valid()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "campo, valor",
    [
        ("DataAbastecimento", "2999-01-01"),
        ("LitrosAbastecidos", "0"),
        ("ValorCombustivel", "-1"),
        ("ValorAbastecido", "999.00"),
        ("TipoCombustivel", "QUEROSENE"),
    ],
)
def test_form_abastecimento_invalido(dados, campo, valor):
    dados[campo] = valor
    form = CadastraAbastecimento(data=dados)
    assert not form.is_valid()
    assert campo in form.errors


@pytest.mark.django_db
def test_form_abastecimento_rejeita_veiculo_de_terceiro(dados, veiculo):
    terceiro = Pessoal.objects.create(Nome="TERCEIRO")
    veiculo.Proprietario = terceiro
    veiculo.save()
    form = CadastraAbastecimento(data=dados)
    assert "idVeiculo" in form.errors


@pytest.mark.django_db
def test_get_abastecimento_form_retorna_modal(client_logado):
    response = client_logado.get(reverse("abastecimento_form"))
    assert response.status_code == 200
    assert "LitrosAbastecidos" in response.json()["modal_html"]


@pytest.mark.django_db
def test_post_abastecimento_valido_salva(client_logado, dados):
    response = client_logado.post(reverse("abastecimento_form"), dados)
    data = response.json()
    assert Abastecimento.objects.count() == 1
    assert Abastecimento.objects.get().LitrosAbastecidos == Decimal("45.70")
    assert "ABC1D23" in data["html-card-abastecimento"]
    assert data["tipo"] == "success"


@pytest.mark.django_db
def test_post_abastecimento_invalido_retorna_erros(client_logado, dados):
    dados["LitrosAbastecidos"] = "0"
    response = client_logado.post(reverse("abastecimento_form"), dados)
    assert Abastecimento.objects.count() == 0
    assert "errorlist" in response.json()["html_form"]


@pytest.mark.django_db
def test_post_abastecimento_altera_existente(client_logado, dados):
    client_logado.post(reverse("abastecimento_form"), dados)
    abastecimento = Abastecimento.objects.get()
    dados.update(
        id_abastecimento=abastecimento.pk,
        LitrosAbastecidos="50.00",
        ValorAbastecido="309.95",
    )
    client_logado.post(reverse("abastecimento_form"), dados)
    abastecimento.refresh_from_db()
    assert Abastecimento.objects.count() == 1
    assert abastecimento.LitrosAbastecidos == Decimal("50.00")


@pytest.mark.django_db
def test_excluir_abastecimento(client_logado, dados):
    client_logado.post(reverse("abastecimento_form"), dados)
    abastecimento = Abastecimento.objects.get()
    url = reverse("abastecimento_excluir")
    assert client_logado.get(url).status_code == 405
    client_logado.post(url, {"id_abastecimento": abastecimento.pk})
    assert Abastecimento.objects.count() == 0


@pytest.mark.django_db
def test_abastecimento_exige_permissao(client, dados):
    User.objects.create_user(username="comum", password="testpassword")
    client.login(username="comum", password="testpassword")
    response = client.post(reverse("abastecimento_form"), dados)
    assert response.status_code == 403
    assert Abastecimento.objects.count() == 0


@pytest.mark.django_db
def test_index_exibe_somente_abastecimento(client_logado):
    response = client_logado.get(reverse("index_despesas"))
    html = response.content.decode()
    assert response.status_code == 200
    assert "card-abastecimento" in html
    assert "csrfmiddlewaretoken" in html
    assert "card-multas" not in html
    assert "card-despesas" not in html
