from django.urls import path
from .views import (
    indexpessoal,
    criafonepessoa,
    bloqueia_pessoa,
    excluifonepessoa,
    criacontapessoa,
    excluicontapessoa,
    edita_salario,
    cria_vale,
    cria_contracheque,
    seleciona_contracheque,
    cria_contrachequeitens,
    edita_demissao,
    salva_foto,
    atualiza_decimo_terceiro,
    print_decimo_terceiro,
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
    altera_salario_colaborador,
    salva_salario_colaborador,
    demissao_colaborador,
    salva_demissao_colaborador,
    periodo_ferias,
    salva_periodo_ferias,
    confirma_exclusao_periodo_ferias,
    exclui_periodo_ferias,
    print_ferias,
    altera_status_colaborador,
    altera_lista,
    verba_rescisoria,
    print_rescisao_trabalho,
    seleciona_aquisitivo,
    seleciona_parcela,
    adiciona_vale_contra_cheque,
    exclui_contra_cheque_item,
    imprime_contra_cheque,
    adiciona_vale_colaborador,
    exclui_vale_colaborador,
    pagamento_contra_cheque,
    estorna_contra_cheque,
    arquiva_contra_cheque,
    exclui_arquivo_contra_cheque,
)

from .views import (
    selecionar_categoria,
    consultar_colaborador,
    adicionar_ou_atualizar_colaborador,
    adicionar_ou_atualizar_doc_colaborador,
)


urlpatterns = [
    path("", indexpessoal, name="indexpessoal"),
    path(
        "selecionar_categoria",
        selecionar_categoria,
        name="selecionar_categoria",
    ),
    path(
        "consultar_colaborador",
        consultar_colaborador,
        name="consultar_colaborador",
    ),
    path(
        "adicionar_ou_atualizar_colaborador",
        adicionar_ou_atualizar_colaborador,
        name="adicionar_ou_atualizar_colaborador",
    ),
    path(
        "adicionar_ou_atualizar_doc_colaborador",
        adicionar_ou_atualizar_doc_colaborador,
        name="adicionar_ou_atualizar_doc_colaborador",
    ),
    # Antigos
    path(
        "bloqueiapessoa/<int:idpessoa>/",
        bloqueia_pessoa,
        name="bloqueiapessoa",
    ),
    path("criafonepessoa/", criafonepessoa, name="criafonepessoa"),
    path(
        "excluifomepessoa/<int:idpesfon>/",
        excluifonepessoa,
        name="excluifonepessoa",
    ),
    path("criacontapessoa/", criacontapessoa, name="criacontapessoa"),
    path(
        "excluicontapessoa/<int:idpescon>/",
        excluicontapessoa,
        name="excluicontapessoa",
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
    path(
        "altera_salario_colaborador",
        altera_salario_colaborador,
        name="altera_salario_colaborador",
    ),
    path(
        "salva_salario_colaborador",
        salva_salario_colaborador,
        name="salva_salario_colaborador",
    ),
    path(
        "demissao_colaborador",
        demissao_colaborador,
        name="demissao_colaborador",
    ),
    path(
        "salva_demissao_colaborador",
        salva_demissao_colaborador,
        name="salva_demissao_colaborador",
    ),
    path(
        "periodo_ferias",
        periodo_ferias,
        name="periodo_ferias",
    ),
    path(
        "salva_periodo_ferias",
        salva_periodo_ferias,
        name="salva_periodo_ferias",
    ),
    path(
        "print_ferias",
        print_ferias,
        name="print_ferias",
    ),
    path(
        "altera_status_colaborador",
        altera_status_colaborador,
        name="altera_status_colaborador",
    ),
    path(
        "altera_lista",
        altera_lista,
        name="altera_lista",
    ),
    path(
        "confirma_exclusao_periodo_ferias",
        confirma_exclusao_periodo_ferias,
        name="confirma_exclusao_periodo_ferias",
    ),
    path(
        "exclui_periodo_ferias",
        exclui_periodo_ferias,
        name="exclui_periodo_ferias",
    ),
    path(
        "verba_rescisoria",
        verba_rescisoria,
        name="verba_rescisoria",
    ),
    path(
        "print_rescisao_trabalho",
        print_rescisao_trabalho,
        name="print_rescisao_trabalho",
    ),
    path(
        "seleciona_aquisitivo",
        seleciona_aquisitivo,
        name="seleciona_aquisitivo",
    ),
    path(
        "seleciona_parcela",
        seleciona_parcela,
        name="seleciona_parcela",
    ),
    path(
        "adiciona_vale_contra_cheque",
        adiciona_vale_contra_cheque,
        name="adiciona_vale_contra_cheque",
    ),
    path(
        "exclui_contra_cheque_item",
        exclui_contra_cheque_item,
        name="exclui_contra_cheque_item",
    ),
    path(
        "imprime_contra_cheque",
        imprime_contra_cheque,
        name="imprime_contra_cheque",
    ),
    path(
        "adiciona_vale_colaborador",
        adiciona_vale_colaborador,
        name="adiciona_vale_colaborador",
    ),
    path(
        "exclui_vale_colaborador",
        exclui_vale_colaborador,
        name="exclui_vale_colaborador",
    ),
    path(
        "pagamento_contra_cheque",
        pagamento_contra_cheque,
        name="pagamento_contra_cheque",
    ),
    path(
        "estorna_contra_cheque",
        estorna_contra_cheque,
        name="estorna_contra_cheque",
    ),
    path(
        "arquiva_contra_cheque",
        arquiva_contra_cheque,
        name="arquiva_contra_cheque",
    ),
    path(
        "exclui_arquivo_contra_cheque",
        exclui_arquivo_contra_cheque,
        name="exclui_arquivo_contra_cheque",
    ),
]
