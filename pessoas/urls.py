from django.urls import path
from .views import (
    indexpessoal,
    cria_pessoa,
    consulta_pessoa,
    criadocpessoa,
    criafonepessoa,
    edita_pessoa,
    excluipessoa,
    bloqueia_pessoa,
    excluidocpessoa,
    excluifonepessoa,
    criacontapessoa,
    excluicontapessoa,
    edita_salario,
    cria_vale,
    cria_contracheque,
    seleciona_contracheque,
    cria_contrachequeitens,
    edita_demissao,
    consulta_pessoa,
    salva_foto,
)


urlpatterns = [
    path("", indexpessoal, name="indexpessoal"),
    path("consultapessoa/<int:idpessoa>/", consulta_pessoa, name="consultapessoa"),
    path("criapessoa/", cria_pessoa, name="criapessoa"),
    path("editapessoa/<int:idpessoa>/", edita_pessoa, name="editapessoa"),
    path("excluipessoa/<int:idpessoa>/", excluipessoa, name="excluipessoa"),
    path("bloqueiapessoa/<int:idpessoa>/", bloqueia_pessoa, name="bloqueiapessoa"),
    path("criadocpessoa/", criadocpessoa, name="criadocpessoa"),
    path("excluidocpessoa/<int:idpesdoc>/", excluidocpessoa, name="excluidocpessoa"),
    path("criafonepessoa/", criafonepessoa, name="criafonepessoa"),
    path("excluifomepessoa/<int:idpesfon>/", excluifonepessoa, name="excluifonepessoa"),
    path("criacontapessoa/", criacontapessoa, name="criacontapessoa"),
    path(
        "excluicontapessoa/<int:idpescon>/", excluicontapessoa, name="excluicontapessoa"
    ),
    path("editasalario/", edita_salario, name="editasalario"),
    path("editademissao", edita_demissao, name="editademissao"),
    path("criavale/", cria_vale, name="criavale"),
    path("criacontracheque/", cria_contracheque, name="criacontracheque"),
    path(
        "selecionacontrachequemudei/",
        seleciona_contracheque,
        name="selecionacontrachequemudei",
    ),
    path(
        "criacontrachequeitensmudei/",
        cria_contrachequeitens,
        name="criacontrachequeitensmudei",
    ),
    path(
        "consulta_pessoa",
        consulta_pessoa,
        name="consulta_pessoa",
    ),
    path(
        "salva_foto",
        salva_foto,
        name="salva_foto",
    ),
]
