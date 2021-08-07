from selenium import webdriver
import unittest


class AcessaModuloMinutas(unittest.TestCase):

    def setUp(self):
        self.browser = webdriver.Firefox()

    def tearDown(self):
        self.browser.quit()

    def test_verifica_pagina_inicial_modulo_miutas(self):
        self.browser.get('http://localhost:8000/minutas')

        # Título da pagina menciona a palavra Modulo
        self.assertIn('Módulo', self.browser.title)
        self.fail('Teste Finalizado!')


if __name__ == '__main__':
    unittest.main()
