"""transefetiva URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from clientes import urls as clientes_urls
from faturamentos import urls as faturamentos_urls
from minutas import urls as minutas_urls
from pessoas import urls as pessoas_urls
from usuarios import urls as usuarios_urls
from veiculos import urls as veiculos_urls
from website import urls as website_urls
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('clientes/', include(clientes_urls)),
    path('faturamentos/', include(faturamentos_urls)),
    path('minutas/', include(minutas_urls)),
    path('pessoas/', include(pessoas_urls)),
    path('usuarios/', include(usuarios_urls)),
    path('veiculos/', include(veiculos_urls)),
    path('', include(website_urls)),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler403 = 'usuarios.views.my_403_template'
