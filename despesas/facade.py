from django.http import JsonResponse
from django.template.loader import render_to_string

from despesas.models import Abastecimento


def create_despesas_context():
    abastecimento = get_abastecimento_all()
    context = {'abastecimento': abastecimento}
    return context


def get_abastecimento_all():
    return Abastecimento.objects.all()


def form_despesa(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    form = c_form(instance=c_instance)
    contexto = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view}
    data['html_html'] = render_to_string('despesas/formdespesa.html', contexto, request=request)
    print(data)
    c_return = JsonResponse(data)
    return c_return
