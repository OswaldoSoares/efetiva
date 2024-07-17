from django.urls import path
from . import views

from .views import (
    adiciona_minuta,
    adiciona_romaneio_minuta,
    atualiza_form_pg,
    buscaminutaentrega,
    conclui_minuta,
    concluir_minuta,
    consultaminuta,
    criaminuta,
    criaminutaajudante,
    criaminutadespesa,
    criaminutaentrega,
    criaminutamotorista,
    criaminutaparametrodespesa,
    edita_comentario,
    edita_minuta,
    edita_minuta_coleta_entrega_obs,
    edita_minuta_hora_final,
    edita_minuta_km_final,
    edita_minuta_km_inicial,
    edita_minuta_saida_extra_ajudante,
    edita_minuta_veiculo_escolhido,
    edita_minuta_veiculo_solicitado,
    editaminuta,
    editaminutaentrega,
    editaminutahorafinal,
    editaminutakmfinal,
    editaminutakminicial,
    editaminutaveiculo,
    estorna_minuta,
    estorna_pagamentos_ajudantes,
    exclui_minuta,
    excluiminutaajudante,
    excluiminutadespesa,
    excluiminutaentrega,
    excluiminutamotorista,
    fecha_minuta,
    filtra_minuta,
    filtra_minuta_veiculo_escolhido,
    filtraminutaveiculo,
    imprimeminuta,
    index_minuta,
    insere_ajudante,
    insere_minuta_despesa,
    insere_minuta_entrega,
    insere_motorista,
    minuta,
    remove_minuta_colaborador,
    remove_minuta_despesa,
    remove_minuta_entrega,
    remove_romaneio_minuta,
    gera_receitas,
    gera_pagamentos,
    estorna_pagamentos_motorista,
    estorna_minuta_concluida,
    minutas_periodo,
)

