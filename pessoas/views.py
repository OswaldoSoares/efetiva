from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from .models import Pessoal, DocPessoal, FonePessoal, ContaPessoal
from .forms import CadastraPessoal, CadastraDocPessoal, CadastraFonePessoal, CadastraContaPessoal


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


def criapessoa(request):
    if request.method == 'POST':
        form = CadastraPessoal(request.POST, request.FILES or None)
    else:
        form = CadastraPessoal()
    return salva_form(request, form, 'pessoas/criapessoa.html', 0)


def editapessoa(request, idpes):
    pessoa = get_object_or_404(Pessoal, idPessoal=idpes)
    if request.method == 'POST':
        form = CadastraPessoal(request.POST, request.FILES, instance=pessoa)
    else:
        form = CadastraPessoal(instance=pessoa)
    return salva_form(request, form, 'pessoas/editapessoa.html', idpes)


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


def consultapessoa(request, idpes):
    pessoa = Pessoal.objects.filter(idPessoal=idpes)
    docpessoa = DocPessoal.objects.filter(idPessoal=idpes)
    fonepessoa = FonePessoal.objects.filter(idPessoal=idpes)
    contapessoa = ContaPessoal.objects.filter(idPessoal=idpes)
    if request.method == 'POST':
        redirect('consultapessoa', idpes)
    return render(request, 'pessoas/consultapessoa.html', {'pessoa': pessoa,
                                                           'docpessoa': docpessoa,
                                                           'fonepessoa': fonepessoa,
                                                           'contapessoa': contapessoa})


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
