from django.urls import path

from .views import index_romaneio

urlpatterns = [
    path(
        "",
        index_romaneio,
        name="index_romaneio",
    ),
]
