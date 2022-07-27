from django.urls import path

from .views import adiciona_nota_cliente, index_romaneio, seleciona_cliente

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
]
