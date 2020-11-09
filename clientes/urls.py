from django.urls import path
from .views import indexcliente,\
    consultacliente, \
    criacliente, \
    editacliente, \
    excluicliente, \
    criaemailcliente, \
    editaemailcliente, \
    excluiemailcliente,\
    criafonecliente, \
    editafonecliente, \
    excluifonecliente, \
    criacobrancacliente, \
    editacobrancacliente, \
    excluicobrancacliente, \
    criatabelacliente, \
    editatabelacliente, \
    editaphkesc, \
    criatabelaveiculo, \
    editatabelaveiculo, \
    selecionatabelaveiculo, \
    criatabelacapacidade,\
    editatabelacapacidade,\
    excluitabelacapacidade,\
    criatabelaperimetro,\
    editatabelaperimetro,\
    excluitabelaperimetro, \
    criaformapgto

urlpatterns = [
    path(
        '',
        indexcliente,
        name='indexcliente'
    ),
    path(
        'consultacliente/<int:idcli>/',
        consultacliente,
        name='consultacliente'
    ),
    path(
        'criacliente/',
        criacliente,
        name='criacliente'
    ),
    path(
        'editacliente/<int:idcli>/',
        editacliente,
        name='editacliente'
    ),
    path(
        'excluicliente/<int:idcli>/',
        excluicliente,
        name='excluicliente'
    ),
    path(
        'criaemailcliente/',
        criaemailcliente,
        name='criaemailcliente'
    ),
    path(
        'editaemailcliente/<int:idemacon>/',
        editaemailcliente,
        name='editaemailcliente'
    ),
    path(
        'excluiemailcliente/<int:idemacon>/',
        excluiemailcliente,
        name='excluiemailcliente'
    ),
    path(
        'criafonecliente/',
        criafonecliente,
        name='criafonecliente'
    ),
    path(
        'editafonecliente/<int:idfoncon>/',
        editafonecliente,
        name='editafonecliente'
    ),
    path(
        'excluifonecliente/<int:idfoncon>/',
        excluifonecliente,
        name='excluifonecliente'
    ),
    path(
        'criacobrancacliente/',
        criacobrancacliente,
        name='criacobrancacliente'
    ),
    path(
        'editacobrancacliente/<int:idcobcli>/',
        editacobrancacliente,
        name='editacobrancacliente'
    ),
    path(
        'excluicobrancacliente/<int:idcobcli>/',
        excluicobrancacliente,
        name='excluicobrancacliente'
    ),
    path(
        'criatabelacliente/',
        criatabelacliente,
        name='criatabelacliente'
    ),
    path(
        'editatabelacliente/<int:idtabcli>/',
        editatabelacliente,
        name='editatabelacliente'
    ),
    path(
        'editaphkesc/<int:idtabcli>/',
        editaphkesc,
        name='editaphkesc'
    ),
    path(
        'criatabelaveiculo/',
        criatabelaveiculo,
        name='criatabelaveiculo'
    ),
    path(
        'editatabelaveiculo/<int:idtabvei>/',
        editatabelaveiculo,
        name='editatabelaveiculo'
    ),
    path(
        'selecionatabelaveiculo/',
        selecionatabelaveiculo,
        name='selecionatabelaveiculo'
    ),
    path(
        'criatabelacapacidade/',
        criatabelacapacidade,
        name='criatabelacapacidade'
    ),
    path(
        'editatabelacapacidade/<int:idtabcap>/',
        editatabelacapacidade,
        name='editatabelacapacidade'
    ),
    path(
        'excluitabelacapacidade/<int:idtabcap>/',
        excluitabelacapacidade,
        name='excluitabelacapacidade'
    ),
    path(
        'criatabelaperimetro/',
        criatabelaperimetro,
        name='criatabelaperimetro'
    ),
    path(
        'editatabelaperimetro/<int:idtabper>/',
        editatabelaperimetro,
        name='editatabelaperimetro'
    ),
    path(
        'excluitabelaperimetro/<int:idtabper>/',
        excluitabelaperimetro,
        name='excluitabelaperimetro'
    ),
    path(
        'criaformapgto/',
        criaformapgto,
        name='criaformapgto'
    )
]
