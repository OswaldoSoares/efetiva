import datetime
from decimal import Decimal

import pytest
from django.contrib.auth.models import User
from django.urls import reverse

from despesas.models import Abastecimento
from pessoas.models import Pessoal
from veiculos.forms import CadastraVeiculo
from veiculos.models import CategoriaVeiculo, Veiculo


@pytest.fixture
def pessoa():
    return Pessoal.objects.create(Nome="TRANSEFETIVA")


@pytest.fixture
def categoria():
    return CategoriaVeiculo.objects.create(Categoria="VUC")


@pytest.fixture
def veiculo(pessoa, categoria):
    return Veiculo.objects.create(
        Marca="VW",
        Modelo="DELIVERY",
        Placa="ABC1D23",
        Capacidade=0,
        MedidaAltura=Decimal("2"),
        MedidaComprimento=Decimal("4"),
        MedidaLargura=Decimal("2.5"),
        Proprietario=pessoa,
        Motorista=pessoa,
        Categoria=categoria,
    )


@pytest.fixture
def client_logado(client):
    User.objects.create_superuser(username="testuser", password="testpassword")
    client.login(username="testuser", password="testpassword")
    return client


@pytest.fixture
def dados(pessoa, categoria):
    return {
        "Placa": "xyz-9a87",
        "Categoria": categoria.pk,
        "Marca": "Fiat",
        "Modelo": "Fiorino",
        "Proprietario": pessoa.pk,
        "Motorista": pessoa.pk,
    }


@pytest.mark.django_db
def test_form_veiculo_normaliza_placa_e_zera_medidas(dados):
    form = CadastraVeiculo(data=dados)
    assert form.is_valid(), form.errors
    veiculo = form.save()
    assert veiculo.Placa == "XYZ9A87"
    assert veiculo.Capacidade == 0
    assert veiculo.MedidaLargura == 0
    assert veiculo.Ativo


@pytest.mark.django_db
@pytest.mark.parametrize("placa", ["AB1234", "ABCD123", "1234ABC"])
def test_form_veiculo_rejeita_placa_invalida(dados, placa):
    dados["Placa"] = placa
    assert "Placa" in CadastraVeiculo(data=dados).errors


@pytest.mark.django_db
def test_form_veiculo_rejeita_placa_duplicada_gravada_com_espaco(
    dados, veiculo
):
    veiculo.Placa = "XYZ 9A87"
    veiculo.save()
    assert "Placa" in CadastraVeiculo(data=dados).errors


@pytest.mark.django_db
def test_form_veiculo_edicao_aceita_a_propria_placa(dados, veiculo):
    dados["Placa"] = veiculo.Placa
    assert CadastraVeiculo(data=dados, instance=veiculo).is_valid()


@pytest.mark.django_db
def test_form_veiculo_oculta_pessoa_inativa_exceto_a_gravada(
    dados, veiculo, pessoa
):
    pessoa.StatusPessoal = False
    pessoa.save()
    assert pessoa not in CadastraVeiculo().fields["Proprietario"].queryset
    form = CadastraVeiculo(instance=veiculo)
    assert pessoa in form.fields["Proprietario"].queryset


@pytest.mark.django_db
def test_index_veiculos(client_logado, veiculo):
    response = client_logado.get(reverse("indexveiculo"))
    assert response.status_code == 200
    assert b"ABC1D23" in response.content


@pytest.mark.django_db
def test_index_veiculos_com_veiculo_selecionado(client_logado, veiculo):
    url = f"{reverse('indexveiculo')}?id_veiculo={veiculo.pk}"
    response = client_logado.get(url)
    assert response.context["veiculo"] == veiculo
    assert response.context["cubagem"] == Decimal("20")


@pytest.mark.django_db
def test_consultaveiculo_antigo_redireciona(client_logado, veiculo):
    response = client_logado.get(
        reverse("consultaveiculo", args=[veiculo.pk])
    )
    assert response.status_code == 302
    assert response.url.endswith(f"?id_veiculo={veiculo.pk}")


