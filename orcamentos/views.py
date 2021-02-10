from django.shortcuts import render, redirect
from .models import Orcamento
from .forms import CadastraOrcamento


def index_orcamento(request):
    form = CadastraOrcamento()
    return render(request, 'orcamentos/index.html', {'form': form})
