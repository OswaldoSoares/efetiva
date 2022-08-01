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


def create_contexto_seleciona_notas(id_cli, sort_nota):
    notas = NotasClientes.objects.filter(idCliente=id_cli).order_by(sort_nota)
    lista = [
        {
            "id_nota_clientes": x.idNotasClientes,
            "local_coleta": x.LocalColeta,
            "data_coleta": x.DataColeta,
            "numero_nota": x.NumeroNota,
            "destinatario": x.Destinatario,
            "endereco": x.Endereco
            + " "
            + x.Bairro
            + " "
            + x.CEP[0:5]
            + "-"
            + x.CEP[5:]
            + " "
            + x.Cidade
            + " "
            + x.Estado,
            "volume": x.Volume,
            "peso": x.Peso,
            "valor": x.Valor,
            "statusnota": x.StatusNota,
            "historico": x.Historico,
            "idcliente": x.idCliente_id,
        }
        for x in notas
    ]
    return lista


def create_contexto_cliente(id_cli):
    cliente = Cliente.objects.get(idCliente=id_cli)
    return cliente.Fantasia


def valida_notas_cliente(request):
    msg = dict()
    error = False
    # Valida Local Coleta
    local_coleta = request.POST.get("localcoleta")
    if local_coleta == "":
        msg["erro_local_coleta"] = "Obrigatório selecionar o local de coleta."
        error = True
    return error, msg


def create_data_cliente_selecionado(request, contexto):
    data = dict()
    html_lista_notas_cliente(request, contexto, data)
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)


def html_lista_notas_cliente(request, contexto, data):
    data["html_lista_notas_cliente"] = render_to_string(
        "romaneios/html_lista_notas_cliente.html", contexto, request=request
    )
    return data


def html_form_notas_cliente(request, contexto, data):
    data["html_form_notas_cliente"] = render_to_string(
        "romaneios/html_form_notas_cliente.html", contexto, request=request
    )
    return data


def hoje():
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    return hoje


def read_nota_post(request):
    nota_post = dict()
    nota_post["local_coleta"] = request.POST.get("localcoleta")
    nota_post["data_coleta"] = request.POST.get("datacoleta")
    nota_post["numero_nota"] = request.POST.get("numeronota")
    nota_post["destinatario"] = request.POST.get("destinatario")
    nota_post["endereco"] = request.POST.get("endereco")
    nota_post["cep"] = request.POST.get("cep")
    nota_post["bairro"] = request.POST.get("bairro")
    nota_post["cidade"] = request.POST.get("cidade")
    nota_post["estado"] = request.POST.get("estado")
    nota_post["volume"] = int(request.POST.get("volume"))
    nota_post["peso"] = request.POST.get("peso")
    nota_post["valor"] = request.POST.get("valor")
    nota_post["idcliente"] = request.POST.get("cliente")
    return nota_post


def read_nota_database(_id_not):
    nota = NotasClientes.objects.get(idNotasClientes=_id_not)
    nota_database = dict()
    nota_database["id_nota_clientes"] = nota.idNotasClientes
    nota_database["local_coleta"] = nota.LocalColeta
    nota_database["data_coleta"] = datetime.datetime.strftime(
        nota.DataColeta, "%Y-%m-%d"
    )
    nota_database["numero_nota"] = nota.NumeroNota
    nota_database["destinatario"] = nota.Destinatario
    nota_database["endereco"] = nota.Endereco
    nota_database["cep"] = nota.CEP
    nota_database["bairro"] = nota.Bairro
    nota_database["cidade"] = nota.Cidade
    nota_database["estado"] = nota.Estado
    nota_database["volume"] = nota.Volume
    nota_database["peso"] = str(nota.Peso)
    nota_database["valor"] = str(nota.Valor)
    nota_database["idcliente"] = nota.idCliente_id
    return nota_database


def save_notas_cliente(nota):
    obj = NotasClientes()
    obj.LocalColeta = nota["local_coleta"]
    obj.DataColeta = nota["data_coleta"]
    obj.NumeroNota = nota["numero_nota"]
    obj.Destinatario = nota["destinatario"]
    obj.Endereco = nota["endereco"]
    obj.CEP = nota["cep"]
    obj.Bairro = nota["bairro"]
    obj.Cidade = nota["cidade"]
    obj.Estado = nota["estado"]
    obj.Volume = nota["volume"]
    obj.Peso = nota["peso"]
    obj.Valor = nota["valor"]
    obj.StatusNota = "COLETAR"
    obj.idCliente_id = nota["idcliente"]
    obj.save()


def update_notas_cliente(nota_form, id_not):
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    obj = nota
    obj.LocalColeta = nota_form["local_coleta"]
    obj.DataColeta = nota_form["data_coleta"]
    obj.NumeroNota = nota_form["numero_nota"]
    obj.Destinatario = nota_form["destinatario"]
    obj.Endereco = nota_form["endereco"]
    obj.CEP = nota_form["cep"]
    obj.Bairro = nota_form["bairro"]
    obj.Cidade = nota_form["cidade"]
    obj.Estado = nota_form["estado"]
    obj.Volume = nota_form["volume"]
    obj.Peso = nota_form["peso"]
    obj.Valor = nota_form["valor"]
    obj.StatusNota = "COLETAR"
    obj.idCliente_id = nota_form["idcliente"]
    obj.save()

def delete_notas_cliente(id_not):
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    nota.delete()


def create_data_edita_nota(request, contexto):
    data = dict()
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)
