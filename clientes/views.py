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


def criacobrancacliente(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraCobranca(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        form = CadastraCobranca(initial={'idCliente': idcliente})
    return salva_form(request, form, 'clientes/criacobrancacliente.html', idcliente)


def editacobrancacliente(request, idcobcli):
    cobrancacliente = get_object_or_404(Cobranca, idCobranca=idcobcli)
    if request.method == 'POST':
        form = CadastraCobranca(request.POST, instance=cobrancacliente)
    else:
        form = CadastraCobranca(instance=cobrancacliente)
    return salva_form(request, form, 'clientes/editacobrancacliente.html', cobrancacliente.idCliente_id)


def excluicobrancacliente(request, idcobcli):
    cobrancacliente = get_object_or_404(Cobranca, idCobranca=idcobcli)
    data = dict()
    if request.method == "POST":
        cobrancacliente.delete()
        return redirect('consultacliente', cobrancacliente.idCliente_id)
    else:
        context = {'cobrancacliente': cobrancacliente}
        data['html_form'] = render_to_string('clientes/excluicobrancacliente.html', context, request=request)
    return JsonResponse(data)


def criatabelacliente(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraTabela(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        form = CadastraTabela(initial={'idCliente': idcliente})
    return salva_form(request, form, 'clientes/criatabelacliente.html', idcliente)


def editatabelacliente(request, idtabcli):
    tabelacliente = get_object_or_404(Tabela, idTabela=idtabcli)
    if request.method == "POST":
        form = CadastraTabela(request.POST, instance=tabelacliente)
    else:
        form = CadastraTabela(instance=tabelacliente)
    return salva_form(request, form, 'clientes/editatabelacliente.html', tabelacliente.idCliente_id)


def editaphkesc(request, idtabcli):
    tabelacliente = get_object_or_404(Tabela, idTabela=idtabcli)
    if request.method == 'POST':
        switchdict = dict(request.POST.lists())
        phkesccobra = '00000000'
        phkescpaga = '00000000'
        if 'switch' in switchdict:
            switchlist = switchdict['switch']
            pc, hc, kc, ec, sc, cc, ekc, evc = '0', '0', '0', '0', '0', '0', '0', '0'
            pp, hp, kp, ep, sp, cp, ekp, evp = '0', '0', '0', '0', '0', '0', '0', '0'
            if switchlist:
                if 'porcentagem-cobra' in switchlist:
                    pc = '1'
                if 'hora-cobra' in switchlist:
                    hc = '1'
                if 'kilometragem-cobra' in switchlist:
                    kc = '1'
                if 'entrega-cobra' in switchlist:
                    ec = '1'
                if 'entregakg-cobra' in switchlist:
                    ekp = '1'
                if 'entregavolume-cobra' in switchlist:
                    ekv = '1'
                if 'saida-cobra' in switchlist:
                    sc = '1'
                if 'capacidade-cobra' in switchlist:
                    cc = '1'
                if 'porcentagem-paga' in switchlist:
                    pp = '1'
                if 'hora-paga' in switchlist:
                    hp = '1'
                if 'kilometragem-paga' in switchlist:
                    kp = '1'
                if 'entrega-paga' in switchlist:
                    ep = '1'
                if 'entregakg-paga' in switchlist:
                    ekp = '1'
                if 'entregavolume-paga' in switchlist:
                    ekv = '1'
                if 'saida-paga' in switchlist:
                    sp = '1'
                if 'capacidade-paga' in switchlist:
                    cp = '1'
                phkesccobra = pc + hc + kc + ec + sc + cc + ekc + evc
                phkescpaga = pp + hp + kp + ep + sp + cp + ekp + evp
        obj = Tabela()
        obj.idTabela = tabelacliente.idTabela
        obj.Comissao = tabelacliente.Comissao
        obj.TaxaExpedicao = tabelacliente.TaxaExpedicao
        obj.AjudanteCobra = tabelacliente.AjudanteCobra
        obj.AjudantePaga = tabelacliente.AjudantePaga
        obj.phkescCobra = phkesccobra
        obj.phkescPaga = phkescpaga
        obj.idFormaPagamento = tabelacliente.idFormaPagamento
        obj.idCliente = tabelacliente.idCliente
        obj.save()
    return redirect('consultacliente', tabelacliente.idCliente_id)


def criatabelaveiculo(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraTabelaVeiculo(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        idcategoriaveiculo = request.GET.get('idcategoriaveiculo')
        form = CadastraTabelaVeiculo(initial={
            'idCliente': idcliente, 'idCategoriaVeiculo': idcategoriaveiculo})
    return salva_form(request, form, 'clientes/criatabelaveiculo.html', idcliente)


def editatabelaveiculo(request, idtabvei):
    tabelaveiculo = get_object_or_404(TabelaVeiculo, idTabelaVeiculo=idtabvei)
    if request.method == 'POST':
        form = CadastraTabelaVeiculo(request.POST, instance=tabelaveiculo)
    else:
        form = CadastraTabelaVeiculo(instance=tabelaveiculo)
    return salva_form(request, form, 'clientes/editatabelaveiculo.html', tabelaveiculo.idCliente_id)


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
