"""
Arquivo de configyrações do pytest - fixtures
"""
from datetime import datetime
from dateutil.relativedelta import relativedelta
import pytest

from faker import Factory

from pessoas.models import Aquisitivo, Pessoal, Ferias

fake = Factory.create("pt-BR")


@pytest.fixture
def gera_colaborador():
    """

    Returns:


    """
    bairro = fake.street_name()  # pylint: disable=no-member
    while len(bairro) > 20:
        bairro = fake.street_name()  # pylint: disable=no-member
    data_admissao_inicial = (
        fake.date_between_dates(  # pylint: disable=no-member
            datetime.strptime(
                "01/01/2021 23:59:59.099000", "%m/%d/%Y %H:%M:%S.%f"
            ).date(),
            datetime.now(),
        )
    )
    data_admissao_final = datetime.now()
    colaborador = Pessoal.objects.create(
        Nome=fake.name_male(),  # pylint: disable=no-member
        Endereco=fake.street_address(),  # pylint: disable=no-member
        Bairro=bairro,
        CEP="01234-987",
        Cidade=fake.city(),  # pylint: disable=no-member
        Estado="SP",
        DataNascimento=fake.date_of_birth(),  # pylint: disable=no-member
        Mae=fake.name_female(),  # pylint: disable=no-member
        Pai=fake.name_male(),  # pylint: disable=no-member
        Categoria="MOTORISTA",
        TipoPgto="MENSALISTA",
        StatusPessoal=True,
        DataAdmissao=fake.date_between_dates(  # pylint: disable=no-member
            data_admissao_inicial,
            data_admissao_final,
        ),
    )
    return colaborador


@pytest.fixture
def gera_aquisitivo(gera_colaborador):  # pylint: disable=redefined-outer-name
    """

    Args:
    gera_colaborador:

    Returns:


    """
    colaborador = gera_colaborador
    aquisitivo = Aquisitivo.objects.create(
        DataInicial=colaborador.DataAdmissao,
        DataFinal=colaborador.DataAdmissao + relativedelta(years=+1, days=-1),
        idPessoal=colaborador,
    )
    return aquisitivo, colaborador


@pytest.fixture
def gera_ferias(gera_aquisitivo):  # pylint: disable=redefined-outer-name
    """

    Args:
    gera_aquisitivo:

    Returns:


    """
    aquisitivo, colaborador = gera_aquisitivo
    ferias = Ferias.objects.create(
        DataInicial=fake.date(),  # pylint: disable=no-member
        DataFinal=fake.date(),  # pylint: disable=no-member
        idAquisitivo=aquisitivo,
        idPessoal=colaborador,
    )
    return ferias, aquisitivo, colaborador


@pytest.fixture
def busca_aquisitivo(gera_colaborador):  # pylint: disable=redefined-outer-name
    """

    Args:
    gera_colaborador:

    Returns:


    """
    colaborador = gera_colaborador
    aquisitivo = Aquisitivo.objects.filter(idPessoal=colaborador)
    return aquisitivo


@pytest.fixture
def gera_varios_aquisitivos(gera_colaborador):
    """

    Args:
    gera_colaborador:

    Returns:


    """

    def cria_aquisitivo(data_inicial, data_final, colaborador):
        Aquisitivo.objects.create(
            DataInicial=data_inicial,
            DataFinal=data_final,
            idPessoal=colaborador,
        )

    colaborador = gera_colaborador
    data_admissao = colaborador.DataAdmissao
    data_um_ano_atraz = (datetime.now() + relativedelta(years=-1)).date()
    if data_admissao > data_um_ano_atraz:
        nova_data_admissao = (
            fake.date_between_dates(  # pylint: disable=no-member
                datetime.strptime(
                    "01/01/2021 23:59:59.099000", "%m/%d/%Y %H:%M:%S.%f"
                ).date(),
                datetime.now() + relativedelta(years=-1),
            )
        )
    colaborador.DataAdmissao = nova_data_admissao
    colaborador.save()
    data_admissao = colaborador.DataAdmissao
    data_completa_ano = data_admissao + relativedelta(years=+1, days=-1)
    cria_aquisitivo(data_admissao, data_completa_ano, colaborador)
    data_inicial = data_admissao
    data_final = data_completa_ano
    while data_final < datetime.now().date():
        data_inicial = data_inicial + relativedelta(years=+1)
        data_final = data_final + relativedelta(years=+1)
        cria_aquisitivo(data_inicial, data_final, colaborador)
    aquisitivo = list(Aquisitivo.objects.filter(idPessoal=colaborador))
    return aquisitivo, colaborador
