import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from despesas.facades import abastecimento
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


def test_somar_meses_vira_o_ano():
    assert abastecimento.somar_meses(datetime.date(2026, 12, 1), 1) == (
        datetime.date(2027, 1, 1)
    )
    assert abastecimento.somar_meses(datetime.date(2026, 1, 1), -1) == (
        datetime.date(2025, 12, 1)
    )


def test_obter_mes_invalido_usa_mes_atual():
    assert abastecimento.obter_mes("xx") == datetime.date.today().replace(
        day=1
    )


@pytest.mark.django_db
def test_abastecimento_mes_filtra_pelo_mes(client_logado, dados):
    client_logado.post(reverse("abastecimento_form"), dados)
    mes_atual = datetime.date.today().strftime("%Y-%m")
    url = reverse("abastecimento_mes")

    html = client_logado.get(url, {"mes": mes_atual}).json()[
        "html-card-abastecimento"
    ]
    assert "ABC1D23" in html

    html = client_logado.get(url, {"mes": "2020-01"}).json()[
        "html-card-abastecimento"
    ]
    assert "ABC1D23" not in html
    assert "Nenhum abastecimento" in html


@pytest.mark.django_db
def test_salvar_mostra_mes_do_abastecimento(client_logado, dados):
    dados["DataAbastecimento"] = "2025-03-10"
    response = client_logado.post(reverse("abastecimento_form"), dados)
    html = response.json()["html-card-abastecimento"]
    assert "ABC1D23" in html
    assert "2025-02" in html  # mês anterior na navegação


@pytest.mark.django_db
def test_resumo_mes_a_mes_e_por_placa(veiculo):
    outro = Veiculo.objects.create(
        Marca="VW",
        Modelo="CONSTELLATION",
        Placa="XYZ9K87",
        Capacidade=0,
        MedidaAltura=0,
        MedidaComprimento=0,
        MedidaLargura=0,
        Proprietario=veiculo.Proprietario,
        Motorista=veiculo.Motorista,
        Categoria=veiculo.Categoria,
    )

    def lanca(data, carro, litros, valor):
        Abastecimento.objects.create(
            DataAbastecimento=data,
            idVeiculo=carro,
            TipoCombustivel="DIESEL",
            LitrosAbastecidos=Decimal(litros),
            ValorCombustivel=Decimal("6.000"),
            ValorAbastecido=Decimal(valor),
        )

    lanca(datetime.date(2026, 9, 5), veiculo, "10.00", "60.00")
    lanca(datetime.date(2026, 9, 20), veiculo, "20.00", "120.00")
    lanca(datetime.date(2026, 9, 21), outro, "50.00", "300.00")
    lanca(datetime.date(2026, 8, 1), veiculo, "5.00", "30.00")

    contexto = abastecimento.create_contexto_resumo_abastecimento(
        datetime.date(2026, 9, 1)
    )
    meses = contexto["resumo_meses"]
    assert len(meses) == 12
    assert meses[0]["mes"] == datetime.date(2026, 9, 1)
    assert meses[0]["valor"] == Decimal("480.00")
    assert meses[0]["quantidade"] == 3
    assert meses[0]["percentual"] == 100
    assert meses[1]["valor"] == Decimal("30.00")
    assert meses[2]["quantidade"] == 0 and meses[2]["media"] is None

    placas = contexto["resumo_placas"]
    assert [p["placa"] for p in placas] == ["XYZ9K87", "ABC1D23"]
    assert placas[1]["valor"] == Decimal("180.00")
    assert placas[1]["litros"] == Decimal("30.00")
    assert placas[1]["media"] == Decimal("6")
    assert placas[1]["percentual"] == 60


    graficos = contexto["graficos_abastecimento"]
    assert len(graficos) == 12
    assert graficos[-1] == {
        "rotulo": "Set/26",
        "mes": "2026-09",
        "valor": 480.0,
        "media": 6.0,
        "ativo": True,
    }
    assert graficos[-3]["media"] is None


@pytest.mark.django_db
def test_index_exibe_resumo_e_graficos(client_logado):
    html = client_logado.get(reverse("index_despesas")).content.decode()
    assert "card-abastecimento-resumo" in html
    assert "Mês a mês" in html
    assert 'id="dados-graficos-abastecimento"' in html
    assert "chart.umd.min.js" in html


@pytest.mark.django_db
def test_form_aceita_data_brasileira(dados):
    dados["DataAbastecimento"] = datetime.date.today().strftime("%d/%m/%Y")
    form = CadastraAbastecimento(data=dados)
    assert form.is_valid(), form.errors
    assert 'value="' + dados["DataAbastecimento"] + '"' in str(
        CadastraAbastecimento()["DataAbastecimento"]
    )


@pytest.mark.django_db
def test_pdf_abastecimento(client_logado, dados):
    client_logado.post(reverse("abastecimento_form"), dados)
    mes = datetime.date.today().strftime("%Y-%m")
    response = client_logado.get(reverse("abastecimento_pdf"), {"mes": mes})
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response.content.startswith(b"%PDF")
    assert f"ABASTECIMENTOS {mes}.pdf" in response["Content-Disposition"]


@pytest.mark.django_db
def test_pdf_abastecimento_mes_vazio(client_logado):
    response = client_logado.get(reverse("abastecimento_pdf"), {"mes": "2020-01"})
    assert response.status_code == 200
    assert response.content.startswith(b"%PDF")
