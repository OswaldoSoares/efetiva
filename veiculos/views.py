from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from .models import Veiculo, CategoriaVeiculo
from pessoas.models import Pessoal, DocPessoal
from .forms import CadastraVeiculo, CadastraCategoria
from clientes.models import TabelaVeiculo

def removeduplicadas(lista):
    novalista = list()
    for i in range(len(lista)):
        if lista[i] not in lista[i+1:]:
            novalista.append(lista[i])
    return novalista


@has_permission_decorator('modulo_veiculos')
def indexveiculo(request):
    meufiltrocategoria = request.GET.get('filtrocategoria', None)
    veiculo = Veiculo.objects.all()
    if meufiltrocategoria:
        veiculo = veiculo.filter(Categoria__Categoria__exact=meufiltrocategoria)
    categoria = CategoriaVeiculo.objects.all()
    return render(request, 'veiculos/index.html', {'veiculo': veiculo, 'categoria': categoria})


def consultaveiculo(request, idvei):
    veiculo = Veiculo.objects.filter(idVeiculo=idvei)
    for x in veiculo:
        idproprietario = (x.Proprietario_id)
        idmotorista = (x.Motorista_id)
    proprietario = Pessoal.objects.filter(idPessoal=idproprietario)
    docproprietario = DocPessoal.objects.filter(idPessoal_id=idproprietario)
    motorista = Pessoal.objects.filter(idPessoal=idmotorista)

    return render(request, 'veiculos/consultaveiculo.html', {'veiculo': veiculo,
                                                             'proprietario': proprietario,
                                                             'docproprietario': docproprietario,
                                                             'motorista': motorista
                                                             })


def criaveiculo(request):
    if request.method == 'POST':
        form = CadastraVeiculo(request.POST)
    else:
        form = CadastraVeiculo()
    return salva_form(request, form, 'veiculos/criaveiculo.html', 0)


def editaveiculo(request, idvei):
    veiculo = get_object_or_404(Veiculo, idVeiculo=idvei)
    if request.method == 'POST':
        form = CadastraVeiculo(request.POST, instance=veiculo)
    else:
        form = CadastraVeiculo(instance=veiculo)
    return salva_form(request, form, 'veiculos/editaveiculo.html', idvei)


def excluiveiculo(request, idvei):
    veiculo = get_object_or_404(Veiculo, idVeiculo=idvei)
    data = dict()
    if request.method == "POST":
        veiculo.delete()
        return redirect('indexveiculo')
    else:
        context = {'veiculo': veiculo}
        data['html_form'] = render_to_string('veiculos/excluiveiculo.html', context, request=request)
    return JsonResponse(data)


def lista_categoria_veiculos(request):
    categoria = CategoriaVeiculo.objects.all()
    return render(request, 'veiculos/listacategoria.html', {'categoria': categoria})


def cria_categoria_veiculos(request):
    form = CadastraCategoria(request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('lista_categoria_veiculos')
    return render(request, 'veiculos/criacategoria.html', {'form': form})


def atualiza_categoria_veiculos(request,id):
    categoria = CategoriaVeiculo.objects.get(idCategoria=id)
    form = CadastraCategoria(request.POST or None, instance=categoria)
    if form.is_valid():
        form.save()
        return redirect('lista_categoria_veiculos')
    return render(request, 'veiculos/criacategoria.html', {'form': form, 'categoria': categoria})


def exclui_categoria_veiculos(request, id):
    categoria = CategoriaVeiculo.objects.get(idCategoria=id)
    try:
        veiculo = Veiculo.objects.filter(Categoria=id)
    except:
        veiculo = ''
    contexto = {'veiculos_list': veiculo, 'categoria': categoria}
    tabelaveiculo = TabelaVeiculo.objects.filter(idCategoriaVeiculo=id)
    tabelaveiculo.delete()
    if request.method == 'POST':
        categoria.delete()
        return redirect('lista_categoria_veiculos')
    return render(request, 'veiculos/excluicategoria.html', contexto)


def salva_form(request, form, template_name, idvei):
    data = dict()
    if request.method == 'POST':
        if form.is_valid():
            form.save()
            data['form_is_valid'] = True
            if template_name == 'veiculos/criaveiculo.html':
                return redirect('indexveiculo')
            else:
                return redirect('consultaveiculo', idvei)
        else:
            data['form_is_valid'] = False
    context = {'form': form}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
