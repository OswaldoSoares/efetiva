from django.urls import path

from .views import adiciona_multa, cria_abastecimento, index_despesas

urlpatterns = [
    path("", index_despesas, name="index_despesas"),
    path("cria_abastecimento", cria_abastecimento, name="cria_abastecimento"),
    path(
        "adiciona_multa",
        adiciona_multa,
        name="adiciona_multa",
    ),
]
