import datetime

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render

from despesas import facade

from .forms import CadastraAbastecimento


@login_required(login_url="login")
def index_despesas(request):
    contexto = facade.create_despesas_context()
    categorias = facade.create_contexto_categoria()
    contexto.update({"categorias": categorias})
    despesas_pagar = facade.create_contexto_despesas()
    contexto.update({"despesas_pagar": despesas_pagar})
    return render(request, "despesas/index.html", contexto)


def cria_abastecimento(request):
    c_forn = CadastraAbastecimento
    c_idobj = None
    c_url = "despesas/criadespesa/"
    c_view = "cria_abastecimento"
    data = facade.form_despesa(request, c_forn, c_idobj, c_url, c_view)
    return data


def adiciona_multa(request):
    idmulta = request.POST.get("idMulta")
    error, msg = facade.valida_multa(request)
    multa = facade.read_multa_post(request)
    if not error:
        facade.save_multa(multa, idmulta)
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


def adiciona_despesa(request):
    error, msg = facade.valida_despesa(request)
    contexto = {"error": error}
    contexto.update(msg)
    despesa = facade.read_despesa_post(request)
    if not error:
        #     if _id_des:
        #         facade.update_multa(multa, _id_des)
        #     else:
        facade.save_despesa(despesa)
        despesa = dict()
    contexto = facade.create_despesas_context()
    categorias = facade.create_contexto_categoria()
    contexto.update({"categorias": categorias})
    if despesa:
        subcategorias = facade.create_contexto_subcategoria(despesa["categoria"])
        contexto.update({"subcategorias": subcategorias})
    contexto.update({"despesa": despesa, "error": error})
    contexto.update(msg)
    data = facade.create_data_form_despesa(request, contexto)
    return data


def edita_despesa(request):
    pass


def exclui_despesa(request):
    pass


def adiciona_categoria(request):
    error, msg = facade.valida_categoria(request)
    if not error:
        categoria = facade.read_categoria_post(request)
        facade.save_categoria(categoria)
    contexto = {"error": error}
    contexto.update(msg)
    data = facade.create_data_form_categoria(request, contexto)
    return data


def adiciona_subcategoria(request):
    error, msg = facade.valida_subcategoria(request)
    if not error:
        subcategoria = facade.read_subcategoria_post(request)
        facade.save_subcategoria(subcategoria)
    contexto = {"error": error}
    contexto.update(msg)
    categorias = facade.create_contexto_categoria()
    contexto.update({"categorias": categorias})
    data = facade.create_data_form_subcategoria(request, contexto)
    return data


def carrega_subcategoria(request):
    idcategoria = request.GET.get("idcategoria")
    subcategorias = facade.create_contexto_subcategoria(idcategoria)
    contexto = {"subcategorias": subcategorias}
    data = facade.create_data_choice_subcategoria(request, contexto)
    return data


def filtro_motorista(request):
    idpessoal = request.GET.get("idpessoal")
    if not idpessoal == "SEM FILTRO":
        contexto = facade.create_contexto_filtro_motorista(idpessoal)
    else:
        contexto = facade.create_contexto_multas_pagar()
    data = facade.create_data_multas_pagar(request, contexto)
    return data


def filtro_veiculo(request):
    idveiculo = request.GET.get("idveiculo")
    if not idveiculo == "SEM FILTRO":
        contexto = facade.create_contexto_filtro_veiculo(idveiculo)
    else:
        contexto = facade.create_contexto_multas_pagar()
    data = facade.create_data_multas_pagar(request, contexto)
    return data
