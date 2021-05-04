from django.urls import path
from .views import index_pagamento, teste, cria_folha, cria_contrachequeitens, seleciona_folha, \
    seleciona_contracheque, manutencao, apagar_tudo

urlpatterns = [
    path('', index_pagamento, name='index_pagamento'),
    path('teste', teste, name='teste'),
    path('criafolha', cria_folha, name='criafolha'),
    path('selecionafolha', seleciona_folha, name='selecionafolha'),
    path('selecionacontracheque', seleciona_contracheque, name='selecionacontracheque'),
    path('criacontrachequeitens', cria_contrachequeitens, name='criacontrachequeitens'),
    path('manutencao', manutencao),
    path('apaga', apagar_tudo, name='apaga')
]
