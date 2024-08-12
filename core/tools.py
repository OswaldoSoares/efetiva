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


def calcular_diferenca(data, inicial, final):
    """
    Calcula a diferença de tempo entre dois horários no mesmo dia e retorna
    como datetime.time.

    Args:
        data (datetime.date): A data associada aos horários.
        inicial (datetime.time): O horário inicial.
        final (datetime.time): O horário final, que pode ser `None`
                               ou `time(0, 0)` se não estiver definido.

    Returns:
        datetime.time: A diferença de tempo entre os dois horários.
                       Retorna `time(0, 0)` se `final` for `None`
                       ou `time(0, 0)` ou se `final` for antes de `inicial`.
    """
    periodo = timedelta(hours=0, minutes=0)
    if final and final != time(0, 0):
        inicial = datetime.combine(data, inicial)
        final = datetime.combine(data, final)
        if inicial < final:
            periodo = final - inicial
    total_segundos = int(periodo.total_seconds())
    horas = total_segundos // 3600
    minutos = (total_segundos % 3600) // 60
    return time(horas, minutos)


def data_str_br(data):
    """
    Converte um objeto datetime para uma string no formato brasileiro de
    data (dd/mm/yyyy).

    Args:
        data (datetime.datetime): O objeto datetime a ser convertido.

    Returns:
        str: A data formatada como string no formato dd/mm/yyyy.
    """
    return datetime.strftime(data, "%d/%m/%Y")


def hora_str(hora):
    """
    Converte um objeto time para uma string no formato HH:MM.

    Args:
        hora (datetime.time): O objeto time a ser convertido.

    Returns:
        str: A hora formatada como string no formato HH:MM.
    """
    return time.strftime(hora, "%H:%M")


def str_hora(string):
    return datetime.strptime(string, "%H:%M").time()
