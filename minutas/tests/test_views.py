from django.test import TestCase

class InicialTeste(TestCase):

    def test_bad_soma(self):
        self.assertEqual(1 + 1, 3)

