from django.urls import path
from .views import index_website

urlpatterns = [
    path('', index_website, name='index_website'),
]
