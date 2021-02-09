from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from rolepermissions.decorators import has_permission_decorator
from clientes import facade
from .models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca, Tabela, TabelaVeiculo, \
    TabelaCapacidade, TabelaPerimetro
from .forms import CadastraCliente, CadastraFoneContatoCliente, CadastraEMailContatoCliente, CadastraCobranca,\
    CadastraTabela, CadastraTabelaVeiculo, CadastraTabelaCapacidade, CadastraTabelaPerimetro, CadastraFormaPgto
from veiculos.models import CategoriaVeiculo


@login_required(login_url='login')
@has_permission_decorator('modulo_clientes')
def index_cliente(request):
    contexto = facade.create_cliente_filter_context(request)
    return render(request, 'clientes/index.html', contexto)


# @has_permission_decorator('modulo_clientes')
def consulta_cliente(request, idcliente):
    contexto = facade.create_cliente_context(idcliente)
    contexto_veiculo = {'categoria_veiculo': facade.get_categoria_veiculo()}
    contexto.update(contexto_veiculo)
    return render(request, 'clientes/consultacliente.html', contexto)


def cria_cliente(request):
    c_form = CadastraCliente
    c_idobj = None,
    c_url = '/clientes/criacliente/'
    c_view = 'cria_cliente'
    idcliente = None
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_cliente(request, idcliente):
    c_form = CadastraCliente
    c_idobj = idcliente
    c_url = '/clientes/editacliente/{}/'.format(c_idobj)
    c_view = 'edita_cliente'
    idcliente = idcliente
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_cliente(request, idcliente):
    c_idobj = idcliente
    c_url = '/clientes/excluicliente/{}/'.format(c_idobj)
    c_view = 'exclui_cliente'
    idcliente = idcliente
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_email_cliente(request):
    c_form = CadastraEMailContatoCliente
    c_idobj = None
    c_url = '/clientes/criaemailcliente/'
    c_view = 'cria_email_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_email_cliente(request, idclienteemail):
    c_form = CadastraEMailContatoCliente
    c_idobj = idclienteemail
    c_url = '/clientes/editaemailcliente/{}/'.format(c_idobj)
    c_view = 'edita_email_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_email_cliente(request, idclienteemail):
    c_idobj = idclienteemail
    c_url = '/clientes/excluiemailcliente/{}/'.format(c_idobj)
    c_view = 'exclui_email_cliente'
    idcliente = request.POST.get('idCliente')
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_fone_cliente(request):
    c_form = CadastraFoneContatoCliente
    c_idobj = None
    c_url = '/clientes/criafonecliente/'
    c_view = 'cria_fone_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_fone_cliente(request, idclientefone):
    c_form = CadastraFoneContatoCliente
    c_idobj = idclientefone
    c_url = '/clientes/editafonecliente/{}/'.format(c_idobj)
    c_view = 'edita_fone_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_fone_cliente(request, idclientefone):
    c_idobj = idclientefone
    c_url = '/clientes/excluifonecliente/{}/'.format(c_idobj)
    c_view = 'exclui_fone_cliente'
    idcliente = request.POST.get('idCliente')
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_cobranca_cliente(request):
    c_form = CadastraCobranca
    c_idobj = None
    c_url = '/clientes/criacobrancacliente/'
    c_view = 'cria_cobranca_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_cobranca_cliente(request, idcobrancacliente):
    c_form = CadastraCobranca
    c_idobj = idcobrancacliente
    c_url = '/clientes/editacobrancacliente/{}/'.format(c_idobj)
    c_view = 'edita_cobranca_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def exclui_cobranca_cliente(request, idcobrancacliente):
    c_idobj = idcobrancacliente
    c_url = '/clientes/excluicobrancacliente/{}/'.format(c_idobj)
    c_view = 'exclui_cobranca_cliente'
    idcliente = request.POST.get('idCliente')
    data = facade.form_exclui_cliente(request, c_idobj, c_url, c_view, idcliente)
    return data


def cria_tabela_cliente(request):
    c_form = CadastraTabela
    c_idobj = None
    c_url = '/clientes/criatabelacliente/'
    c_view = 'cria_tabela_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_tabela_cliente(request, idclientetabela):
    c_form = CadastraTabela
    c_idobj = idclientetabela
    c_url = '/clientes/editatabelacliente/{}/'.format(c_idobj)
    c_view = 'edita_tabela_cliente'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data


def edita_phkesc(request, idclientetabela):
    phkesc_cobra, phkesc_paga = facade.phkesc(dict(request.POST.lists()))
    data = facade.save_phkesc(idclientetabela, phkesc_cobra, phkesc_paga)
    return data


def cria_tabela_veiculo(request):
    c_form = CadastraTabelaVeiculo
    c_idobj = None
    c_url = '/clientes/criatabelaveiculo/'
    c_view = 'cria_tabela_veiculo'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data
    # if request.method == 'POST':
    #     idcliente = request.POST.get('idCliente')
    #     form = CadastraTabelaVeiculo(request.POST)
    # else:
    #     idcliente = request.GET.get('idcliente')
    #     idcategoriaveiculo = request.GET.get('idcategoriaveiculo')
    #     form = CadastraTabelaVeiculo(initial={
    #         'idCliente': idcliente, 'idCategoriaVeiculo': idcategoriaveiculo})
    # return salva_form(request, form, 'clientes/criatabelaveiculo.html', idcliente)