@pytest.mark.django_db
@pytest.mark.parametrize(
    "situacao, aparece", [("ativos", False), ("inativos", True), ("todos", True)]
)
def test_lista_filtra_por_situacao(client_logado, veiculo, situacao, aparece):
    veiculo.Ativo = False
    veiculo.save()
    response = client_logado.get(
        reverse("veiculos_lista"), {"situacao": situacao}
    )
    assert ("ABC1D23" in response.json()["html-card-veiculos"]) == aparece


@pytest.mark.django_db
def test_lista_filtra_por_categoria(client_logado, veiculo):
    outra = CategoriaVeiculo.objects.create(Categoria="TRUCK")
    response = client_logado.get(
        reverse("veiculos_lista"), {"id_categoria": outra.pk}
    )
    assert "ABC1D23" not in response.json()["html-card-veiculos"]


@pytest.mark.django_db
def test_consulta_retorna_card_do_veiculo(client_logado, veiculo):
    response = client_logado.get(
        reverse("veiculo_consulta"), {"id_veiculo": veiculo.pk}
    )
    assert "DELIVERY" in response.json()["html-card-veiculo"]


@pytest.mark.django_db
def test_get_form_retorna_modal(client_logado, veiculo):
    response = client_logado.get(
        reverse("veiculo_form"), {"id_veiculo": veiculo.pk}
    )
    assert 'value="ABC1D23"' in response.json()["modal_html"]


@pytest.mark.django_db
def test_post_form_cria_veiculo(client_logado, dados):
    response = client_logado.post(reverse("veiculo_form"), dados)
    data = response.json()
    assert Veiculo.objects.filter(Placa="XYZ9A87").exists()
    assert data["tipo"] == "success"
    assert "XYZ9A87" in data["html-card-veiculo"]


@pytest.mark.django_db
def test_post_form_invalido_devolve_formulario(client_logado, dados):
    dados["Placa"] = "X"
    response = client_logado.post(reverse("veiculo_form"), dados)
    assert "html_form" in response.json()
    assert not Veiculo.objects.exists()


@pytest.mark.django_db
def test_post_form_altera_veiculo(client_logado, dados, veiculo):
    dados["id_veiculo"] = veiculo.pk
    client_logado.post(reverse("veiculo_form"), dados)
    veiculo.refresh_from_db()
    assert veiculo.Placa == "XYZ9A87"
    assert Veiculo.objects.count() == 1


@pytest.mark.django_db
def test_situacao_alterna_ativo(client_logado, veiculo):
    url = reverse("veiculo_situacao")
    client_logado.post(url, {"id_veiculo": veiculo.pk})
    veiculo.refresh_from_db()
    assert not veiculo.Ativo
    client_logado.post(url, {"id_veiculo": veiculo.pk})
    veiculo.refresh_from_db()
    assert veiculo.Ativo


@pytest.mark.django_db
def test_excluir_veiculo_sem_uso(client_logado, veiculo):
    response = client_logado.post(
        reverse("veiculo_excluir"), {"id_veiculo": veiculo.pk}
    )
    assert response.json()["tipo"] == "success"
    assert not Veiculo.objects.exists()


@pytest.mark.django_db
def test_excluir_veiculo_em_uso_e_recusado(client_logado, veiculo):
    Abastecimento.objects.create(
        DataAbastecimento=datetime.date.today(),
        idVeiculo=veiculo,
        TipoCombustivel="DIESEL",
        LitrosAbastecidos=Decimal("10"),
        ValorCombustivel=Decimal("6"),
        ValorAbastecido=Decimal("60"),
    )
    response = client_logado.post(
        reverse("veiculo_excluir"), {"id_veiculo": veiculo.pk}
    )
    data = response.json()
    assert data["tipo"] == "warning"
    assert "1 abastecimento(s)" in data["mensagem"]
    assert Veiculo.objects.exists()


@pytest.mark.django_db
def test_acoes_exigem_post(client_logado, veiculo):
    for nome in ("veiculo_situacao", "veiculo_excluir"):
        response = client_logado.get(reverse(nome), {"id_veiculo": veiculo.pk})
        assert response.status_code == 405
