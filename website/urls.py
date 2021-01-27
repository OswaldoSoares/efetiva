from django.urls import path
from .views import index_website, parametros

urlpatterns = [
    path('', index_website, name='index_website'),
    path('parametros', parametros, name='parametros'),
]