def edita_tabela_veiculo(request, idtabelaveiculo):
    c_form = CadastraTabelaVeiculo
    c_idobj = idtabelaveiculo
    c_url = '/clientes/editatabelaveiculo/{}/'.format(c_idobj)
    c_view = 'edita_tabela_veiculo'
    idcliente = request.GET.get('idcliente')
    data = facade.form_cliente(request, c_form, c_idobj, c_url, c_view, idcliente)
    return data
    # tabelaveiculo = get_object_or_404(TabelaVeiculo, idTabelaVeiculo=idtabvei)
    # if request.method == 'POST':
    #     form = CadastraTabelaVeiculo(request.POST, instance=tabelaveiculo)
    # else:
    #     form = CadastraTabelaVeiculo(instance=tabelaveiculo)
    # return salva_form(request, form, 'clientes/editatabelaveiculo.html', tabelaveiculo.idCliente_id)


def selecionatabelaveiculo(request):
    data = dict()
    selecionaveiculo = request.GET.get('selecionaveiculo')
    selecionacliente = request.GET.get('selecionacliente')
    tabelaveiculocliente = TabelaVeiculo.objects.filter(idCategoriaVeiculo=selecionaveiculo,
                                                        idCliente=selecionacliente).values()
    selecionatabelaveiculo = list(tabelaveiculocliente)
    tabelacategoriaveiculo = CategoriaVeiculo.objects.filter(idCategoria=selecionaveiculo).values()
    selecionaveiculo = list(tabelacategoriaveiculo)
    context = {
        'selecionatabelaveiculo': selecionatabelaveiculo,
        'selecionaveiculo': selecionaveiculo
    }
    data['html_tabelaveiculo'] = render_to_string('clientes/selecionatabelaveiculo.html', context, request=request)
    return JsonResponse(data)


def criatabelacapacidade(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraTabelaCapacidade(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        registros = TabelaCapacidade.objects.filter(idCliente=idcliente).values()
        if registros:
            ultimoregistro = registros[len(registros) - 1]
            peso = ultimoregistro['CapacidadeFinal']
        else:
            peso = 0
        form = CadastraTabelaCapacidade(initial={'idCliente': idcliente, 'CapacidadeInicial': peso+1,
                                                 'CapacidadeFinal': peso+2})
    return salva_form(request, form, 'clientes/criatabelacapacidade.html', idcliente)


def editatabelacapacidade(request, idtabcap):
    tabelacapacidade = get_object_or_404(TabelaCapacidade, idTabelaCapacidade=idtabcap)
    if request.method == 'POST':
        requestcopia = request.POST.copy()
        requestcopia['CapacidadeFinal'] = tabelacapacidade.CapacidadeFinal
        form = CadastraTabelaCapacidade(requestcopia, instance=tabelacapacidade)
    else:
        form = CadastraTabelaCapacidade(instance=tabelacapacidade)
    return salva_form(request, form, 'clientes/editatabelacapacidade.html', tabelacapacidade.idCliente_id)


def excluitabelacapacidade(request, idtabcap):
    tabelacapacidade = get_object_or_404(TabelaCapacidade, idTabelaCapacidade=idtabcap)
    cliente = Cliente.objects.get(Nome=tabelacapacidade.idCliente)
    data = dict()
    if request.method == "POST":
        tabelacapacidade.delete()
        return redirect('consultacliente', cliente.idCliente)
    else:
        context = {'tabelacapacidade': tabelacapacidade}
        data['html_form'] = render_to_string('clientes/excluitabelacapacidade.html', context, request=request)
    return JsonResponse(data)


def criatabelaperimetro(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraTabelaPerimetro(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        registros = TabelaPerimetro.objects.filter(idCliente=idcliente).values()
        if registros:
            ultimoregistro = registros[len(registros)-1]
            kms = ultimoregistro['PerimetroFinal']
        else:
            kms = 0
        form = CadastraTabelaPerimetro(initial={'idCliente': idcliente,
                                                'PerimetroInicial': kms+1,
                                                'PerimetroFinal': kms+2})
    return salva_form(request, form, 'clientes/criatabelaperimetro.html', idcliente)


def criaformapgto(request):
    if request.method == 'POST':
        formapgto = CadastraFormaPgto(request.POST)
        formapgto.save()
    else:
        formapgto = CadastraFormaPgto()
    return render(request, 'clientes/criaformapgto.html', {'formapgto': formapgto})


def editatabelaperimetro(request, idtabper):
    tabelaperimetro = get_object_or_404(TabelaPerimetro, idTabelaPerimetro=idtabper)
    if request.method == 'POST':
        requestcopia = request.POST.copy()
        requestcopia['PerimetroFinal'] = tabelaperimetro.PerimetroFinal
        form = CadastraTabelaPerimetro(requestcopia, instance=tabelaperimetro)
    else:
        form = CadastraTabelaPerimetro(instance=tabelaperimetro)
    return salva_form(request, form, 'clientes/editatabelaperimetro.html', tabelaperimetro.idCliente_id)


def excluitabelaperimetro(request, idtabper):
    tabelaperimetro = get_object_or_404(TabelaPerimetro, idTabelaPerimetro=idtabper)
    cliente = Cliente.objects.get(Fantasia=tabelaperimetro.idCliente)
    data = dict()
    if request.method == "POST":
        tabelaperimetro.delete()
        return redirect('consultacliente', cliente.idCliente)
    else:
        context = {'tabelaperimetro': tabelaperimetro}
        data['html_form'] = render_to_string('clientes/excluitabelaperimetro.html', context, request=request)
    return JsonResponse(data)


def salva_form(request, form, template_name, idcli):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            return redirect('consultacliente', idcli)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
