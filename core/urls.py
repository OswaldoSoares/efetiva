from django.urls import path
from core.views import index_core, visualizar_arquivo

urlpatterns = [
    path(
        "",
        index_core,
        name="index_core",
    ),
]
