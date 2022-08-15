import datetime
from cgitb import html
from decimal import Decimal

from clientes.models import Cliente
from django.http import JsonResponse
from django.template.loader import render_to_string

from romaneios.models import NotasClientes, NotasOcorrencias


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
            "contato": x.Contato,
            "informa": x.Informa,
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


def create_contexto_seleciona_ocorrencia(id_not, sort_ocorrencia):
    ocorrencia = NotasOcorrencias.objects.filter(idNotasClientes=id_not)
    lista = [
        {
            "id_notas_ocorrencia": x.idNotasOcorrencia,
            "data_ocorrencia": x.DataOcorrencia,
            "tipo_ocorrencia": x.TipoOcorrencia,
            "data_agendada": x.DataAgendada,
            "ocorrencia": x.Ocorrencia,
            "id_notas_clientes": x.idNotasClientes_id,
        }
        for x in ocorrencia
    ]
    return lista


def create_contexto_ocorrencia_notas(_id_not):
    notas = NotasClientes.objects.filter(idNotasClientes=_id_not)
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
            "contato": x.Contato,
            "informa": x.Informa,
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


def valida_ocorrencia(request):
    msg = dict()
    error = False
    # Valida Tipo Ocorrencia
    tipo_ocorrencia = request.POST.get("tipo_ocorrencia")
    if tipo_ocorrencia == "":
        msg["erro_tipo_ocorrencia"] = "Obrigatório selecionar o tipo de ocorrencia."
        error = True
    return error, msg


def create_data_cliente_selecionado(request, contexto):
    data = dict()
    html_lista_notas_cliente(request, contexto, data)
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)


def create_data_ocorrencia_selecionada(request, contexto):
    data = dict()
    html_lista_ocorrencia(request, contexto, data)
    return JsonResponse(data)


def create_data_nota_selecionada(request, contexto):
    data = dict()
    html_lista_ocorrencia(request, contexto, data)
    return JsonResponse(data)


def html_lista_ocorrencia(request, contexto, data):
    data["html_lista_ocorrencia"] = render_to_string(
        "romaneios/html_lista_ocorrencia.html", contexto, request=request
    )
    return data


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
    nota_post["contato"] = request.POST.get("contato")
    nota_post["informa"] = request.POST.get("informa")
    nota_post["volume"] = int(request.POST.get("volume"))
    nota_post["peso"] = request.POST.get("peso")
    nota_post["valor"] = request.POST.get("valor")
    nota_post["idcliente"] = request.POST.get("cliente")
    return nota_post


def read_ocorrencia_post(request):
    ocorrencia_post = dict()
    ocorrencia_post["data_ocorrencia"] = request.POST.get("data_ocorrencia")
    ocorrencia_post["tipo_ocorrencia"] = request.POST.get("tipo_ocorrencia")
    ocorrencia_post["data_agendade"] = request.POST.get("data_agendada")
    ocorrencia_post["ocorrencia"] = request.POST.get("ocorrencia")
    ocorrencia_post["idnotaclientes"] = request.POST.get("id_nota_clientes")
    return ocorrencia_post


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
    nota_database["contato"] = nota.Contato
    nota_database["informa"] = nota.Informa
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
    obj.Contato = nota["contato"]
    obj.Informa = nota["informa"]
    obj.Volume = nota["volume"]
    obj.Peso = nota["peso"]
    obj.Valor = nota["valor"]
    obj.StatusNota = "PENDENTE"
    obj.idCliente_id = nota["idcliente"]
    obj.save()


def save_ocorrencia(ocorrencia):
    obj = NotasOcorrencias()
    obj.DataOcorrencia = ocorrencia["data_ocorrencia"]
    obj.TipoOcorrencia = ocorrencia["tipo_ocorrencia"]
    obj.DataAgendada = ocorrencia["data_agendade"]
    obj.Ocorrencia = ocorrencia["ocorrencia"]
    obj.idNotasClientes_id = ocorrencia["idnotaclientes"]
    obj.save()
    nota = NotasClientes.objects.get(idNotasClientes=ocorrencia["idnotaclientes"])
    obj = nota
    obj.StatusNota = ocorrencia["tipo_ocorrencia"]
    obj.save(update_fields=["StatusNota"])


def update_ocorrencia(ocorrencia_form, id_ocor):
    ocorrencia = NotasOcorrencias.objects.get(idNotasOcorrencia=id_ocor)
    obj = ocorrencia
    obj.DataOcorrencia = ocorrencia_form["data_ocorrencia"]
    obj.TipoOcorrencia = ocorrencia_form["tipo_ocorrencia"]
    obj.DataAgendada = ocorrencia_form["data_agendade"]
    obj.Ocorrencia = ocorrencia_form["ocorrencia"]
    obj.idNotasClientes_id = ocorrencia_form["idnotaclientes"]
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
    obj.Contato = nota_form["contato"]
    obj.Informa = nota_form["informa"]
    obj.Volume = nota_form["volume"]
    obj.Peso = nota_form["peso"]
    obj.Valor = nota_form["valor"]
    # obj.StatusNota = ""
    obj.idCliente_id = nota_form["idcliente"]
    obj.save()


def delete_notas_cliente(id_not):
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    nota.delete()


def create_data_edita_nota(request, contexto):
    data = dict()
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)
