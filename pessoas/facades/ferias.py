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
    Args:
        id_pessoal:

    Returns:
        Dict: {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}

    """
    aquisitivos = Aquisitivo.objects.filter(idPessoal=id_pessoal)
    gozo_ferias = Ferias.objects.filter(idPessoal=id_pessoal)

    return {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}
