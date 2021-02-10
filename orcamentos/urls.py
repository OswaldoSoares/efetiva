from django.urls import path
from .views import index_orcamento

urlpatterns = [
    path('', index_orcamento, name='indexorcamento')
]