from django.urls import path

from .views import (
    adiciona_nota_cliente,
    adiciona_ocorrencia,
    edita_nota_cliente,
    exclui_nota_cliente,
    index_romaneio,
    ocorrencia_nota_cliente,
    seleciona_cliente,
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
]
