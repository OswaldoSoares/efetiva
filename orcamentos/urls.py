from django.urls import path
from .views import index_orcamento, cria_orcamento, edita_orcamento, orcamento_veiculo, orcamento_perimetro, \
    orcamento_ajudante

urlpatterns = [
    path('', index_orcamento, name='indexorcamento'),
    path('criaorcamento/', cria_orcamento, name='criaorcamento'),
    path('editaorcamento/<int:idorcamento>/', edita_orcamento, name='editaorcamento'),
    path('orcamentoveiculo', orcamento_veiculo, name='orcamentoveiculo'),
    path('orcamentoperimetro/', orcamento_perimetro, name='orcamentoperimetro'),
    path('orcamentoajudante/', orcamento_ajudante, name='orcamentoajudante'),
]
