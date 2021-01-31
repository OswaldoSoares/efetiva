from django.test import TestCase
from django.urls import reverse
from minutas.views import index_minuta


class URLTests(TestCase):
    def test_minuta_index(self):

        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
