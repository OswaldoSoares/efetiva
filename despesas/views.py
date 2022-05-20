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
    _var = dict(request.POST)
    data = facade.valida_multa(request, _var)
    return data
