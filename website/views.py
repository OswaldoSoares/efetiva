from django.shortcuts import render
from veiculos.models import CategoriaVeiculo


def index_website(request):
    return render(request, 'website/index.html')


def parametros(request):
    categoria_veiculos = CategoriaVeiculo.objects.all()
    contexto = {'categoria_veiculos': categoria_veiculos}
    return render(request, 'website/parametros.html', contexto)
