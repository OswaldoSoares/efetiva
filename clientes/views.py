from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from clientes import facade
from .models import Cliente, FoneContatoCliente, EMailContatoCliente, Cobranca, Tabela, TabelaVeiculo, \
    TabelaCapacidade, TabelaPerimetro
from .forms import CadastraCliente, CadastraFoneContatoCliente, CadastraEMailContatoCliente, CadastraCobranca,\
    CadastraTabela, CadastraTabelaVeiculo, CadastraTabelaCapacidade, CadastraTabelaPerimetro, CadastraFormaPgto
from veiculos.models import CategoriaVeiculo


@has_permission_decorator('modulo_clientes')
def indexcliente(request):
    meufiltrofantasia = request.GET.get('filtrofantasia', None)
    meufiltronome = request.GET.get('filtronome', None)
    cliente = facade.list_cliente_all()
    if meufiltrofantasia:
        cliente = cliente.filter(Fantasia__icontains=meufiltrofantasia)
    elif meufiltronome:
        cliente = cliente.filter(Nome__icontains=meufiltronome)
    return render(request, 'clientes/index.html', {'cliente': cliente})


@has_permission_decorator('modulo_clientes')
def consultacliente(request, idcli):
    contexto = facade.create_cliente_context(idcli)
    contexto_veiculo = {'categoria_veiculo': facade.get_categoria_veiculo()}
    contexto.update(contexto_veiculo)
    return render(request, 'clientes/consultacliente.html', contexto)


def criacliente(request):
    if request.method == 'POST':
        form = CadastraCliente(request.POST)
    else:
        form = CadastraCliente()
    return salva_form(request, form, 'clientes/criacliente.html', 0)


def editacliente(request, idcli):
    cliente = get_object_or_404(Cliente, idCliente=idcli)
    if request.method == 'POST':
        form = CadastraCliente(request.POST, instance=cliente)
    else:
        form = CadastraCliente(instance=cliente)
    return salva_form(request, form, 'clientes/editacliente.html', idcli)


def excluicliente(request, idcli):
    cliente = get_object_or_404(Cliente, idCliente=idcli)
    data = dict()
    if request.method == "POST":
        cliente.delete()
        return redirect('indexcliente')
    else:
        context = {'cliente': cliente}
        data['html_form'] = render_to_string('clientes/excluicliente.html', context, request=request)
    return JsonResponse(data)


def criaemailcliente(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraEMailContatoCliente(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        form = CadastraEMailContatoCliente(initial={'idCliente': idcliente})
    return salva_form(request, form, 'clientes/criaemailcliente.html', idcliente)


def editaemailcliente(request, idemacon):
    emailcliente = get_object_or_404(EMailContatoCliente, idEmailContatoCliente=idemacon)
    if request.method == 'POST':
        form = CadastraEMailContatoCliente(request.POST, instance=emailcliente)
    else:
        form = CadastraEMailContatoCliente(instance=emailcliente)
    return salva_form(request, form, 'clientes/editaemailcliente.html', emailcliente.idCliente_id)


def excluiemailcliente(request, idemacon):
    emailcliente = get_object_or_404(EMailContatoCliente, idEmailContatoCliente=idemacon)
    data = dict()
    if request.method == "POST":
        emailcliente.delete()
        return redirect('consultacliente', emailcliente.idCliente_id)
    else:
        context = {'emailcliente': emailcliente}
        data['html_form'] = render_to_string('clientes/excluiemailcliente.html', context, request=request)
    return JsonResponse(data)


def criafonecliente(request):
    if request.method == 'POST':
        idcliente = request.POST.get('idCliente')
        form = CadastraFoneContatoCliente(request.POST)
    else:
        idcliente = request.GET.get('idcliente')
        form = CadastraFoneContatoCliente(initial={'idCliente': idcliente})
    return salva_form(request, form, 'clientes/criafonecliente.html', idcliente)


def editafonecliente(request, idfoncon):
    fonecliente = get_object_or_404(FoneContatoCliente, idFoneContatoCliente=idfoncon)
    if request.method == 'POST':
        form = CadastraFoneContatoCliente(request.POST, instance=fonecliente)
    else:
        form = CadastraFoneContatoCliente(instance=fonecliente)
    return salva_form(request, form, 'clientes/editafonecliente.html', fonecliente.idCliente_id)


def excluifonecliente(request, idfoncon):
    fonecliente = get_object_or_404(FoneContatoCliente, idFoneContatoCliente=idfoncon)
    data = dict()
    if request.method == "POST":
        fonecliente.delete()
        return redirect('consultacliente', fonecliente.idCliente_id)
    else:
        context = {'fonecliente': fonecliente}
        data['html_form'] = render_to_string('clientes/excluifonecliente.html', context, request=request)
    return JsonResponse(data)


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
            if template_name == 'clientes/criacliente.html':
                return redirect('indexcliente')
            else:
                return redirect('consultacliente', idcli)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
