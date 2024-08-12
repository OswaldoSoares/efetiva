""" MÓDULO COM FUNÇÕES QUE SERÃO USADAS EM TODO O PROJETO """
from datetime import datetime, time, timedelta


def apos_meia_noite(hora):
    """
    Verifica se a hora fornecida é após a meia-noite.

    Args:
        hora (datetime.time): A hora a ser verificada.

    Returns:
        bool: True se a hora for após a meia-noite, False caso contrário.
    """
    meia_noite = time(0, 0)
    is_apos_meia_noite = hora > meia_noite
    return is_apos_meia_noite
