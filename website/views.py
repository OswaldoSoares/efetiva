from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from veiculos.models import CategoriaVeiculo
from .models import Parametros
from .forms import CadastraParametro, CadastraParametroTabelaPadrao
from website import facade


@login_required(login_url='login')
def index_website(request):
    return render(request, 'website/index.html')


def parametros(request):
    # parametro = facade.get_parametros_all()
    # categoria_veiculos = CategoriaVeiculo.objects.all()
    # contexto = {'categoria_veiculos': categoria_veiculos, 'tabela_padrao': tabela_padrao}
    contexto = facade.create_parametro_context()
    return render(request, 'website/parametros.html', contexto)


def cria_parametro(request):
    c_form = CadastraParametro
    c_idobj = None
    c_url = '/criaparametro/'
    c_view = 'cria_parametro'
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data


def cria_parametro_tabela_padrao(request):
    c_form = CadastraParametroTabelaPadrao
    c_idobj = None
    c_url = '/criaparametrotabelapadrao/'
    c_view = 'cria_parametro_tabela_padrao'
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_parametro_tabela_padrao(request, idparametro):
    c_form = CadastraParametroTabelaPadrao
    c_idobj = idparametro
    c_url = '/editaparametrotabelapadrao/{}/'.format(c_idobj)
    c_view = 'edita_parametro_tabela_padrao'
    data = facade.form_parametro(request, c_form, c_idobj, c_url, c_view)
    return data
