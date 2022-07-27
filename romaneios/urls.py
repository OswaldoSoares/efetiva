from django.urls import path

from .views import index_romaneio, seleciona_cliente

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
]
