from django.urls import path
from .views import index_pagamento, teste, cria_folha, cria_contrachequeitens, exclui_contrachequeitens, \
    seleciona_folha, seleciona_contracheque, inserefalta, edita_cartaoponto, seleciona_periodo, cria_vale, \
    manutencao, apagar_tudo

urlpatterns = [
    path('', index_pagamento, name='index_pagamento'),
    path('teste', teste, name='teste'),
    path('criafolha', cria_folha, name='criafolha'),
    path('selecionafolha', seleciona_folha, name='selecionafolha'),
    path('selecionacontracheque', seleciona_contracheque, name='selecionacontracheque'),
    path('criacontrachequeitens', cria_contrachequeitens, name='criacontrachequeitens'),
    path('excluicontrachequeitens', exclui_contrachequeitens, name='excluicontrachequeitens'),
    path('inserefalta', inserefalta, name='inserefalta'),
    path('editacartaoponto/<int:idcartaoponto>/', edita_cartaoponto, name='editacartaoponto'),
    path('selecionaperiodo', seleciona_periodo, name='selecionaperiodo'),
    path('criavale', cria_vale, name='criavale'),
    path('manutencao', manutencao),
    path('apaga', apagar_tudo, name='apaga')
]
