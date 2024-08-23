from django.urls import path
from . import views

from .views import (
    edita_comentario,
    edita_minuta_saida_extra_ajudante,
    estorna_minuta,
    estorna_pagamentos_ajudantes,
    filtra_minuta,
    filtra_minuta_veiculo_escolhido,
    imprimeminuta,
    index_minuta,
    minuta,
    gera_receitas,
    gera_pagamentos,
    estorna_pagamentos_motorista,
    estorna_minuta_concluida,
    minutas_periodo,
)
from .views import (
    adicionar_minuta,
    editar_minuta,
    editar_minuta_hora_final,
    adicionar_veiculo_solicitado,
    adicionar_motorista_minuta,
    adicionar_veiculo_minuta,
    editar_minuta_km_final,
    editar_minuta_km_inicial,
    adicionar_ajudante_minuta,
    excluir_colaborador_minuta,
    editar_informacoes_minuta,
    adicionar_despesa,
    excluir_despesa,
    adicionar_entrega,
    remover_entrega,
    gerenciar_romaneio_minuta,
    alterar_status_minuta,
)

urlpatterns = [
    path("", index_minuta, name="index_minuta"),
    path("imprimeminuta/<int:idmin>/", imprimeminuta, name="imprimeminuta"),
    path("estorna_minuta/<int:idmin>/", estorna_minuta, name="estorna_minuta"),
    path(
        "editacomentario/<int:idmin>/",
        edita_comentario,
        name="editacomentario",
    ),
    path(
        "editaminutasaidaextraajudante/<int:idminuta>",
        edita_minuta_saida_extra_ajudante,
        name="editaminutasaidaextraajudante",
    ),
    path("minuta/<int:idminuta>/", minuta, name="minuta"),
    path("filtraminuta", filtra_minuta, name="filtraminuta"),
    path(
        "filtraveiculoescolhido/",
        filtra_minuta_veiculo_escolhido,
        name="filtraveiculoescolhido",
    ),
    path(
        "estorna_pagamentos_ajudantes",
        estorna_pagamentos_ajudantes,
        name="estorna_pagamentos_ajudantes",
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
        "estorna_faturamento",
        views.estorna_faturamento,
        name="estorna_faturamento",
    ),
    # paths validos a partir de 01/08/2024
    path(
        "adicionar_minuta",
        adicionar_minuta,
        name="adicionar_minuta",
    ),
    path(
        "editar_minuta",
        editar_minuta,
        name="editar_minuta",
    ),
    path(
        "editar_minuta_hora_final",
        editar_minuta_hora_final,
        name="editar_minuta_hora_final",
    ),
    path(
        "adicionar_veiculo_solicitado",
        adicionar_veiculo_solicitado,
        name="adicionar_veiculo_solicitado",
    ),
    path(
        "adicionar_motorista_minuta",
        adicionar_motorista_minuta,
        name="adicionar_motorista_minuta",
    ),
    path(
        "adicionar_veiculo_minuta",
        adicionar_veiculo_minuta,
        name="adicionar_veiculo_minuta",
    ),
    path(
        "editar_minuta_km_inicial",
        editar_minuta_km_inicial,
        name="editar_minuta_km_inicial",
    ),
    path(
        "editar_minuta_km_final/",
        editar_minuta_km_final,
        name="editar_minuta_km_final",
    ),
    path(
        "adicionar_ajudante_minuta",
        adicionar_ajudante_minuta,
        name="adicionar_ajudante_minuta",
    ),
    path(
        "excluir_colaborador_minuta",
        excluir_colaborador_minuta,
        name="excluir_colaborador_minuta",
    ),
    path(
        "editar_informacoes_minuta",
        editar_informacoes_minuta,
        name="editar_informacoes_minuta",
    ),
    path(
        "adicionar_despesa",
        adicionar_despesa,
        name="adicionar_despesa",
    ),
    path(
        "excluir_despesa",
        excluir_despesa,
        name="excluir_despesa",
    ),
    path(
        "adicionar_entrega",
        adicionar_entrega,
        name="adicionar_entrega",
    ),
    path(
        "remover_entrega",
        remover_entrega,
        name="remover_entrega",
    ),
    path(
        "gerenciar_romaneio_minuta",
        gerenciar_romaneio_minuta,
        name="gerenciar_romaneio_minuta",
    ),
    path(
        "alterar_status_minuta",
        alterar_status_minuta,
        name="alterar_status_minuta",
    ),
]
