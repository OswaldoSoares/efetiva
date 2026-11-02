import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from despesas.facades import abastecimento, consumo
from despesas.forms import CadastraAbastecimento
from clientes.models import Cliente
from despesas.models import Abastecimento
from minutas.models import Minuta
from pessoas.models import Pessoal
from veiculos.models import CategoriaVeiculo, Veiculo


@pytest.fixture
def veiculo():
    proprietario = Pessoal.objects.create(Nome="TRANSEFETIVA")
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
        ("ValorAbastecido", "0"),
        ("TipoCombustivel", "QUEROSENE"),
    ],
)
def test_form_abastecimento_invalido(dados, campo, valor):
    dados[campo] = valor
    form = CadastraAbastecimento(data=dados)
    assert not form.is_valid()
    assert campo in form.errors


@pytest.mark.django_db
def test_form_abastecimento_litros_nao_conferem_com_valor(dados):
    dados["ValorAbastecido"] = "999.00"
    form = CadastraAbastecimento(data=dados)
    assert not form.is_valid()
    assert "LitrosAbastecidos" in form.errors


@pytest.mark.django_db
def test_form_abastecimento_ordem_dos_campos():
    assert list(CadastraAbastecimento().fields)[3:] == [
        "ValorAbastecido",
        "ValorCombustivel",
        "LitrosAbastecidos",
    ]


@pytest.mark.django_db
def test_form_abastecimento_aceita_veiculo_de_agregado(dados, veiculo):
    agregado = Pessoal.objects.create(Nome="AGREGADO")
    veiculo.Proprietario = agregado
    veiculo.save()
    assert CadastraAbastecimento(data=dados).is_valid()


@pytest.mark.django_db
def test_form_abastecimento_rejeita_veiculo_inativo(dados, veiculo):
    veiculo.Ativo = False
    veiculo.save()
    form = CadastraAbastecimento(data=dados)
    assert "idVeiculo" in form.errors


@pytest.mark.django_db
def test_form_abastecimento_edicao_mantem_veiculo_inativo(dados, veiculo):
    registro = CadastraAbastecimento(data=dados).save()
    veiculo.Ativo = False
    veiculo.save()
    form = CadastraAbastecimento(data=dados, instance=registro)
    assert form.is_valid()


@pytest.mark.django_db
def test_get_abastecimento_form_retorna_modal(client_logado):
    response = client_logado.get(reverse("abastecimento_form"))
    assert response.status_code == 200
    assert "LitrosAbastecidos" in response.json()["modal_html"]


@pytest.mark.django_db
def test_ultimos_precos_combustivel(veiculo):
    for data, tipo, preco in [
        (datetime.date(2026, 9, 1), "DIESEL", "5.990"),
        (datetime.date(2026, 10, 1), "DIESEL", "6.190"),
        (datetime.date(2026, 9, 15), "ARLA", "3.500"),
    ]:
        Abastecimento.objects.create(
            DataAbastecimento=data,
            idVeiculo=veiculo,
            TipoCombustivel=tipo,
            LitrosAbastecidos=Decimal("10"),
            ValorCombustivel=Decimal(preco),
            ValorAbastecido=Decimal(preco) * 10,
        )
    assert abastecimento.ultimos_precos_combustivel() == {
        "DIESEL": "6.190",
        "ARLA": "3.500",
    }


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
        "consumo": None,
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
    campo = str(CadastraAbastecimento()["DataAbastecimento"])
    assert 'type="date"' in campo
    assert 'value="' + datetime.date.today().isoformat() + '"' in campo


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


def _minuta(veiculo, data, km_inicial, km_final, status="FATURADA"):
    cliente, _ = Cliente.objects.get_or_create(Fantasia="CLIENTE", Nome="CLIENTE")
    return Minuta.objects.create(
        Minuta=Minuta.objects.count() + 1,
        DataMinuta=data,
        KMInicial=km_inicial,
        KMFinal=km_final,
        StatusMinuta=status,
        idCliente=cliente,
        idVeiculo=veiculo,
    )


