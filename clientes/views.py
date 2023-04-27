from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from clientes import facade
from .models import (
    Cliente,
    FoneContatoCliente,
    EMailContatoCliente,
    Cobranca,
    Tabela,
    TabelaVeiculo,
    TabelaCapacidade,
    TabelaPerimetro,
)
from .forms import (
    CadastraCliente,
    CadastraFoneContatoCliente,
    CadastraEMailContatoCliente,
    CadastraCobranca,
    CadastraTabela,
    CadastraTabelaVeiculo,
    CadastraTabelaCapacidade,
    CadastraTabelaPerimetro,
    CadastraFormaPgto,
)
from veiculos.models import CategoriaVeiculo


@has_permission_decorator("modulo_clientes")
def index_cliente(request):
    contexto = facade.create_cliente_filter_context(request)
    return render(request, "clientes/index.html", contexto)


# @has_permission_decorator('modulo_clientes')
def consulta_cliente(request, idcliente):
    contexto = facade.create_cliente_context(idcliente)
    contexto_veiculo = {"categoria_veiculo": facade.get_categoria_veiculo()}
    contexto.update(contexto_veiculo)
    return render(request, "clientes/consultacliente.html", contexto)


def cria_cliente(request):
    c_form = CadastraCliente
    c_idobj = None
    c_url = "/clientes/criacliente/"
    c_view = "cria_cliente"
    idcliente = None
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_cliente(request, idcliente):
    c_form = CadastraCliente
    c_idobj = idcliente
    c_url = "/clientes/editacliente/{}/".format(c_idobj)
    c_view = "edita_cliente"
    idcliente = idcliente
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_cliente(request, idcliente):
    c_idobj = idcliente
    c_url = "/clientes/excluicliente/{}/".format(c_idobj)
    c_view = "exclui_cliente"
    idcliente = idcliente
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_email_cliente(request):
    c_form = CadastraEMailContatoCliente
    c_idobj = None
    c_url = "/clientes/criaemailcliente/"
    c_view = "cria_email_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_email_cliente(request, idclienteemail):
    c_form = CadastraEMailContatoCliente
    c_idobj = idclienteemail
    c_url = "/clientes/editaemailcliente/{}/".format(c_idobj)
    c_view = "edita_email_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_email_cliente(request, idclienteemail):
    c_idobj = idclienteemail
    c_url = "/clientes/excluiemailcliente/{}/".format(c_idobj)
    c_view = "exclui_email_cliente"
    idcliente = request.POST.get("idCliente")
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_fone_cliente(request):
    c_form = CadastraFoneContatoCliente
    c_idobj = None
    c_url = "/clientes/criafonecliente/"
    c_view = "cria_fone_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_fone_cliente(request, idclientefone):
    c_form = CadastraFoneContatoCliente
    c_idobj = idclientefone
    c_url = "/clientes/editafonecliente/{}/".format(c_idobj)
    c_view = "edita_fone_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_fone_cliente(request, idclientefone):
    c_idobj = idclientefone
    c_url = "/clientes/excluifonecliente/{}/".format(c_idobj)
    c_view = "exclui_fone_cliente"
    idcliente = request.POST.get("idCliente")
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_cobranca_cliente(request):
    c_form = CadastraCobranca
    c_idobj = None
    c_url = "/clientes/criacobrancacliente/"
    c_view = "cria_cobranca_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_cobranca_cliente(request, idcobrancacliente):
    c_form = CadastraCobranca
    c_idobj = idcobrancacliente
    c_url = "/clientes/editacobrancacliente/{}/".format(c_idobj)
    c_view = "edita_cobranca_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_cobranca_cliente(request, idcobrancacliente):
    c_idobj = idcobrancacliente
    c_url = "/clientes/excluicobrancacliente/{}/".format(c_idobj)
    c_view = "exclui_cobranca_cliente"
    idcliente = request.POST.get("idCliente")
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_tabela_cliente(request):
    c_form = CadastraTabela
    c_idobj = None
    c_url = "/clientes/criatabelacliente/"
    c_view = "cria_tabela_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_tabela_cliente(request, idclientetabela):
    c_form = CadastraTabela
    c_idobj = idclientetabela
    c_url = "/clientes/editatabelacliente/{}/".format(c_idobj)
    c_view = "edita_tabela_cliente"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_phkesc(request, idclientetabela):
    phkesc_cobra, phkesc_paga = facade.phkesc(dict(request.POST.lists()))
    data = facade.save_phkesc(idclientetabela, phkesc_cobra, phkesc_paga)
    return data


def cria_tabela_veiculo(request):
    c_form = CadastraTabelaVeiculo
    c_idobj = None
    c_url = "/clientes/criatabelaveiculo/"
    c_view = "cria_tabela_veiculo"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_tabela_veiculo(request, idtabelaveiculo):
    c_form = CadastraTabelaVeiculo
    c_idobj = idtabelaveiculo
    c_url = "/clientes/editatabelaveiculo/{}/".format(c_idobj)
    c_view = "edita_tabela_veiculo"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def cria_tabela_capacidade(request):
    c_form = CadastraTabelaCapacidade
    c_idobj = None
    c_url = "/clientes/criatabelacapacidade/"
    c_view = "cria_tabela_capacidade"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_tabela_capacidade(request, idtabelacapacidade):
    c_form = CadastraTabelaCapacidade
    c_idobj = idtabelacapacidade
    c_url = "/clientes/editatabelacapacidade/{}/".format(c_idobj)
    c_view = "edita_tabela_capacidade"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_tabela_capacidade(request, idtabelacapacidade):
    c_idobj = idtabelacapacidade
    c_url = "/clientes/excluitabelacapacidade/{}/".format(c_idobj)
    c_view = "exclui_tabela_capacidade"
    idcliente = request.POST.get("idCliente")
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_tabela_perimetro(request):
    c_form = CadastraTabelaPerimetro
    c_idobj = None
    c_url = "/clientes/criatabelaperimetro/"
    c_view = "cria_tabela_perimetro"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def criaformapgto(request):
    if request.method == "POST":
        formapgto = CadastraFormaPgto(request.POST)
        formapgto.save()
    else:
        formapgto = CadastraFormaPgto()
    return render(request, "clientes/criaformapgto.html", {"formapgto": formapgto})


def edita_tabela_perimetro(request, idtabelaperimetro):
    c_form = CadastraTabelaPerimetro
    c_idobj = idtabelaperimetro
    c_url = "/clientes/editatabelaperimetro/{}/".format(c_idobj)
    c_view = "edita_tabela_perimetro"
    idcliente = request.GET.get("idcliente")
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_tabela_perimetro(request, idtabelaperimetro):
    c_idobj = idtabelaperimetro
    c_url = "/clientes/excluitabelaperimetro/{}/".format(c_idobj)
    c_view = "exclui_tabela_perimetro"
    idcliente = request.POST.get("idCliente")
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


# def salva_form(request, form, template_name, idcli):
#     data = dict()
#     if request.method == 'POST':
#         if form.is_valid():
#             form.save()
#             data['form_is_valid'] = True
#             return redirect('consultacliente', idcli)
#         else:
#             data['form_is_valid'] = False
#     context = {'form': form}
#     data['html_form'] = render_to_string(template_name, context, request=request)
#     return JsonResponse(data)
