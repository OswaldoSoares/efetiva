from django.urls import path
from .views import index_pagamento, teste, cria_folha, cria_contrachequeitens, exclui_contrachequeitens, \
    seleciona_folha, seleciona_contracheque, inserefalta, edita_cartaoponto, seleciona_periodo, \
    seleciona_saldoavulso, cria_pagamento, cria_vale, exclui_vale, exclui_recibo, imprime_recibo, \
    cria_contrachequeitensvale, exclui_contrachequeitensvale, imprime_contracheque, manutencao, apagar_tudo

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
    path('selecionasaldoavulso', seleciona_saldoavulso, name='selecionasaldoavulso'),
    path('criapagamento', cria_pagamento, name='criapagamento'),
    path('criavale', cria_vale, name='criavale'),
    path('excluivale', exclui_vale, name='excluivale'),
    path('excluirecibo', exclui_recibo, name='excluirecibo'),
    path('imprimerecibo', imprime_recibo, name='imprimerecibo'),
    path('criacontrachequeitensvale', cria_contrachequeitensvale, name='criacontrachequeitensvale'),
    path('excluicontrachequeitensvale', exclui_contrachequeitensvale, name='excluicontrachequeitensvale'),
    path('imprimecontracheque/', imprime_contracheque, name='imprimecontracheque'),
    path('manutencao', manutencao),
    path('apaga', apagar_tudo, name='apaga')
]
