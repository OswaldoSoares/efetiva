from django.urls import path
from .views import indexpessoal, cria_pessoa, consulta_pessoa, criadocpessoa, criafonepessoa, edita_pessoa, \
    excluipessoa, excluidocpessoa, excluifonepessoa, criacontapessoa, excluicontapessoa, edita_salario, cria_vale,\
    cria_contracheque, seleciona_contracheque, cria_contrachequeitens


urlpatterns = [
    path('', indexpessoal, name='indexpessoal'),
    path('consultapessoa/<int:idpessoa>/', consulta_pessoa, name='consultapessoa'),
    path('criapessoa/', cria_pessoa, name='criapessoa'),
    path('editapessoa/<int:idpessoa>/', edita_pessoa, name='editapessoa'),
    path('excluipessoa/<int:idpes>/', excluipessoa, name='excluipessoa'),
    path('criadocpessoa/', criadocpessoa, name='criadocpessoa'),
    path('excluidocpessoa/<int:idpesdoc>/', excluidocpessoa, name='excluidocpessoa'),
    path('criafonepessoa/', criafonepessoa, name='criafonepessoa'),
    path('excluifomepessoa/<int:idpesfon>', excluifonepessoa, name='excluifonepessoa'),
    path('criacontapessoa/', criacontapessoa, name='criacontapessoa'),
    path('excluicontapessoa/<int:idpescon>/', excluicontapessoa, name='excluicontapessoa'),
    path('editasalario/', edita_salario, name='editasalario'),
    path('criavale/', cria_vale, name='criavale'),
    path('criacontracheque/', cria_contracheque, name='criacontracheque'),
    path('selecionacontracheque/', seleciona_contracheque, name='selecionacontracheque'),
    path('criacontrachequeitens/', cria_contrachequeitens, name='criacontrachequeitens')
]
