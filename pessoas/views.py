from django.db.models import Sum
from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from pessoas import facade
from .models import Pessoal, DocPessoal, FonePessoal, ContaPessoal, ContraChequeItens
from .forms import CadastraPessoal, CadastraDocPessoal, CadastraFonePessoal, CadastraContaPessoal, CadastraSalario, \
    CadastraVale
from .print import print_contracheque
from decimal import Decimal


def removeduplicadas(lista):
    novalista = list()
    for i in range(len(lista)):
        if lista[i] not in lista[i+1:]:
            novalista.append(lista[i])
    return novalista


@has_permission_decorator('modulo_colaboradores')
def indexpessoal(request):
    meufiltronome = request.GET.get('filtronome', None)
    meufiltrofuncao = request.GET.get('filtrofuncao', None)
    pessoal = Pessoal.objects.all()
    if meufiltronome:
        pessoal = pessoal.filter(Nome__icontains=meufiltronome)
    elif meufiltrofuncao:
        pessoal = pessoal.filter(Categoria__iexact=meufiltrofuncao)
    categoriaslist = Pessoal.objects.values('Categoria').order_by('Categoria')
    categorias = removeduplicadas(categoriaslist)
    return render(
        request, 'pessoas/index.html', {
            'pessoal': pessoal,
            'categorias': categorias
        }
    )


def cria_pessoa(request):
    print('ok')
    c_form = CadastraPessoal
    c_idobj = None
    c_url = '/pessoas/criapessoa/'
    c_view = 'cria_pessoa'
    idpessoal = None
    data = facade.form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal)
    return data
    # if request.method == 'POST':
    #     form = CadastraPessoal(request.POST, request.FILES or None)
    # else:
    #     form = CadastraPessoal()
    # return salva_form(request, form, 'pessoas/criapessoa.html', 0)


def edita_pessoa(request, idpessoa):
    c_form = CadastraPessoal
    c_idobj = idpessoa
    c_url = '/pessoas/editapessoa/{}/'.format(c_idobj)
    c_view = 'edita_pessoa'
    idpessoal = 'edita_pessoa'
    data = facade.form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal)
    return data
    # pessoa = get_object_or_404(Pessoal, idPessoal=idpes)
    # if request.method == 'POST':
    #     form = CadastraPessoal(request.POST, request.FILES, instance=pessoa)
    # else:
    #     form = CadastraPessoal(instance=pessoa)
    # return salva_form(request, form, 'pessoas/editapessoa.html', idpes)


def excluipessoa(request, idpes):
    pessoa = get_object_or_404(Pessoal, idPessoal=idpes)
    data = dict()
    if request.method == 'POST':
        pessoa.delete()
        return redirect('indexpessoal')
    else:
        context = {'pessoa': pessoa}
        data['html_form'] = render_to_string('pessoas/excluipessoa.html', context, request=request)
    return JsonResponse(data)


def criadocpessoa(request):
    if request.method == 'POST':
        idpessoal = request.POST.get('idPessoal')
        form = CadastraDocPessoal(request.POST or None)
    else:
        idpessoal = request.GET.get('idpessoal')
        form = CadastraDocPessoal(initial={'idPessoal': idpessoal})
    return salva_form(request, form, 'pessoas/criadocpessoa.html', idpessoal)


def excluidocpessoa(request, idpesdoc):
    docpessoa = get_object_or_404(DocPessoal, idDocPessoal=idpesdoc)
    data = dict()
    if request.method == 'POST':
        docpessoa.delete()
        return redirect('consultapessoa', docpessoa.idPessoal_id)
    else:
        context = {'docpessoa': docpessoa}
        data['html_form'] = render_to_string('pessoas/excluidocpessoa.html', context, request=request)
    return JsonResponse(data)


def criafonepessoa(request):
    if request.method == 'POST':
        idpessoal = request.POST.get('idPessoal')
        form = CadastraFonePessoal(request.POST or None)
    else:
        idpessoal = request.GET.get('idpessoal')
        form = CadastraFonePessoal(initial={'idPessoal': idpessoal})
    return salva_form(request, form, 'pessoas/criafonepessoa.html', idpessoal)