urlpatterns = [
    path("", index_minuta, name="index_minuta"),
    path("criaminuta", criaminuta, name="criaminuta"),
    # path('editaminuta/<int:idmin>/', editaminuta, name='editaminuta'),
    path("imprimeminuta/<int:idmin>/", imprimeminuta, name="imprimeminuta"),
    path("concluiminuta/<int:idmin>/", conclui_minuta, name="concluiminuta"),
    path("fecha_minuta/<int:idmin>/", fecha_minuta, name="fecha_minuta"),
    path("estorna_minuta/<int:idmin>/", estorna_minuta, name="estorna_minuta"),
    path("consultaminuta/<int:idmin>/", consultaminuta, name="consultaminuta"),
    path(
        "criaminutamotorista/", criaminutamotorista, name="criaminutamotorista"
    ),
    path(
        "excluiminutamotorista/<int:idmincol>/",
        excluiminutamotorista,
        name="excluiminutamotorista",
    ),
    path("criaminutaajudante/", criaminutaajudante, name="criaminutaajudante"),
    path(
        "excluiminutaajudante/<int:idmincol>/",
        excluiminutaajudante,
        name="excluiminutaajudante",
    ),
    path(
        "editaminutaveiculo/<int:idmin>/",
        editaminutaveiculo,
        name="editaminutaveiculo",
    ),
    path(
        "editaminutakminicial/<int:idmin>/",
        editaminutakminicial,
        name="editaminutakminicial",
    ),
    path(
        "editaminutakmfinal/<int:idmin>/",
        editaminutakmfinal,
        name="editaminutakmfinal",
    ),
    path(
        "editaminutahorafinal/<int:idmin>/",
        editaminutahorafinal,
        name="editaminutahorafinal",
    ),
    path("criaminutadespesa", criaminutadespesa, name="criaminutadespesa"),
    path(
        "excluiminutadespesa/<int:idmindes>/",
        excluiminutadespesa,
        name="excluiminutadespesa",
    ),
    path(
        "criaminutaparametrodespesa",
        criaminutaparametrodespesa,
        name="criaminutaparametrodespesa",
    ),
    path("criaminutaentrega", criaminutaentrega, name="criaminutaentrega"),
    path(
        "editaminutaentrega/<int:idminent>/",
        editaminutaentrega,
        name="editaminutaentrega",
    ),
    path(
        "excluiminutaentrega/<int:idminent>/",
        excluiminutaentrega,
        name="excluiminutaentrega",
    ),
    path("buscaminutaentrega/", buscaminutaentrega, name="buscaminutaentrega"),
    path(
        "editacomentario/<int:idmin>/",
        edita_comentario,
        name="editacomentario",
    ),
    path(
        "filtraminutaveiculo/", filtraminutaveiculo, name="filtraminutaveiculo"
    ),
    path("excluiminuta/<int:idminuta>/", exclui_minuta, name="excluiminuta"),
    path(
        "editaminutasaidaextraajudante/<int:idminuta>",
        edita_minuta_saida_extra_ajudante,
        name="editaminutasaidaextraajudante",
    ),
    path("minuta/<int:idminuta>/", minuta, name="minuta"),
    path("adicionaminuta/", adiciona_minuta, name="adicionaminuta"),
    path("filtraminuta", filtra_minuta, name="filtraminuta"),
    path("editaminuta/", edita_minuta, name="editaminuta"),
    path("editahorafinal/", edita_minuta_hora_final, name="editahorafinal"),
    path(
        "editaveiculosolicitado/",
        edita_minuta_veiculo_solicitado,
        name="editaveiculosolicitado",
    ),
    path("inseremotorista/", insere_motorista, name="inseremotorista"),
    path(
        "editaveiculoescolhido/",
        edita_minuta_veiculo_escolhido,
        name="editaveiculoescolhido",
    ),
    path(
        "filtraveiculoescolhido/",
        filtra_minuta_veiculo_escolhido,
        name="filtraveiculoescolhido",
    ),
    path("editakminicial/", edita_minuta_km_inicial, name="editakminicial"),
    path("editakmfinal/", edita_minuta_km_final, name="editakmfinal"),
    path("insereajudante/", insere_ajudante, name="insereajudante"),
    path(
        "removecolaborador/",
        remove_minuta_colaborador,
        name="removecolaborador",
    ),
    path(
        "editacoletaentregaobs/",
        edita_minuta_coleta_entrega_obs,
        name="editacoletaentregaobs",
    ),
    path("inseredespesa/", insere_minuta_despesa, name="inseredespesa"),
    path("removedespesa/", remove_minuta_despesa, name="removedespesa"),
    path("insereentrega/", insere_minuta_entrega, name="insereentrega"),
    path(
        "remove_entrega/",
        remove_minuta_entrega,
        name="remove_entrega",
    ),
    path("atualizaformpg/", atualiza_form_pg, name="atualizaformpg"),
    path(
        "estorna_pagamentos_ajudantes",
        estorna_pagamentos_ajudantes,
        name="estorna_pagamentos_ajudantes",
    ),
    path("concluirminuta/", concluir_minuta, name="concluirminuta"),
    path(
        "adiciona_romaneio_minuta",
        adiciona_romaneio_minuta,
        name="adiciona_romaneio_minuta",
    ),
    path(
        "remove_romaneio_minuta",
        remove_romaneio_minuta,
        name="remove_romaneio_minuta",
    ),
    path(
        "gera_receitas",
        gera_receitas,
        name="gera_receitas",
    ),
    path(
        "gera_pagamentos",
        gera_pagamentos,
        name="gera_pagamentos",
    ),
    path(
        "estorna_pagamentos_motorista",
        estorna_pagamentos_motorista,
        name="estorna_pagamentos_motorista",
    ),
    path(
        "estorna_minuta_concluida",
        estorna_minuta_concluida,
        name="estorna_minuta_concluida",
    ),
    path(
        "minutas_periodo",
        minutas_periodo,
        name="minutas_periodo",
    ),
    path(
        "minuta_cards",
        views.minuta_cards,
        name="minuta_cards",
    ),
    path(
        "estorna_faturamento",
        views.estorna_faturamento,
        name="estorna_faturamento",
    ),
]
