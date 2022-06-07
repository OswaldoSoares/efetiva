from django.urls import path

from .views import (
    adiciona_multa,
    cria_abastecimento,
    edita_multa,
    exclui_multa,
    index_despesas,
    minutas_multa,
)

urlpatterns = [
    path("", index_despesas, name="index_despesas"),
    path("cria_abastecimento", cria_abastecimento, name="cria_abastecimento"),
    path(
        "adiciona_multa",
        adiciona_multa,
        name="adiciona_multa",
    ),
    path(
        "minutas_multa",
        minutas_multa,
        name="minutas_multa",
    ),
    path(
        "edita_multa",
        edita_multa,
        name="edita_multa",
    ),
    path(
        "exclui_multa",
        exclui_multa,
        name="exclui_multa",
    ),
]
