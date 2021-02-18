from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from rolepermissions.decorators import has_permission_decorator

from .forms import CadastraOrcamento
from orcamentos import facade


@login_required(login_url='login')
@has_permission_decorator('modulo_clientes')
def index_orcamento(request):
    contexto = facade.create_orcamento_context()
    return render(request, 'orcamentos/index.html', contexto)


def cria_orcamento(request):
    c_form = CadastraOrcamento
    c_idobj = None
    c_url = '/orcamentos/criaorcamento/'
    c_view = 'cria_orcamento'
    data = facade.form_orcamento(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_orcamento(request, idorcamento):
    c_form = CadastraOrcamento
    c_idobj = idorcamento
    c_url = '/orcamentos/editaorcamento/{}/'.format(c_idobj)
    c_view = 'edita_orcamento'
    data = facade.form_orcamento(request, c_form, c_idobj, c_url, c_view)
    return data


def exclui_orcamento(request, idorcamento):
    c_idobj = idorcamento
    c_url = '/orcamentos/excluiorcamento/{}/'.format(c_idobj)
    c_view = 'exclui_orcamento'
    data = facade.form_exclui_orcamento(request, c_idobj, c_url, c_view)
    return data


def email_orcamento(request, idorcamento):
    c_idobj =idorcamento
    data = facade.create_email(c_idobj)
    return data


def orcamento_veiculo(request):
    data = facade.get_valor_veiculo(request)
    return data


def orcamento_perimetro(request):
    data = facade.get_porcentagem_perimetro(request)
    return data


def orcamento_ajudante():
    data = facade.get_valor_ajudante()
    return data


def orcamento_taxa_expedicao():
    data = facade.get_valor_taxa_expedicao()
    return data
