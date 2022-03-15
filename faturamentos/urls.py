from django.urls import path
from .views import index_faturamento, minutas_faturar_cliente, cria_div_selecionada, cria_fatura, estorna_fatura, paga_fatura, imprime_fatura, email_fatura, fatura, delete_file

urlpatterns = [
    path('', index_faturamento, name='index_faturamento'),
    path('minutasfaturarcliente/<int:idcli>/', minutas_faturar_cliente, name='minutasfaturarcliente'),
    path('criadivselecionada/', cria_div_selecionada, name='criadivselecionada'),
    path('criafatura/', cria_fatura, name='criafatura'),
    path('estornafatura/<int:idfatura>/', estorna_fatura, name='estornafatura'),
    path('pagafatura/<int:idfatura>/', paga_fatura, name='pagafatura'),
    path('estornapagamentofatura/<int:idfatura>/', estorna_fatura, name='estornapagamentofatura'),
    path('imprimefatura/<int:idfatura>/', imprime_fatura, name='imprimefatura'),


    path('fatura/<int:idfatura>/', fatura, name='fatura'),
    path('email_fatura', email_fatura, name='email_fatura'),
    path('delete_file', delete_file, name='delete_file')
]