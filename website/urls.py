from django.urls import path
from .views import (
    index_website,
    parametros,
    cria_parametro,
    cria_parametro_tabela_padrao,
    edita_parametro_tabela_padrao,
    cria_feriado,
    exclui_feriado,
)

urlpatterns = [
    path("", index_website, name="index_website"),
    path("parametro/", parametros, name="parametro"),
    path("criaparametro/", cria_parametro, name="criaparametro"),
    path(
        "criaparametrotabelapadrao/",
        cria_parametro_tabela_padrao,
        name="criaparametrotabelapadrao",
    ),
    path(
        "editaparametrotabelapadrao/<int:idparametro>/",
        edita_parametro_tabela_padrao,
        name="editaparametrotabelapadrao",
    ),
    path("cria_feriado/", cria_feriado, name="criaferiado"),
    path("exclui_feriado/", exclui_feriado, name="exclui_feriado"),
]
