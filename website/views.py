from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from veiculos.models import CategoriaVeiculo
from .models import Parametros
from .forms import CadastraParametro, CadastraParametroTabelaPadrao
from website import facade


def index_website(request):
    return render(request, "website/index.html")


@login_required(login_url="login")
def parametros(request):
    # parametro = facade.get_parametros_all()
    # categoria_veiculos = CategoriaVeiculo.objects.all()
    # contexto = {'categoria_veiculos': categoria_veiculos, 'tabela_padrao': tabela_padrao}
    contexto = facade.create_parametro_context()
    return render(request, "website/parametros.html", contexto)


@login_required(login_url="login")
def cria_parametro(request):
    c_form = CadastraParametro
    c_idobj = None
    c_url = "/criaparametro/"
    c_view = "cria_parametro"
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data


@login_required(login_url="login")
def cria_parametro_tabela_padrao(request):
    c_form = CadastraParametroTabelaPadrao
    c_idobj = None
    c_url = "/criaparametrotabelapadrao/"
    c_view = "cria_parametro_tabela_padrao"
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data


@login_required(login_url="login")
def edita_parametro_tabela_padrao(request, idparametro):
    c_form = CadastraParametroTabelaPadrao
    c_idobj = idparametro
    c_url = "/editaparametrotabelapadrao/{}/".format(c_idobj)
    c_view = "edita_parametro_tabela_padrao"
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data


@login_required(login_url="login")
def cria_feriado(request):
    c_chave = request.POST.get("Chave")
    c_valor = request.POST.get("Valor")
    facade.salva_parametro(c_chave, c_valor)
    return redirect("parametro")


@login_required(login_url="login")
def exclui_feriado(request):
    pass
