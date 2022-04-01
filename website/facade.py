import email
from django.http import JsonResponse
from django.template.loader import render_to_string

from website.forms import CadastraFeriado
from .models import Parametros
from clientes.facade import get_cliente

from imap_tools import MailBox, AND


class Feriados():
    def __init__(self, chave, valor):
        self.chave = chave
        self.valor = valor
        self.feriados = self.get_feriados()

    @staticmethod
    def get_feriados():
        feriados = Parametros.objects.filter(Chave='FERIADO').order_by('-Valor')
        lista = [itens.Valor for itens in feriados]
        return lista


def create_parametro_context():
    tabela_padrao = get_tabela_padrao()
    tabela_padrao_cliente = ''
    if tabela_padrao:
        tabela_padrao_cliente = get_cliente(tabela_padrao[0].Valor)
    lista_feriados = Feriados('Lista', 'Feriados')
    form_feriado = CadastraFeriado()
    context = {'tabela_padrao': tabela_padrao, 'tabela_padrao_cliente': tabela_padrao_cliente,
               'form_feriado': form_feriado, 'lista_feriados': lista_feriados}
    return context


def get_parametros_all():
    """

    :return:
    """
    return Parametros.objects.all()


def get_parametro(idparametro):
    """

    :return:
    """
    return Parametros.objects.filter(idParametro=idparametro)


def get_tabela_padrao():
    """

    :return:
    """
    return Parametros.objects.filter(Chave='TABELA PADRAO')


def salva_parametro(chave, valor):
    parametro = Parametros()
    obj = parametro
    obj.Chave = chave
    obj.Valor = valor
    obj.save()


def form_parametro(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    if c_idobj:
        c_instance = Parametros.objects.get(idParametro=c_idobj)
    if request.method == 'POST':
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
    else:
        form = c_form(instance=c_instance)
    context = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view}
    data['html_form'] = render_to_string('website/formparametros.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_parametro(request, c_idobj, c_url, c_view):
    data = dict()
    c_queryset = get_parametro(c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {'c_url': c_url, 'c_view': c_view, 'c_queryset': c_queryset}
    data['html_form'] = render_to_string('clientes/formcliente.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return


def conecta_imap():
    usuario = 'operacional.efetiva@terra.com.br'
    senha = 'mau159753'

    meu_email = MailBox('imap.terra.com.br').login(usuario, senha)

    lista_emails = meu_email.fetch(AND(from_='faturamento@fulgor1923.com.br'))
    for x in lista_emails:
        print(x.text)
    return lista_emails