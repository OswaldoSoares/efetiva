from django.urls import resolve
from django.test import TestCase
from django.http import HttpRequest

from minutas.views import index_minuta


class PaginaInicialMinutas(TestCase):

    def test_root_url_resolve_to_pagina_inicial_minutas_view(self):
        found = resolve('/minutas/')
        self.assertEqual(found.func, index_minuta)

    def test_pagina_inicial_minuta_retorna_index_html(self):
        request = HttpRequest()
        response = index_minuta(request)
        html = response.content.decode('utf8')
        self.assertTrue(html.startswith('<html>'))
        self.assertIn('<title>Módulo Minutas</title>', html)
        self.assertTrue(html.endswith('</html>'))
