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
    data = facade.html_form_multas(request, multa, error, msg)
    return data


def edita_multa(request):
    _id_mul = request.GET.get("idMulta")
    print(_id_mul)
    error, msg = False, dict()
    multa = facade.read_multa_database(_id_mul)
    data = facade.html_form_multas(request, multa, error, msg)
    return data


def exclui_multa(request):
    _id_mul = request.GET.get("idMulta")
    facade.delete_multa(_id_mul)


def minutas_multa(request):
    _id_vei = request.GET.get("idveiculo")
    _date = request.GET.get("date")
    _mm = facade.busca_minutas_multa(_id_vei, _date)
    data = facade.html_minutas_multa(request, _mm)
    return data