def excluifonepessoa(request, idpesfon):
    fonepessoa = get_object_or_404(FonePessoal, idFonePessoal=idpesfon)
    data = dict()
    if request.method == 'POST':
        fonepessoa.delete()
        return redirect('consultapessoa', fonepessoa.idPessoal_id)
    else:
        context = {'fonepessoa': fonepessoa}
        data['html_form'] = render_to_string('pessoas/excluifonepessoa.html', context, request=request)
    return JsonResponse(data)


def criacontapessoa(request):
    if request.method == 'POST':
        idpessoal = request.POST.get('idPessoal')
        form = CadastraContaPessoal(request.POST or None)
    else:
        idpessoal = request.GET.get('idpessoal')
        form = CadastraContaPessoal(initial={'idPessoal': idpessoal})
    return salva_form(request, form, 'pessoas/criacontapessoa.html', idpessoal)


def excluicontapessoa(request, idpescon):
    contapessoa = get_object_or_404(ContaPessoal, idContaPessoal=idpescon)
    data = dict()
    if request.method == 'POST':
        contapessoa.delete()
        return redirect('consultapessoa', contapessoa.idPessoal_id)
    else:
        context = {'contapessoa': contapessoa}
        data['html_form'] = render_to_string('pessoas/excluicontapessoa.html', context, request=request)
    return JsonResponse(data)


def consulta_pessoa(request, idpessoa):
    contexto = facade.create_pessoal_context(idpessoa)
    # if request.method == 'POST':
    #     redirect('consultapessoa', idpessoa)
    return render(request, 'pessoas/consultapessoa.html', contexto)


def salva_form(request, form, template_name, idpes):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            if template_name == 'pessoas/criapessoa.html':
                return redirect('indexpessoal')
            else:
                return redirect('consultapessoa', idpes)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)



def edita_salario(request):
    c_pessoal = request.POST.get('idPessoal')
    c_salario = request.POST.get('Salario')
    c_horas_mensais = float(request.POST.get('HorasMensais'))
    facade.save_salario(c_pessoal, c_salario, c_horas_mensais)
    return redirect('consultapessoa', c_pessoal)


def cria_vale(request):
    c_data = request.POST.get('Data')
    c_descricao = request.POST.get('Descricao')
    c_valor = request.POST.get('Valor')
    c_pessoal = request.POST.get('idPessoal')
    facade.create_vale(c_data, c_descricao, c_valor, c_pessoal)
    return render(request, 'pessoas/consultapessoa.html')


def cria_contracheque(request):
    c_mesreferencia = request.POST.get('MesReferencia')
    c_anoreferencia = request.POST.get('AnoReferencia')
    c_valor = 0.00
    c_pessoal = request.POST.get('idPessoal')
    facade.create_contracheque(c_mesreferencia, c_anoreferencia, c_valor, c_pessoal)
    return redirect('consultapessoa', c_pessoal)


def seleciona_contracheque(request):
    c_idpessoal = request.GET.get('idpessoal')
    c_mes = request.GET.get('mes')
    c_ano = request.GET.get('ano')
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpessoal)
    return data


def cria_contrachequeitens(request):
    c_idcontracheque = request.POST.get('idContraCheque')
    c_descricao = request.POST.get('Descricao')
    c_valor = request.POST.get('Valor')
    c_registro = request.POST.get('Registro')
    c_mes = request.POST.get('MesReferencia')
    c_ano = request.POST.get('AnoReferencia')
    c_idpessoal = request.POST.get('idPessoal')
    facade.create_contracheque_itens(c_descricao, c_valor, c_registro, c_idcontracheque)
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpessoal)
    return data


def imprime_contracheque(request, idcontracheque):
    contexto = facade.print_contracheque_context(idcontracheque)
    response = print_contracheque(contexto)
    return response
