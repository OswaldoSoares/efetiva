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
    Args:
        id_pessoal:

    Returns:
        Dict: {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}

    """
    aquisitivos = Aquisitivo.objects.filter(idPessoal=id_pessoal)
    gozo_ferias = Ferias.objects.filter(idPessoal=id_pessoal)

    return {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}
