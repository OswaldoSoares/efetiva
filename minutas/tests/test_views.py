from django.urls import resolve
from django.test import TestCase
from minutas.views import index_minuta

class PaginaInicialMinutas(TestCase):

    def test_root_url_resolve_to_pagina_inicial_minutas_view(self):
        found = resolve('/minutas/')
        self.assertEqual(found.func, index_minuta)
