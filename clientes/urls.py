from django.urls import path
from .views import (
    index_cliente,
    consulta_cliente,
    cria_cliente,
    edita_cliente,
    exclui_cliente,
    cria_email_cliente,
    edita_email_cliente,
    exclui_email_cliente,
    cria_fone_cliente,
    edita_fone_cliente,
    exclui_fone_cliente,
    cria_cobranca_cliente,
    edita_cobranca_cliente,
    exclui_cobranca_cliente,
    cria_tabela_cliente,
    edita_tabela_cliente,
    edita_phkesc,
    cria_tabela_veiculo,
    edita_tabela_veiculo,
    cria_tabela_capacidade,
    edita_tabela_capacidade,
    exclui_tabela_capacidade,
    cria_tabela_perimetro,
    edita_tabela_perimetro,
    exclui_tabela_perimetro,
    criaformapgto,
)

urlpatterns = [
    path("", index_cliente, name="indexcliente"),
    path(
        "consultacliente/<int:idcliente>/",
        consulta_cliente,
        name="consultacliente",
    ),
    path("criacliente/", cria_cliente, name="criacliente"),
    path("editacliente/<int:idcliente>/", edita_cliente, name="editacliente"),
    path(
        "excluicliente/<int:idcliente>/", exclui_cliente, name="excluicliente"
    ),
    path("criaemailcliente/", cria_email_cliente, name="criaemailcliente"),
    path(
        "editaemailcliente/<int:idclienteemail>/",
        edita_email_cliente,
        name="editaemailcliente",
    ),
    path(
        "excluiemailcliente/<int:idclienteemail>/",
        exclui_email_cliente,
        name="excluiemailcliente",
    ),
    path("criafonecliente/", cria_fone_cliente, name="criafonecliente"),
    path(
        "editafonecliente/<int:idclientefone>/",
        edita_fone_cliente,
        name="editafonecliente",
    ),
    path(
        "excluifonecliente/<int:idclientefone>/",
        exclui_fone_cliente,
        name="excluifonecliente",
    ),
    path(
        "criacobrancacliente/",
        cria_cobranca_cliente,
        name="criacobrancacliente",
    ),
    path(
        "editacobrancacliente/<int:idcobrancacliente>/",
        edita_cobranca_cliente,
        name="editacobrancacliente",
    ),
    path(
        "excluicobrancacliente/<int:idcobrancacliente>/",
        exclui_cobranca_cliente,
        name="excluicobrancacliente",
    ),
    path("criatabelacliente/", cria_tabela_cliente, name="criatabelacliente"),
    path(
        "editatabelacliente/<int:idclientetabela>/",
        edita_tabela_cliente,
        name="editatabelacliente",
    ),
    path(
        "editaphkesc/<int:idclientetabela>/", edita_phkesc, name="editaphkesc"
    ),
    path("criatabelaveiculo/", cria_tabela_veiculo, name="criatabelaveiculo"),
    path(
        "editatabelaveiculo/<int:idtabelaveiculo>/",
        edita_tabela_veiculo,
        name="editatabelaveiculo",
    ),
    path(
        "criatabelacapacidade/",
        cria_tabela_capacidade,
        name="criatabelacapacidade",
    ),
    path(
        "editatabelacapacidade/<int:idtabelacapacidade>/",
        edita_tabela_capacidade,
        name="editatabelacapacidade",
    ),
    path(
        "excluitabelacapacidade/<int:idtabelacapacidade>/",
        exclui_tabela_capacidade,
        name="excluitabelacapacidade",
    ),
    path(
        "criatabelaperimetro/",
        cria_tabela_perimetro,
        name="criatabelaperimetro",
    ),
    path(
        "editatabelaperimetro/<int:idtabelaperimetro>/",
        edita_tabela_perimetro,
        name="editatabelaperimetro",
    ),
    path(
        "excluitabelaperimetro/<int:idtabelaperimetro>/",
        exclui_tabela_perimetro,
        name="excluitabelaperimetro",
    ),
    path("criaformapgto/", criaformapgto, name="criaformapgto"),
]
