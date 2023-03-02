import pytest
from django.template import loader
from django.test import RequestFactory


def test_template_html_form_paga_recibo_colaborador():
    template_name = "pagamentos/html_form_paga_recibo_colaborador.html"
    try:
        template = loader.get_template(template_name)
    except loader.TemplateDoesNotExist:
        pytest.fail(f"{template_name} não existe.")
