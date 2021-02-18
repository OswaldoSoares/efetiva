from django.urls import path
from .views import index_orcamento, cria_orcamento, edita_orcamento, exclui_orcamento, email_orcamento, \
    orcamento_veiculo, orcamento_perimetro, orcamento_ajudante, orcamento_taxa_expedicao

urlpatterns = [
    path('', index_orcamento, name='indexorcamento'),
    path('criaorcamento/', cria_orcamento, name='criaorcamento'),
    path('editaorcamento/<int:idorcamento>/', edita_orcamento, name='editaorcamento'),
    path('excluiorcamento/<int:idorcamento>/', exclui_orcamento, name='excluiorcamento'),
    path('emailorcamento/<int:idorcamento>/', email_orcamento, name='emailorcamento'),
    path('orcamentoveiculo', orcamento_veiculo, name='orcamentoveiculo'),
    path('orcamentoperimetro/', orcamento_perimetro, name='orcamentoperimetro'),
    path('orcamentoajudante/', orcamento_ajudante, name='orcamentoajudante'),
    path('orcamentotaxaexpedicao/', orcamento_taxa_expedicao, name='orcamentotaxaexpedicao'),
]
