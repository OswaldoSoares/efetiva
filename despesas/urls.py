from django.urls import path
from .views import index_despesas


urlpatterns = [
    path('', index_despesas, name='index_despesas'),

]