from django.urls import path
from .views import index_despesas, cria_abastecimento


urlpatterns = [
    path('', index_despesas, name='index_despesas'),
    path('cria_abastecimento', cria_abastecimento, name='cria_abastecimento'),
]