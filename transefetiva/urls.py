from clientes import urls as clientes_urls
from core import urls as core_urls
from despesas import urls as despesas_urls
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from faturamentos import urls as faturamentos_urls
from minutas import urls as minutas_urls
from orcamentos import urls as orcamentos_urls
from pagamentos import urls as pagamentos_urls
from pessoas import urls as pessoas_urls
from romaneios import urls as romaneios_urls
from usuarios import urls as usuarios_urls
from veiculos import urls as veiculos_urls
from website import urls as website_urls

urlpatterns = (
    [
        path("admin/", admin.site.urls),
        path("clientes/", include(clientes_urls)),
        path("core/", include(core_urls)),
        path("despesas/", include(despesas_urls)),
        path("faturamentos/", include(faturamentos_urls)),
        path("minutas/", include(minutas_urls)),
        path("orcamentos/", include(orcamentos_urls)),
        path("pagamentos/", include(pagamentos_urls)),
        path("pessoas/", include(pessoas_urls)),
        path("romaneios/", include(romaneios_urls)),
        path("usuarios/", include(usuarios_urls)),
        path("veiculos/", include(veiculos_urls)),
        path("", include(website_urls)),
    ]
    + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
)

handler403 = "usuarios.views.my_403_template"
handler404 = "usuarios.views.my_404_template"
