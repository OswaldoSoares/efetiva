from django.urls import path
from .views import indexpessoal, \
    criapessoa, consultapessoa, criadocpessoa, criafonepessoa, editapessoa,\
    excluipessoa, excluidocpessoa, excluifonepessoa, criacontapessoa, excluicontapessoa

urlpatterns = [
    path(
        '',
        indexpessoal,
        name='indexpessoal'
    ),
    path(
        'consultapessoa/<int:idpes>/',
        consultapessoa,
        name='consultapessoa'
    ),
    path(
        'criapessoa/',
        criapessoa,
        name='criapessoa'
    ),
    path(
        'editapessoa/<int:idpes>/',
        editapessoa,
        name='editapessoa'
    ),
    path(
        'excluipessoa/<int:idpes>/',
        excluipessoa,
        name='excluipessoa'
    ),
    path(
        'criadocpessoa/',
        criadocpessoa,
        name='criadocpessoa'
    ),
    path(
        'excluidocpessoa/<int:idpesdoc>/',
        excluidocpessoa,
        name='excluidocpessoa'
    ),
    path(
        'criafonepessoa/',
        criafonepessoa,
        name='criafonepessoa'
    ),
    path(
        'excluifomepessoa/<int:idpesfon>',
        excluifonepessoa,
        name='excluifonepessoa'
    ),
    path(
        'criacontapessoa/',
        criacontapessoa,
        name='criacontapessoa'
    ),
    path(
        'excluicontapessoa/<int:idpescon>/',
        excluicontapessoa,
        name='excluicontapessoa'
    )
]
