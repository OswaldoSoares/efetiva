from django.shortcuts import render, redirect
from .models import Orcamento
from .forms import CadastraOrcamento
from orcamentos import facade


def index_orcamento(request):
    form = CadastraOrcamento()
    return render(request, 'orcamentos/index.html', {'form': form})


def cria_orcamento(request):
    c_form = CadastraOrcamento
    c_idobj = None
    c_url = '/orcamentos/criaorcamento/'
    c_view = 'cria_orcamento'
    data = facade.form_orcamento(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_orcamento(request, idparametro):
    c_form = CadastraOrcamento
    c_idobj = idparametro
    c_url = '/orcamentos/editaorcamento/{}/'.format(c_idobj)
    c_view = 'edita_orcamento'
    data = facade.form_orcamento(request, c_form, c_idobj, c_url, c_view)
    return data


def orcamento_veiculo(request):
    data = facade.get_valor_veiculo(request)
    return data


def orcamento_perimetro(request):
    data = facade.get_porcentagem_perimetro(request)
    return data
