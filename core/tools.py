""" MÓDULO COM FUNÇÕES QUE SERÃO USADAS EM TODO O PROJETO """
import calendar
import os
from datetime import datetime, time, timedelta
from pathlib import Path
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.constants import MESES
from website.models import FileUpload


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


def nome_curto(nome):
    apelido = None
    if nome:
        apelido = nome.split()
        if len(apelido) > 2:
            if len(apelido[1]) > 2:
                del apelido[2:]
            else:
                del apelido[3:]
            apelido = " ".join(apelido)
        else:
            apelido = nome
    return apelido


def nome_curto_underscore(nome):
    apelido = None
    if nome:
        apelido = nome.split()
        if len(apelido) > 2:
            if len(apelido[1]) > 2:
                del apelido[2:]
            else:
                del apelido[3:]
            apelido = "_".join(apelido)
        else:
            apelido = "_".join(apelido)
    return apelido


def obter_mes_por_numero(numero):
    return MESES.get(numero, "Mês inválido")


def gerar_data_html(html_functions, request, contexto, data):
    data["mensagem"] = contexto["mensagem"]
    for html_func in html_functions:
        data = html_func(request, contexto, data)

    return JsonResponse(data)


def primeiro_e_ultimo_dia_do_mes(mes: int, ano: int) -> tuple:
    """
    Retorna o primeiro e o último dia de um mês específico.

    Args:
        mes (int): O mês desejado (1 a 12).
        ano (int): O ano desejado.

    Returns:
        tuple: Uma tupla contendo duas datas:
            - O primeiro dia do mês como um objeto `datetime`.
            - O último dia do mês como um objeto `datetime`.

    Exemplo:
        >>> primeiro_e_ultimo_dia_do_mes(2, 2024)
        (datetime.datetime(2024, 2, 1, 0, 0), datetime.datetime(2024, 2, 29, 0, 0))
    """
    primeiro = datetime(ano, mes, 1)
    ultimo = primeiro.replace(day=calendar.monthrange(ano, mes)[1])
    return [primeiro, ultimo]


def upload_de_arquivo(request, nome_arquivo, max_size_mb):
    """Consultar Documentação Sistema Efetiva"""
    if request.method != "POST":
        return {"mensagem": "Método inválido."}

    if not request.FILES:
        return {"mensagem": "Arquivo não selecionado."}

    file_uploaded = request.FILES["arquivo"]
    ext_file = file_uploaded.name.split(".")[-1].lower()

    if ext_file not in ["pdf", "jpg", "png"]:
        return {
            "mensagem": "Tipo de arquivo não permitido."
            " Permitidos: pdf, jpg e png",
        }

    max_file_size = max_size_mb * 1024 * 1024
    if file_uploaded.size > max_file_size:
        return {
            "mensagem": f"Arquivo muito grande. O limite é {max_size_mb}MB.",
        }

    descricao = nome_arquivo.rsplit(".", 1)[0]
    name_file = f"{descricao}.{ext_file}"
    file_uploaded.name = name_file

    try:
        obj = FileUpload.objects.filter(DescricaoUpload=descricao).first()

        if obj:
            if obj.uploadFile and os.path.isfile(obj.uploadFile.path):
                os.remove(obj.uploadFile.path)
        else:
            obj = FileUpload()

        obj.DescricaoUpload = descricao
        obj.uploadFile = file_uploaded
        obj.save()

        return {"mensagem": "Arquivo enviado ao servidor com sucesso"}

    # TODO: Refinar exceções específicas mais tarde
    except Exception as error:  # pylint: disable=W0703
        print(f"Erro ao salvar: {error}")

        return {"mensagem": "Falha ao salvar o arquivo, tente novamente"}


def excluir_arquivo(id_file_upload):
    """Consultar Documentação Sistema Efetiva"""
    file = FileUpload.objects.filter(idFileUpload=id_file_upload).first()
    if file:
        try:
            caminho = file.uploadFile.path
            if os.path.exists(caminho):
                os.remove(caminho)
            file.delete()
            mensagem = "Arquivo excluído com sucesso."

        # TODO: Refinar exceções específicas mais tarde
        except Exception as error:  # pylint: disable=W0703
            print(f"Erro ao excluir arquivo: {error}")
            mensagem = "Erro ao excluir o arquivo."
    else:
        mensagem = "Arquivo não encontrado."

    return {"mensagem": mensagem}


def modal_excluir_arquivo(id_file_upload, request):
    file = FileUpload.objects.get(idFileUpload=id_file_upload)
    ext = Path(file.uploadFile.name).suffix.lower().strip(".")

    contexto = {
        "file": file,
        "file_url": file.uploadFile.url,
        "file_ext": ext,
        "file_id": file.idFileUpload,
    }

    modal_html = render_to_string(
        "core/modal_excluir_arquivo.html", contexto, request=request
    )

    return JsonResponse({"modal_html": modal_html})
