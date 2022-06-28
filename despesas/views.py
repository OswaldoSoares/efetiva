import datetime

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from despesas import facade

from .forms import CadastraAbastecimento


@login_required(login_url="login")
def index_despesas(request):
    contexto = facade.create_despesas_context()
    return render(request, "despesas/index.html", contexto)


def cria_abastecimento(request):
    c_forn = CadastraAbastecimento
    c_idobj = None
    c_url = "despesas/criadespesa/"
    c_view = "cria_abastecimento"
    data = facade.form_despesa(request, c_forn, c_idobj, c_url, c_view)
    return data


def adiciona_multa(request):
    _id_mul = request.POST.get("idMulta")
    error, msg = facade.valida_multa(request)
    multa = facade.read_multa_post(request)
    if not error:
        if _id_mul:
            facade.update_multa(multa, _id_mul)
        else:
            facade.save_multa(multa)
        multa = dict()
    contexto = facade.create_despesas_context()
    contexto.update({"multa": multa, "error": error})
    contexto.update(msg)
    data = facade.create_data_form_multa(request, contexto)
    return data


def edita_multa(request):
    _id_mul = request.GET.get("idMulta")
    error, msg = False, dict()
    multa = facade.read_multa_database(_id_mul)
    _mm = facade.busca_minutas_multa(multa["data_multa"])
    dia = datetime.datetime.strptime(multa["data_multa"], "%Y-%m-%d")
    contexto = facade.create_despesas_context()
    contexto.update({"multa": multa, "error": error, "minutas": _mm})
    contexto.update({"minutas": _mm, "dia": dia})
    contexto.update(msg)
    data = facade.create_data_edita_multa(request, contexto)
    return data


def exclui_multa(request):
    _id_mul = request.GET.get("idMulta")
    facade.delete_multa(_id_mul)
    contexto = facade.create_despesas_context()
    data = facade.create_data_multas_pagar(request, contexto)
    return data


def minutas_multa(request):
    _date = request.GET.get("date")
    _mm = facade.busca_minutas_multa(_date)
    dia = datetime.datetime.strptime(_date, "%Y-%m-%d")
    contexto = {"minutas": _mm, "dia": dia}
    data = facade.create_data_minutas_multa(request, contexto)
    return data
