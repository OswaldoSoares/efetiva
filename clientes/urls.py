from django.urls import path
from .views import index_cliente, consulta_cliente, cria_cliente, edita_cliente, exclui_cliente, cria_email_cliente, \
    edita_email_cliente, exclui_email_cliente, cria_fone_cliente, edita_fone_cliente, exclui_fone_cliente, \
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
    path('', index_cliente, name='indexcliente'),
    path('consultacliente/<int:idcliente>/', consulta_cliente, name='consultacliente'),
    path('criacliente/', cria_cliente, name='criacliente'),
    path('editacliente/<int:idcliente>/', edita_cliente, name='editacliente'),
    path('excluicliente/<int:idcliente>/', exclui_cliente, name='excluicliente'),
    path('criaemailcliente/', cria_email_cliente, name='criaemailcliente'),
    path('editaemailcliente/<int:idclienteemail>/', edita_email_cliente, name='editaemailcliente'),
    path('excluiemailcliente/<int:idclienteemail>/', exclui_email_cliente, name='excluiemailcliente'),
    path('criafonecliente/', cria_fone_cliente, name='criafonecliente'),
    path('editafonecliente/<int:idclientefone>/', edita_fone_cliente, name='editafonecliente'),
    path('excluifonecliente/<int:idclientefone>/', exclui_fone_cliente, name='excluifonecliente'),
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
