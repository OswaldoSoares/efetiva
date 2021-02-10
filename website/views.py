from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from veiculos.models import CategoriaVeiculo
from .models import Parametros


@login_required(login_url='login')
def index_website(request):
    return render(request, 'website/index.html')


def parametros(request):
    parametro = Parametros.objects.all()
    categoria_veiculos = CategoriaVeiculo.objects.all()
    contexto = {'categoria_veiculos': categoria_veiculos}
    return render(request, 'website/parametros.html', contexto)
