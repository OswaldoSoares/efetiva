from django.urls import path

from .views import adiciona_multa, cria_abastecimento, index_despesas, minutas_multa

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
]
