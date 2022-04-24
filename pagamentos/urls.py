from django.urls import path

from .views import (
    apagar_tudo,
    cria_contrachequeitens,
    cria_contrachequeitensvale,
    cria_folha,
    cria_pagamento,
    cria_vale,
    dados,
    edita_cartaoponto,
    exclui_contrachequeitens,
    exclui_contrachequeitensvale,
    exclui_recibo,
    exclui_vale,
    imprime_contracheque,
    imprime_recibo,
    index_pagamento,
    inserefalta,
    manutencao,
    seleciona_contracheque,
    seleciona_folha,
    seleciona_mes_ano,
    seleciona_periodo,
    seleciona_saldoavulso,
)

urlpatterns = [
    path("", index_pagamento, name="index_pagamento"),
    path("criafolha", cria_folha, name="criafolha"),
    path("selecionafolha", seleciona_folha, name="selecionafolha"),
    path("selecionacontracheque", seleciona_contracheque, name="selecionacontracheque"),
    path("criacontrachequeitens", cria_contrachequeitens, name="criacontrachequeitens"),
    path(
        "excluicontrachequeitens",
        exclui_contrachequeitens,
        name="excluicontrachequeitens",
    ),
    path("inserefalta", inserefalta, name="inserefalta"),
    path(
        "editacartaoponto/<int:idcartaoponto>/",
        edita_cartaoponto,
        name="editacartaoponto",
    ),
    path("selecionaperiodo", seleciona_periodo, name="selecionaperiodo"),
    path("selecionasaldoavulso", seleciona_saldoavulso, name="selecionasaldoavulso"),
    path("criapagamento", cria_pagamento, name="criapagamento"),
    path("criavale", cria_vale, name="criavale"),
    path("excluivale", exclui_vale, name="excluivale"),
    path("excluirecibo", exclui_recibo, name="excluirecibo"),
    path("imprimerecibo", imprime_recibo, name="imprimerecibo"),
    path(
        "criacontrachequeitensvale",
        cria_contrachequeitensvale,
        name="criacontrachequeitensvale",
    ),
    path(
        "excluicontrachequeitensvale",
        exclui_contrachequeitensvale,
        name="excluicontrachequeitensvale",
    ),
    path("imprimecontracheque/", imprime_contracheque, name="imprimecontracheque"),
    path("manutencao", manutencao),
    path("apaga", apagar_tudo, name="apaga"),
    path("seleciona_mes_ano", seleciona_mes_ano, name="seleciona_mes_ano"),
    path("dados", dados, name="dados"),
]
