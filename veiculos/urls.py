from django.urls import path

from .views import (
    consultaveiculo,
    indexveiculo,
    veiculo_consulta,
    veiculo_excluir,
    veiculo_form,
    veiculo_situacao,
    veiculos_lista,
)

urlpatterns = [
    path("", indexveiculo, name="indexveiculo"),
    path("lista", veiculos_lista, name="veiculos_lista"),
    path("consulta", veiculo_consulta, name="veiculo_consulta"),
    path("veiculo", veiculo_form, name="veiculo_form"),
    path("situacao", veiculo_situacao, name="veiculo_situacao"),
    path("excluir", veiculo_excluir, name="veiculo_excluir"),
    # Endereço antigo, mantido para links salvos
    path(
        "consultaveiculo/<int:idvei>/",
        consultaveiculo,
        name="consultaveiculo",
    ),
]
