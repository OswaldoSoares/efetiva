""" MÓDULO COM FUNÇÕES QUE SERÃO USADAS EM TODO O PROJETO """
import calendar
import json
import locale
import os
from datetime import datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import parse_qs, urlparse

from django.db.models import Sum
from django.http import JsonResponse
from django.template.loader import render_to_string
from num2words import num2words

from core.constants import MESES
from core.message import mensagens
from pessoas.models import CartaoPonto
from transefetiva.settings import settings
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
    data["tipo"] = contexto["tipo"]
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
    """Consultar Documentação Sistema Efetiva"""
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


def injetar_parametro_no_request_post(request, url_field="request_passado"):
    """Consultar Documentação Sistema Efetiva"""
    url_string = request.POST.get(url_field)

    if url_string:
        parsed_url = urlparse(url_string)
        query_params = parse_qs(parsed_url.query)

        new_post = request.POST.copy()

        for key, value in query_params.items():
            if not key == "id_file_upload":
                if value:
                    new_post[key] = value[0]

        del new_post[url_field]

        request._post = new_post
        request._files = request.FILES  # mantém arquivos se houver

    return request


def criar_lista_nome_de_arquivos_no_diretorio(inicio_nome, diretorio):
    caminho = Path(settings.MEDIA_ROOT) / "upload_files"

    arquivos = [
        f.stem
        for f in caminho.iterdir()
        if f.is_file() and f.name.startswith("Documento")
    ]

    return arquivos


def get_mensagem(codigo, **kwargs):
    msg_data = mensagens.get(codigo)
    if not msg_data:
        return {"mensagem": "Mensagem não encontrada.", "tipo": "info"}

    try:
        mensagem_formatada = msg_data["mensagem"].format(**kwargs)
    except KeyError as e:
        mensagem_formatada = f"erro ao formatar mensagem: parâmetro ausente ({e})"

    return{"mensagem": mensagem_formatada, "tipo": msg_data["tipo"]}


def obter_feriados_sabados_domingos_mes(mes: int, ano: int):
    with open('data/Feriados_2021_2035.json', encoding='utf-8') as f:
        feriados = json.load(f)

    ano_str = str(ano)
    mes_str = str(mes).zfill(2)

    feriados_mes_formatado = []
    feriados_datas = set()
    if ano_str in feriados and mes_str in feriados[ano_str]:
        for evento in feriados[ano_str][mes_str]:
            data_formatada = datetime.strptime(
                evento['data'][:10], "%Y-%m-%d"
            ).strftime("%d/%m/%Y")
            descricao = ", ".join(evento['descricao'])
            feriados_mes_formatado.append(f"{data_formatada} - {descricao}")
            feriados_datas.add(data_formatada)

    domingos = []
    for semana in calendar.monthcalendar(ano, mes):
        dia = semana[calendar.SUNDAY]
        if dia != 0:
            data_domingo = datetime(ano, mes, dia).strftime("%d/%m/%Y")
            if data_domingo not in feriados_datas:
                domingos.append(data_domingo)

    sabados = []
    for semana in calendar.monthcalendar(ano, mes):
        dia = semana[calendar.SATURDAY]
        if dia != 0:
            data_sabado = datetime(ano, mes, dia).strftime("%d/%m/%Y")
            if data_sabado not in feriados_datas:
                sabados.append(data_sabado)

    return feriados_mes_formatado, domingos, sabados


def get_saldo_contra_cheque(contra_cheque_itens):
    """Consultar Documentação Sistema Efetiva"""
    creditos = contra_cheque_itens.filter(Registro="C").aggregate(
        total=Sum("Valor")
    ).get("total") or Decimal(0)
    debitos = contra_cheque_itens.filter(Registro="D").aggregate(
        total=Sum("Valor")
    ).get("total") or Decimal(0)
    saldo = creditos - debitos

    return {"credito": creditos, "debito": debitos, "saldo": saldo}


def periodo_por_extenso(data_inicial, data_final):
    locale.setlocale(locale.LC_TIME, 'pt_BR.UTF-8')

    inicial_extenso = datetime.strftime(data_inicial, "%d de %B de %Y")
    final_extenso = datetime.strftime(data_final, "%d de %B de %Y")

    return f"{inicial_extenso} a {final_extenso}"


def valor_por_extenso(valor, tamanho=200, padrao=" _*_"):
    extenso = num2words(valor, lang="pt_BR", to="currency")
    extenso = extenso.upper()

    if len(extenso) < tamanho:
        faltam = tamanho - len(extenso)
        repeticoes = (padrao * ((faltam // len(padrao)) + 1))[:faltam]
        extenso += repeticoes

    return extenso


def antecipar_data_final_de_semana(data):
    if data.weekday() == 5:
        data -= timedelta(days=1)
    elif data.weekday() == 6:
        data -= timedelta(days=2)

    return data


def obter_faltas_periodo(id_pessoal, inicio, final):
    dias_faltas = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[inicio, final],
        Ausencia="FALTA",
        Remunerado=False,
    ).values_list("Dia", flat=True)

    return [datetime.strftime(dia, "%d/%m/%Y") for dia in dias_faltas]


def obter_dias_inicial_final_contra_cheque(contra_cheque, mes_atual=0):
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    mes_extenso = contra_cheque.MesReferencia
    mes = int(datetime.strptime(mes_extenso, "%B").month)
    mes += mes_atual
    ano = contra_cheque.AnoReferencia

    return primeiro_e_ultimo_dia_do_mes(mes, ano)