@pytest.mark.django_db
def test_km_rodados_soma_percurso_e_descarta_erros(veiculo):
    setembro = datetime.date(2026, 9, 1)
    _minuta(veiculo, datetime.date(2026, 9, 2), 998100, 998200)
    _minuta(veiculo, datetime.date(2026, 9, 3), 998200, 998350)
    # km absoluto de outra sequência: o percurso continua válido
    _minuta(veiculo, datetime.date(2026, 9, 4), 104783, 104833)
    _minuta(veiculo, datetime.date(2026, 9, 5), 998350, 309494)  # erro
    _minuta(veiculo, datetime.date(2026, 9, 6), 998350, 998400, "CANCELADA")
    _minuta(veiculo, datetime.date(2026, 10, 1), 998400, 998500)  # outro mês

    km = consumo.km_rodados_por_veiculo_mes(setembro, datetime.date(2026, 10, 1))
    assert dict(km) == {(veiculo.pk, setembro): {"km": 300, "descartadas": 1}}


def test_calcular_consumo():
    assert consumo.calcular_consumo(250, Decimal("25")) == (10.0, False)
    assert consumo.calcular_consumo(0, Decimal("25")) == (None, False)
    assert consumo.calcular_consumo(250, 0) == (None, False)
    assert consumo.calcular_consumo(2500, Decimal("25"))[1] is True


@pytest.mark.django_db
def test_resumo_inclui_consumo_por_placa_e_frota(veiculo):
    sem_minuta = Veiculo.objects.create(
        Marca="VW",
        Modelo="DELIVERY",
        Placa="SEM0M00",
        Capacidade=0,
        MedidaAltura=0,
        MedidaComprimento=0,
        MedidaLargura=0,
        Proprietario=veiculo.Proprietario,
        Motorista=veiculo.Motorista,
        Categoria=veiculo.Categoria,
    )
    for carro, litros in ((veiculo, "25.00"), (sem_minuta, "50.00")):
        Abastecimento.objects.create(
            DataAbastecimento=datetime.date(2026, 9, 10),
            idVeiculo=carro,
            TipoCombustivel="DIESEL",
            LitrosAbastecidos=Decimal(litros),
            ValorCombustivel=Decimal("6.000"),
            ValorAbastecido=Decimal(litros) * 6,
        )
    _minuta(veiculo, datetime.date(2026, 9, 2), 1000, 1100)
    _minuta(veiculo, datetime.date(2026, 9, 20), 1100, 1250)

    contexto = abastecimento.create_contexto_resumo_abastecimento(
        datetime.date(2026, 9, 1)
    )
    placas = {p["placa"]: p for p in contexto["resumo_placas"]}
    assert placas["ABC1D23"]["km"] == 250
    assert placas["ABC1D23"]["consumo"] == 10.0
    assert placas["SEM0M00"]["consumo"] is None
    # veículo sem minuta não entra no consumo da frota
    assert contexto["resumo_meses"][0]["consumo"] == 10.0
    assert contexto["graficos_abastecimento"][-1]["consumo"] == 10.0


@pytest.mark.django_db
def test_resumo_exibe_km_e_consumo(client_logado, dados, veiculo):
    client_logado.post(reverse("abastecimento_form"), dados)
    hoje = datetime.date.today()
    _minuta(veiculo, hoje, 5000, 5457)
    _minuta(veiculo, hoje, 5457, 99999)  # descartada
    data = client_logado.get(
        reverse("abastecimento_mes"), {"mes": hoje.strftime("%Y-%m")}
    ).json()
    html = data["html-card-abastecimento-resumo"]
    assert "457" in html  # km
    assert "10,00" in html  # 457 km / 45,70 L
    assert "1 minuta com km inválido ignorada" in html
    pdf = client_logado.get(
        reverse("abastecimento_pdf"), {"mes": hoje.strftime("%Y-%m")}
    )
    assert pdf.content.startswith(b"%PDF")
