from django.urls import path
from .views import index_pagamento, teste, cria_folha, seleciona_folha

urlpatterns = [
    path('', index_pagamento, name='index_pagamento'),
    path('teste', teste, name='teste'),
    path('criafolha', cria_folha, name='criafolha'),
    path('selecionafolha', seleciona_folha, name='selecionafolha')
]
