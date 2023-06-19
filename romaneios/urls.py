from django.urls import path

from .views import (
    adiciona_nota_cliente,
    adiciona_nota_romaneio,
    adiciona_ocorrencia,
    adiciona_romaneio,
    carrega_xml,
    edita_nota_cliente,
    edita_romaneio,
    envia_telegram_relatorio,
    envia_telegram_romaneio,
    exclui_nota_cliente,
    exclui_nota_romaneio,
    fecha_romaneio,
    filtra_nota_cliente,
    filtra_status,
    imprime_notas_status,
    imprime_romaneio,
    index_romaneio,
    ler_nota_xml,
    nota_deposito,
    ocorrencia_nota_cliente,
    orderna_notas,
    seleciona_cliente,
    seleciona_romaneio,
    reabre_romaneio,
    busca_local_nota,
    exclui_ocorrencia,
    seleciona_filtro_emitente,
)

urlpatterns = [
    path(
        "",
        index_romaneio,
        name="index_romaneio",
    ),
    path(
        "seleciona_cliente",
        seleciona_cliente,
        name="seleciona_cliente",
    ),
    path(
        "adiciona_nota_cliente",
        adiciona_nota_cliente,
        name="adiciona_nota_cliente",
    ),
    path(
        "edita_nota_cliente",
        edita_nota_cliente,
        name="edita_nota_cliente",
    ),
    path(
        "exclui_nota_cliente",
        exclui_nota_cliente,
        name="exclui_nota_cliente",
    ),
    path(
        "ocorrencia_nota_cliente",
        ocorrencia_nota_cliente,
        name="ocorrencia_nota_cliente",
    ),
    path(
        "adiciona_ocorrencia",
        adiciona_ocorrencia,
        name="adiciona_ocorrencia",
    ),
    path(
        "adiciona_romaneio",
        adiciona_romaneio,
        name="adiciona_romaneio",
    ),
    path(
        "edita_romaneio",
        edita_romaneio,
        name="edita_romaneio",
    ),
    path(
        "seleciona_romaneio",
        seleciona_romaneio,
        name="seleciona_romaneio",
    ),
    path(
        "adiciona_nota_romaneio",
        adiciona_nota_romaneio,
        name="adiciona_nota_romaneio",
    ),
    path(
        "ler_nota_xml",
        ler_nota_xml,
        name="ler_nota_xml",
    ),
    path(
        "carrega_xml",
        carrega_xml,
        name="carrega_xml",
    ),
    path(
        "orderna_notas",
        orderna_notas,
        name="orderna_notas",
    ),
    path(
        "exclui_nota_romaneio",
        exclui_nota_romaneio,
        name="exclui_nota_romaneio",
    ),
    path(
        "imprime_romaneio",
        imprime_romaneio,
        name="imprime_romaneio",
    ),
    path(
        "filtra_nota_cliente",
        filtra_nota_cliente,
        name="filtra_nota_cliente",
    ),
    path(
        "fecha_romaneio",
        fecha_romaneio,
        name="fecha_romaneio",
    ),
    path(
        "envia_telegram_romaneio",
        envia_telegram_romaneio,
        name="envia_telegram_romaneio",
    ),
    path(
        "filtra_status",
        filtra_status,
        name="filtra_status",
    ),
    path(
        "imprime_notas_status",
        imprime_notas_status,
        name="imprime_notas_status",
    ),
    path(
        "nota_deposito",
        nota_deposito,
        name="nota_deposito",
    ),
    path(
        "envia_telegram_relatorio",
        envia_telegram_relatorio,
        name="envia_telegram_relatorio",
    ),
    path(
        "reabre_romaneio",
        reabre_romaneio,
        name="reabre_romaneio",
    ),
    path(
        "busca_local_nota",
        busca_local_nota,
        name="busca_local_nota",        
    ),
    path(
        "exclui_ocorrencia",
        exclui_ocorrencia,
        name="exclui_ocorrencia",
    ),
    path(
        "seleciona_filtro_emitente",
        seleciona_filtro_emitente,
        name="seleciona_filtro_emitente",
    ),
]
