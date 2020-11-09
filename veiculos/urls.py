from django.urls import path
from .views import indexveiculo, \
    consultaveiculo, \
    criaveiculo, \
    editaveiculo, \
    excluiveiculo, \
    lista_categoria_veiculos, cria_categoria_veiculos,\
    atualiza_categoria_veiculos,exclui_categoria_veiculos

urlpatterns = [
    path('',
         indexveiculo,
         name='indexveiculo'
     ),
    path(
        'consultaveiculo/<int:idvei>/',
        consultaveiculo,
        name='consultaveiculo'
    ),
    path(
        'criaveiculo/',
        criaveiculo,
        name='criaveiculo'
    ),
    path(
        'editaveiculo/<int:idvei>/',
        editaveiculo,
        name='editaveiculo'
    ),
    path(
        'excluiveiculo/<int:idvei>/',
        excluiveiculo,
        name='excluiveiculo'
    ),
    path('listacategoria/', lista_categoria_veiculos, name='lista_categoria_veiculos'),
    path('criacategoria/', cria_categoria_veiculos, name='cria_categoria_veiculos'),
    path('atualizacategoria/<int:id>/', atualiza_categoria_veiculos, name='atualiza_categoria_veiculos'),
    path('excluicategoria/<int:id>/', exclui_categoria_veiculos, name='exclui_categoria_veiculos'),
]