""" Responsável pelas férias do colaborador """
from typing import Dict
from pessoas.models import Aquisitivo, Ferias


def create_contexto_card_ferias(id_pessoal: int) -> Dict:
    """
        Retorna um dicionário com os períodos aquititivos e os períodos de
        gozo das férias de um colaborador
    Args:
        id_pessoal:

    Returns:
        Dict: {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}

    """
    aquisitivos = Aquisitivo.objects.filter(idPessoal=id_pessoal)
    gozo_ferias = Ferias.objects.filter(idPessoal=id_pessoal)

    return {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}
