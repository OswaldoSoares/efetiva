from django.urls import path
from .views import index_faturamento, minutas_faturar_cliente, cria_div_selecionada

urlpatterns = [
    path('', index_faturamento, name='index_faturamento'),
    path('minutasfaturarcliente/<int:idcli>/', minutas_faturar_cliente, name='minutasfaturarcliente'),
    path('criadivselecionada/', cria_div_selecionada, name='criadivselecionada'),
]