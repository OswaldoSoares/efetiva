"""
    Módulo Facade
"""
import datetime
import time

from dateutil.relativedelta import relativedelta
from django.db import connection, reset_queries
from django.http import JsonResponse
from django.template.loader import render_to_string
from clientes.facade import get_cliente

from website.forms import CadastraFeriado

from website.models import FileUpload
from .models import Parametros


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


def cmp(mm: float) -> float:
    """
    Converte milimetros em pontos - Utilizado na criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def str_hoje() -> str:
    """
    Data de Hoje

    Returns:
        str: Retorna a data de hoje no formato ano-mês-dia
    """
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    return hoje


def dict_tipo_doc() -> dict:
    tipo_doc = {
        "RG": "RG",
        "CPF": "CPF",
        "HABILITAÇÃO": "HABILITAÇÃO",
        "RESERVISTA": "RESERVISTA",
        "PIS/PASEP": "PISPASEP",
    }
    return tipo_doc


def dict_tipo_fone() -> dict:
    tipo_fone = {
        "WHATSAPP": "WHATSAPP",
        "VIVO": "VIVO",
        "TIM": "TIM",
        "OI": "OI",
        "CLARO": "CLARO",
        "FIXO": "FIXO",
        "RECADO": "RECADO",
    }
    return tipo_fone


def dict_tipo_conta() -> dict:
    tipo_conta = {
        "CORRENTE",
        "CORRENTE",
        "POUPANÇA",
        "POUPANÇA",
    }
    return tipo_conta


def extremos_mes(_mes, _ano):
    first_day = datetime.datetime.strptime(
        f"1-{int(_mes)}-{int(_ano)}", "%d-%m-%Y"
    )
    last_day = first_day + relativedelta(months=+1, days=-1)
    return first_day, last_day


def converter_mes_ano(_mes_ano):
    _date = datetime.datetime.strptime(_mes_ano, "%B/%Y")
    _mes = datetime.datetime.strftime(_date, "%m")
    _ano = datetime.datetime.strftime(_date, "%Y")
    return _mes, _ano


def valor_ponto_milhar(valor, digitos_decimal):
    if valor:
        formato_decimal = f",.{digitos_decimal}f"
        valor_formatado = (
            format(float(valor), f"{formato_decimal}")
            .replace(",", "_")
            .replace(".", ",")
            .replace("_", ".")
        )
        return valor_formatado
    else:
        string = "0"
        valor_return = f"0,{string * digitos_decimal}"
        return valor_return


def queries_inicio():
    reset_queries()
    start = time.time()
    start_queries = len(connection.queries)
    return start, start_queries


def queries_termino(start, start_queries, info):
    end = time.time()
    end_queries = len(connection.queries)
    print(connection.queries)
    print(f"{info} - Queries {end_queries} - Tempo: {'%.2fs' % (end - start)}")


def busca_arquivo_descricao(descricao):
    file = FileUpload.objects.filter(DescricaoUpload=descricao)
    return file


class DiasFeriados:
    def __init__(self):
        self.feriados = self.get_dias_feriados()

    @staticmethod
    def get_dias_feriados():
        feriados = Parametros.objects.filter(Chave="FERIADO").order_by(
            "-Valor"
        )
        lista = [
            datetime.datetime.strptime(itens.Valor, "%Y-%m-%d").date()
            for itens in feriados
        ]
        return lista


class Feriados:
    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.feriados = self.get_feriados()

    @staticmethod
    def get_feriados():
        feriados = Parametros.objects.filter(Chave="FERIADO").order_by(
            "-Valor"
        )
        lista = [itens.Valor for itens in feriados]
        return lista


def create_parametro_context():
    tabela_padrao = get_tabela_padrao()
    tabela_padrao_cliente = ""
    if tabela_padrao:
        tabela_padrao_cliente = get_cliente(tabela_padrao[0].Valor)
    lista_feriados = Feriados("Lista", "Feriados")
    form_feriado = CadastraFeriado()
    context = {
        "tabela_padrao": tabela_padrao,
        "tabela_padrao_cliente": tabela_padrao_cliente,
        "form_feriado": form_feriado,
        "lista_feriados": lista_feriados,
    }
    return context


def get_parametros_all():
    """

    :return:
    """
    return Parametros.objects.all()


def get_parametro(idparametro):
    """

    :return:
    """
    return Parametros.objects.filter(idParametro=idparametro)


def get_tabela_padrao():
    """

    :return:
    """
    return Parametros.objects.filter(Chave="TABELA PADRAO")


def salva_parametro(chave, valor):
    parametro = Parametros()
    obj = parametro
    obj.Chave = chave
    obj.Valor = valor
    obj.save()


def form_parametro(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    if c_idobj:
        c_instance = Parametros.objects.get(idParametro=c_idobj)
    if request.method == "POST":
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
    else:
        form = c_form(instance=c_instance)
    context = {
        "form": form,
        "c_idobj": c_idobj,
        "c_url": c_url,
        "c_view": c_view,
    }
    data["html_form"] = render_to_string(
        "website/formparametros.html", context, request=request
    )
    data["c_view"] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_parametro(request, c_idobj, c_url, c_view):
    data = dict()
    c_queryset = get_parametro(c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {"c_url": c_url, "c_view": c_view, "c_queryset": c_queryset}
    data["html_form"] = render_to_string(
        "clientes/formcliente.html", context, request=request
    )
    data["c_view"] = c_view
    c_return = JsonResponse(data)
    return c_return
