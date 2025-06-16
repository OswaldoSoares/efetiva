""" Responsável pelas férias do colaborador """
from typing import Dict
from pessoas.models import Aquisitivo, Ferias


def create_contexto_ferias_colaborador(id_pessoal: int) -> Dict:
def faltas_periodo_aquisitivo(id_pessoal: int, aquisitivo) -> List[str]:
    """
        Retorna um dicionário com os períodos aquititivos e os períodos de
        gozo das férias de um colaborador
    Retorna uma lista com as datas das faltas não remuneradas registradas
    durante o período aquisitivo do colaborador.

    De acordo com a CLT, faltas injustificadas podem impactar diretamente
    no cálculo dos dias de férias a que o colaborador tem direito.

    Args:
        id_pessoal (int): ID do colaborador.
        aquisitivo: Objeto representando o período aquisitivo.

    Returns:
        List[str]: Lista de datas (formatadas como "dd/mm/yyyy") das faltas
                   não remuneradas.
    """
    inicio = aquisitivo.DataInicial
    final = aquisitivo.DataFinal

    dias_faltas = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[inicio, final],
        Ausencia="FALTA",
        Remunerado=False,
    ).values_list("Dia", flat=True)

    return [datetime.strftime(dia, "%d/%m/%Y") for dia in dias_faltas]


def meses_proporcionais_ferias(data_inicial, data_final):
    """
    Calcula a quantidade de meses proporcionais de férias com base no
    período entre a data inicial e final do contrato (ou até a data atual).

    Conforme orientação da CLT, cada mês completo de trabalho gera direito
    a 1/12 de férias. Um mês é considerado completo se houver ao menos 15
    dias trabalhados.

    Args:
        data_inicial (date): Data de início do período aquisitivo.
        data_final (date): Data de fim do contrato ou do período.

    Returns:
        int: Quantidade de meses proporcionais de férias (doze avos).
    """
    hoje = datetime.today().date()
    periodo = relativedelta(
        data_final if data_final < hoje else hoje, data_inicial
    )

    return periodo.months + (1 if periodo.days >= 15 else 0)


def calcular_dias_ferias_proporcionais(faltas, dozeavos):
    """
    Calcula a quantidade de dias de férias proporcionais de acordo com as
    faixas de faltas injustificadas, conforme prevê a CLT (Art. 130).

    Faixas aplicadas:
        - Até 5 faltas: 30 dias (2.5 dias por mês)
        - 6 a 14 faltas: 24 dias (2.0 dias por mês)
        - 15 a 23 faltas: 18 dias (1.5 dias por mês)
        - 24 a 32 faltas: 12 dias (1.0 dia por mês)
        - Acima de 32 faltas: 0 dias

    Args:
        faltas (int): Número de faltas injustificadas.
        dozeavos (int): Meses de férias proporcionais adquiridos.

    Returns:
        float: Quantidade proporcional de dias de férias devidos.
    """
    faixas = [
        (5, 2.5),  # Até 5 faltas
        (14, 2.0),  # De 6 a 14 faltas
        (23, 1.5),  # De 15 a 23 faltas
        (32, 1.0),  # De 24 a 32 faltas
    ]

    multiplicador = next(
        (valor for limite, valor in faixas if faltas <= limite), 0
    )

    return multiplicador * dozeavos


def calcula_valores_ferias(salario, faltas, data_inicial, data_final):
    """
    Calcula os valores financeiros referentes às férias proporcionais,
    incluindo:
    - Valor das férias (dias proporcionais x salário diário)
    - Adicional de 1/3 constitucional
    - Total a ser pago

    Cálculos realizados conforme a CLT (Art. 129 a 130 e 142).

    Args:
        id_pessoal:
        salario (Decimal): Valor do salário base mensal.
        faltas (int): Total de faltas injustificadas no período.
        data_inicial (date): Data inicial do período aquisitivo.
        data_final (date): Data final do período aquisitivo.

    Returns:
        Dict: {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}
        Tuple[Decimal, Decimal, Decimal, Decimal]:
            - dias: Dias proporcionais de férias
            - valor: Valor base das férias
            - um_terco: Adicional de 1/3 constitucional
            - total: Valor total a ser pago (férias + 1/3)
    """
    meses = meses_proporcionais_ferias(data_inicial, data_final)
    dias = Decimal(calcular_dias_ferias_proporcionais(faltas, meses))
    valor = (salario / 30 * dias).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    um_terco = (valor / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = valor + um_terco

    return dias, valor, um_terco, total


def anota_dados_ferias(id_pessoal, aquisitivos):
    """
    aquisitivos = Aquisitivo.objects.filter(idPessoal=id_pessoal)
    gozo_ferias = Ferias.objects.filter(idPessoal=id_pessoal)
    Processa cada período aquisitivo de um colaborador e anota os dados de
    férias calculados, incluindo:
        - Faltas
        - Dias de férias proporcionais
        - Valor das férias
        - Adicional de 1/3 constitucional
        - Valor total

    Args:
        id_pessoal (int): ID do colaborador.
        aquisitivos (QuerySet): Lista de objetos de períodos aquisitivos.

    Returns:
        QuerySet: Lista de objetos aquisitivos com os atributos anotados.
    """
    salario = (
        Salario.objects.filter(idPessoal=id_pessoal)
        .values_list("Salario", flat=True)
        .first()
    )

    for aquisitivo in aquisitivos:
        faltas = len(faltas_periodo_aquisitivo(id_pessoal, aquisitivo))
        dias, valor, um_terco, total = calcula_valores_ferias(
            salario, faltas, aquisitivo.DataInicial, aquisitivo.DataFinal
        )

        aquisitivo.faltas = faltas
        aquisitivo.dias = dias
        aquisitivo.valor = valor
        aquisitivo.um_terco = um_terco
        aquisitivo.total = total

    return aquisitivos

    return {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}
