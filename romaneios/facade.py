import datetime
from cgitb import html
from decimal import Decimal

from clientes.models import Cliente
from django.http import JsonResponse
from django.template.loader import render_to_string

from romaneios.models import NotasClientes


def create_contexto_seleciona_cliente():
    clientes = Cliente.objects.all()
    lista = [{"idcliente": x.idCliente, "fantasia": x.Fantasia} for x in clientes]
    return lista


def create_contexto_seleciona_notas(id_cli):
    notas = NotasClientes.objects.filter(idCliente=id_cli)
    lista = [{notas: x.NumeroNota} for x in notas]
    return notas


def create_contexto_cliente(id_cli):
    cliente = Cliente.objects.get(idCliente=id_cli)
    return cliente.Fantasia


def create_data_cliente_selecionado(request, contexto):
    data = dict()
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)


def html_form_notas_cliente(request, contexto, data):
    data["html_form_notas_cliente"] = render_to_string(
        "romaneios/html_form_notas_cliente.html", contexto, request=request
    )
    return data

def hoje():
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    return hoje
