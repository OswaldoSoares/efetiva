from django.urls import path
from core.views import index_core, visualizar_arquivo

urlpatterns = [
    path(
        "",
        index_core,
        name="index_core",
    ),
    path(
        "visualizar_arquivo/<int:id_file_upload>",
        visualizar_arquivo,
        name="visualizar_arquivo",
    ),
]
