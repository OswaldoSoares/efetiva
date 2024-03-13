from django.urls import path

from .views import (
    adiciona_agenda,
    adiciona_contra_cheque_itens,
    adiciona_vales,
    altera_horario_cartao_ponto,
    atestada,
    ausencia_falta,
    carrega_agenda,
    carro_empresa,
    delete_file,
    exclui_agenda,
    exclui_recibo,
    gera_pagamento_avulso,
    imprime_recibo,
    paga_recibo,
    index_pagamento,
    print_contra_cheque_adiantamento,
    print_contra_cheque_pagamento,
    print_contra_cheque_transporte,
    remove_contra_cheque_itens,
    remove_vales,
    salva_file,
    seleciona_colaborador_avulso,
    seleciona_funcionario,
    seleciona_mes_ano,
    seleciona_periodo_avulso,
    seleciona_vales,
    imprime_relatorio_saldo_avulso,
    form_paga_recibo,
    seleciona_contra_cheque,
    adiciona_agenda_colaborador,
    edita_agenda_colaborador,
    exclui_agenda_colaborador,
)

urlpatterns = [
    path("", index_pagamento, name="index_pagamento"),
    path(
        "seleciona_periodo_avulso",
        seleciona_periodo_avulso,
        name="seleciona_periodo_avulso",
    ),
    path(
        "seleciona_colaborador_avulso",
        seleciona_colaborador_avulso,
        name="seleciona_colaborador_avulso",
    ),
    path(
        "gera_pagamento_avulso",
        gera_pagamento_avulso,
        name="gera_pagamento_avulso",
    ),
    path("excluirecibo", exclui_recibo, name="excluirecibo"),
    path("imprimerecibo", imprime_recibo, name="imprimerecibo"),
    path(
        "seleciona_mes_ano",
        seleciona_mes_ano,
        name="seleciona_mes_ano",
    ),
    path(
        "seleciona_funcionario",
        seleciona_funcionario,
        name="seleciona_funcionario",
    ),
    path(
        "ausencia_falta",
        ausencia_falta,
        name="ausencia_falta",
    ),
    path(
        "altera_horario_cartao_ponto",
        altera_horario_cartao_ponto,
        name="altera_horario_cartao_ponto",
    ),
    path(
        "atestada",
        atestada,
        name="atestada",
    ),
    path(
        "adiciona_contra_cheque_itens",
        adiciona_contra_cheque_itens,
        name="adiciona_contra_cheque_itens",
    ),
    path(
        "remove_contra_cheque_itens",
        remove_contra_cheque_itens,
        name="remove_contra_cheque_itens",
    ),
    path(
        "adiciona_vales",
        adiciona_vales,
        name="adiciona_vales",
    ),
    path(
        "seleciona_vales",
        seleciona_vales,
        name="seleciona_vales",
    ),
    path(
        "remove_vales",
        remove_vales,
        name="remove_vales",
    ),
    path(
        "print_contra_cheque_pagamento",
        print_contra_cheque_pagamento,
        name="print_contra_cheque_pagamento",
    ),
    path(
        "print_contra_cheque_adiantamento",
        print_contra_cheque_adiantamento,
        name="print_contra_cheque_adiantamento",
    ),
    path(
        "print_contra_cheque_transporte",
        print_contra_cheque_transporte,
        name="print_contra_cheque_transporte",
    ),
    path(
        "salva_file",
        salva_file,
        name="salva_file",
    ),
    path(
        "delete_file",
        delete_file,
        name="delete_file",
    ),
    path(
        "carro_empresa",
        carro_empresa,
        name="carro_empresa",
    ),
    path(
        "adiciona_agenda",
        adiciona_agenda,
        name="adiciona_agenda",
    ),
    path(
        "carrega_agenda",
        carrega_agenda,
        name="carrega_agenda",
    ),
    path(
        "exclui_agenda",
        exclui_agenda,
        name="exclui_agenda",
    ),
    path(
        "imprime_relatorio_saldo_avulso",
        imprime_relatorio_saldo_avulso,
        name="imprime_relatorio_saldo_avulso",
    ),
    path(
        "paga_recibo",
        paga_recibo,
        name="paga_recibo",
    ),
    path(
        "form_paga_recibo",
        form_paga_recibo,
        name="form_paga_recibo",
    ),
    path(
        "seleciona_contra_cheque",
        seleciona_contra_cheque,
        name="seleciona_contra_cheque",
    ),
    path(
        "adiciona_agenda_colaborador",
        adiciona_agenda_colaborador,
        name="adiciona_agenda_colaborador",
    ),
    path(
        "edita_agenda_colaborador",
        edita_agenda_colaborador,
        name="edita_agenda_colaborador",
    ),
    path(
        "exclui_agenda_colaborador",
        exclui_agenda_colaborador,
        name="exclui_agenda_colaborador",
    ),
]
