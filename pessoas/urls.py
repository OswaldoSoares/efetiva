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
    atualiza_decimo_terceiro,
    print_decimo_terceiro,
    adiciona_documento_colaborador,
    altera_documento_colaborador,
    exclui_documento_colaborador,
    salva_documento_colaborador,
    apaga_documento_colaborador,
    adiciona_telefone_colaborador,
    altera_telefone_colaborador,
    exclui_telefone_colaborador,
    salva_telefone_colaborador,
    apaga_telefone_colaborador,
    adiciona_conta_colaborador,
    altera_conta_colaborador,
    exclui_conta_colaborador,
    salva_conta_colaborador,
    apaga_conta_colaborador,
    form_paga_decimo_terceiro,
    paga_decimo_terceiro,
    print_ficha_colaborador,
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
    path(
        "atualiza_decimo_terceiro",
        atualiza_decimo_terceiro,
        name="atualiza_decimo_terceiro",
    ),
    path(
        "print_decimo_terceiro",
        print_decimo_terceiro,
        name="print_decimo_terceiro",
    ),
    path(
        "adiciona_documento_colaborador",
        adiciona_documento_colaborador,
        name="adiciona_documento_colaborador",
    ),
    path(
        "altera_documento_colaborador",
        altera_documento_colaborador,
        name="altera_documento_colaborador",
    ),
    path(
        "exclui_documento_colaborador",
        exclui_documento_colaborador,
        name="exclui_documento_colaborador",
    ),
    path(
        "salva_documento_colaborador",
        salva_documento_colaborador,
        name="salva_documento_colaborador",
    ),
    path(
        "apaga_documento_colaborador",
        apaga_documento_colaborador,
        name="apaga_documento_colaborador",
    ),
    path(
        "adiciona_telefone_colaborador",
        adiciona_telefone_colaborador,
        name="adiciona_telefone_colaborador",
    ),
    path(
        "altera_telefone_colaborador",
        altera_telefone_colaborador,
        name="altera_telefone_colaborador",
    ),
    path(
        "exclui_telefone_colaborador",
        exclui_telefone_colaborador,
        name="exclui_telefone_colaborador",
    ),
    path(
        "salva_telefone_colaborador",
        salva_telefone_colaborador,
        name="salva_telefone_colaborador",
    ),
    path(
        "apaga_telefone_colaborador",
        apaga_telefone_colaborador,
        name="apaga_telefone_colabor",
    ),
    path(
        "adiciona_conta_colaborador",
        adiciona_conta_colaborador,
        name="adiciona_conta_colaborador",
    ),
    path(
        "altera_conta_colaborador",
        altera_conta_colaborador,
        name="altera_conta_colaborador",
    ),
    path(
        "exclui_conta_colaborador",
        exclui_conta_colaborador,
        name="exclui_conta_colaborador",
    ),
    path(
        "salva_conta_colaborador",
        salva_conta_colaborador,
        name="salva_conta_colaborador",
    ),
    path(
        "apaga_conta_colaborador",
        apaga_conta_colaborador,
        name="apaga_conta_colaborador",
    ),
    path(
        "form_paga_decimo_terceiro",
        form_paga_decimo_terceiro,
        name="form_paga_decimo_terceiro",
    ),
    path(
        "paga_decimo_terceiro",
        paga_decimo_terceiro,
        name="paga_decimo_terceiro",
    ),
    path(
        "print_ficha_colaborador",
        print_ficha_colaborador,
        name="print_ficha_colaborador",
    ),
]
