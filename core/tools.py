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


def str_hoje() -> str:
    """
    Data de Hoje

    Returns:
        str: Retorna a data de hoje no formato ano-mês-dia
    """
    hoje = datetime.today()
    hoje = datetime.strftime(hoje, "%Y-%m-%d")
    return hoje


def convert_milimetro_pontos(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def get_request_data(request, key):
    """
    Recupera um valor da requisição HTTP, priorizando os dados do POST.

    Esta função tenta recuperar o valor associado à chave fornecida
    a partir dos dados do POST da requisição. Se a chave não for encontrada
    no POST, ela verifica os dados do GET.

    Args:
        request (HttpRequest): O objeto de requisição HTTP contendo os dados
        de POST e GET.
        key (str): A chave do dado a ser recuperado da requisição.

    Returns:
        str ou None: O valor associado à chave, se encontrado nos dados de
        POST ou GET, ou None se a chave não estiver presente em nenhum dos
        dois.
    """
    return request.POST.get(key) or request.GET.get(key)


def formatar_numero_com_separadores(valor, digitos_decimais):
    """
    Formata um número para uma string com separadores de milhar e um
    formato decimal específico.

    A função assume que o separador decimal deve ser uma vírgula e o
    separador de milhar deve ser um ponto.
    Se o valor for None ou uma string vazia, retorna "0" com o formato
    decimal especificado.

    Exemplo:
        Para o valor 1234.567 e digitos_decimais = 2, a função
        retornará "1.234,57".

    :param valor: O número a ser formatado. Pode ser um float ou uma
                  string representando um número.
    :param digitos_decimais: O número de casas decimais desejadas na
                             formatação.
    :return: O número formatado como uma string.
    """
    digitos_decimais = int(digitos_decimais)
    if valor:
        # Converte o valor para float e formata com o número de casas
        # decimais especificado
        valor_formatado = f"{float(valor):,.{digitos_decimais}f}"
        # Substitui os separadores conforme o formato local
        return (
            valor_formatado.replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )
    else:
        # Retorna 0 com o número de casas decimais especificado
        if digitos_decimais == 0:
            return "0"
        else:
            return f"0,{''.join(['0' for _ in range(digitos_decimais)])}"
