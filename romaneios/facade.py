import datetime
import os
import xml.etree.ElementTree as ET
from cgitb import html
from decimal import Decimal
from xml.dom import ValidationErr

import requests
from clientes.models import Cliente
from django.db.models import Max
from django.http import JsonResponse
from django.template.loader import render_to_string
from website.facade import nome_curto
from website.models import FileUpload

from romaneios.models import (NotasClientes, NotasOcorrencias, RomaneioNotas,
                              Romaneios)


def create_contexto_seleciona_cliente():
    clientes = Cliente.objects.all()
    lista = [{"idcliente": x.idCliente, "fantasia": x.Fantasia} for x in clientes]
    return lista


def create_contexto_seleciona_ocorrencia(idnota, sort_ocorrencia):
    ocorrencia = NotasOcorrencias.objects.filter(idNotasClientes=idnota)
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


def create_contexto_ocorrencia_notas(idnota):
    notas = NotasClientes.objects.filter(idNotasClientes=idnota)
    lista = create_lista_notas_clientes(notas)
    return lista


def create_contexto_cliente(id_cli):
    cliente = Cliente.objects.get(idCliente=id_cli)
    return cliente.Fantasia


def valida_seleciona_cliente(request):
    msg = dict()
    error = False
    seleciona = request.POST.get("cliente")
    if seleciona == "0":
        msg["erro_seleciona"] = "Obrigatório selecionar um cliente."
        error = True
    return error, msg


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


def create_data_seleciona_cliente(request, contexto):
    data = dict()
    html_form_seleciona_cliente(request, contexto, data)
    return JsonResponse(data)


def html_form_seleciona_cliente(request, contexto, data):
    data["html_form_seleciona_cliente"] = render_to_string(
        "romaneios/html_form_seleciona_cliente.html", contexto, request=request
    )
    return data


def create_data_cliente_selecionado(request, contexto):
    data = dict()
    html_lista_notas_cliente(request, contexto, data)
    html_form_notas_cliente(request, contexto, data)
    html_form_romaneios(request, contexto, data)
    html_lista_romaneios(request, contexto, data)
    html_filtro_notas_romaneios(request, contexto, data)
    html_quantidade_notas(request, contexto, data)
    return JsonResponse(data)


def html_quantidade_notas(request, contexto, data):
    data["html_quantidade_notas"] = render_to_string(
        "romaneios/html_quantidade_notas.html", contexto, request=request
    )
    return data


def create_data_sort_notas(request, contexto):
    data = dict()
    if contexto["tipo_sort"] == "completo":
        html_lista_notas_cliente(request, contexto, data)
    else:
        html_card_lista_notas_cliente(request, contexto, data)
    return JsonResponse(data)


def create_data_filtro_nota(request, contexto):
    data = dict()
    data["id_rom"] = contexto["id_rom"]
    html_lista_notas_cliente(request, contexto, data)
    html_lista_notas_romaneio(request, contexto, data)
    return JsonResponse(data)


def create_data_filtro_status_reduzida(request, contexto):
    data = dict()
    html_card_lista_notas_cliente(request, contexto, data)
    html_quantidade_notas(request, contexto, data)
    return JsonResponse(data)


def create_data_romaneios(request, contexto):
    data = dict()
    html_lista_romaneios(request, contexto, data)
    return JsonResponse(data)


def html_lista_romaneios(request, contexto, data):
    data["html_lista_romaneios"] = render_to_string(
        "romaneios/html_lista_romaneios.html", contexto, request=request
    )
    return data


def create_data_ocorrencia_selecionada(request, contexto):
    data = dict()
    html_lista_ocorrencia(request, contexto, data)
    html_lista_notas_romaneio(request, contexto, data)
    html_quantidade_notas(request, contexto, data)
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
        "romaneios/html_card_lista_notas_cliente.html", contexto, request=request
    )
    return data


def html_card_lista_notas_cliente(request, contexto, data):
    data["html_card_lista_notas_cliente"] = render_to_string(
        "romaneios/html_card_lista_notas_cliente.html", contexto, request=request
    )
    return data


def html_form_notas_cliente(request, contexto, data):
    data["html_form_notas_cliente"] = render_to_string(
        "romaneios/html_form_notas_cliente.html", contexto, request=request
    )
    return data


def html_form_romaneios(request, contexto, data):
    data["html_form_romaneios"] = render_to_string(
        "romaneios/html_form_romaneios.html", contexto, request=request
    )
    return data


# TODO remover para facade website
def hoje():
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    return hoje


def read_nota_post(request):
    nota_post = dict()
    nota_post["local_coleta"] = request.POST.get("localcoleta")
    nota_post["emitente"] = request.POST.get("emitente")
    nota_post["endereco_emi"] = request.POST.get("endereco_emi")
    nota_post["cep_emi"] = request.POST.get("cep_emi")
    nota_post["bairro_emi"] = request.POST.get("bairro_emi")
    nota_post["cidade_emi"] = request.POST.get("cidade_emi")
    nota_post["estado_emi"] = request.POST.get("estado_emi")
    nota_post["data_nota"] = request.POST.get("datanota")
    nota_post["serie_nota"] = request.POST.get("serienota")
    nota_post["numero_nota"] = request.POST.get("numeronota")
    nota_post["destinatario"] = request.POST.get("destinatario")
    nota_post["cnpj"] = request.POST.get("cnpj")
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
    nota_database["emitente"] = nota.Emitente
    nota_database["endereco_emi"] = nota.Endereco_emi
    nota_database["cep_emi"] = nota.CEP_emi
    nota_database["bairro_emi"] = nota.Bairro_emi
    nota_database["cidade_emi"] = nota.Cidade_emi
    nota_database["estado_emi"] = nota.Estado_emi
    nota_database["data_nota"] = datetime.datetime.strftime(nota.DataColeta, "%Y-%m-%d")
    nota_database["serie_nota"] = nota.SerieNota
    nota_database["numero_nota"] = nota.NumeroNota
    nota_database["destinatario"] = nota.Destinatario
    nota_database["cnpj"] = nota.CNPJ
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


def read_nota_xml(nota):
    nota_xml = dict()
    nota_xml["local_coleta"] = nota["local_coleta"]
    nota_xml["emitente"] = nota['emitente']
    nota_xml["endereco_emi"] = nota['endereco_emi']
    nota_xml["cep_emi"] = nota['cep_emi']
    nota_xml["bairro_emi"] = nota['bairro_emi']
    nota_xml["cidade_emi"] = nota['cidade_emi']
    nota_xml["estado_emi"] = nota['estado_emi']
    nota_xml["data_nota"] = datetime.datetime.strftime(nota['data_nf'], "%Y-%m-%d")
    nota_xml["serie_nota"] = nota['serie_nf']
    nota_xml["numero_nota"] = nota['numero_nf']
    nota_xml["destinatario"] = nota['destinatario']
    nota_xml["cnpj"] = nota['cnpj']
    nota_xml["endereco"] = nota['endereco']
    nota_xml["cep"] = nota['cep']
    nota_xml["bairro"] = nota['bairro']
    nota_xml["cidade"] = nota['cidade']
    nota_xml["estado"] = nota['estado']
    nota_xml["contato"] = nota['telefone']
    nota_xml["informa"] = nota['informa']
    nota_xml["volume"] = nota['volume']
    nota_xml["peso"] = str(nota['peso'])
    nota_xml["valor"] = str(nota['valor'])
    nota_xml["idcliente"] = nota['id_cliente']
    return nota_xml


def save_notas_cliente(nota):
    obj = NotasClientes()
    obj.LocalColeta = nota["local_coleta"]
    obj.Emitente = nota["emitente"]
    obj.Endereco_emi = nota["endereco_emi"]
    obj.CEP_emi = nota["cep_emi"]
    obj.Bairro_emi = nota["bairro_emi"]
    obj.Cidade_emi = nota["cidade_emi"]
    obj.Estado_emi = nota["estado_emi"]
    obj.DataColeta = nota["data_nota"]
    obj.SerieNota = nota["serie_nota"]
    obj.NumeroNota = nota["numero_nota"]
    obj.Destinatario = nota["destinatario"]
    obj.CNPJ = nota["cnpj"]
    obj.Endereco = nota["endereco"]
    obj.CEP = nota["cep"]
    obj.Bairro = nota["bairro"]
    obj.Cidade = nota["cidade"]
    obj.Estado = nota["estado"]
    obj.Contato = nota["contato"]
    obj.Informa = nota["informa"][0:299]
    obj.Volume = nota["volume"]
    obj.Peso = nota["peso"]
    obj.Valor = nota["valor"]
    obj.StatusNota = "NOTA CADASTRADA"
    obj.idCliente_id = nota["idcliente"]
    obj.save()


def save_ocorrencia(ocorrencia, idcliente):
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
    if not ocorrencia["ocorrencia"]:
        ocorrencia["ocorrencia"] = "ENTREGA EFETUADA COM SUCESSO."
    texto = f"""
    Nota: {nota.NumeroNota} - Valor R$ {nota.Valor} - Peso: {nota.Peso} - Volume {nota.Volume}
    Emitente: {nota.Emitente}
    Endereço: {nota.Endereco_emi} - {nota.Bairro_emi} - CEP: {nota.CEP_emi} - {nota.Cidade_emi} - {nota.Estado_emi}
    Destinatário: {nota.Destinatario}
    Endereço: {nota.Endereco} - {nota.Bairro} - CEP: {nota.CEP} - {nota.Cidade} - {nota.Estado}
    Tipo de Ocorrência: {ocorrencia["tipo_ocorrencia"]}
    Ocorrência: {ocorrencia["ocorrencia"]}
    """
    send_message(texto, idcliente)


def altera_status_rota(id_rom, id_not):
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    obj = NotasOcorrencias()
    obj.DataOcorrencia = romaneio.DataRomaneio
    obj.TipoOcorrencia = "EM ROTA"
    obj.DataAgendada = romaneio.DataRomaneio
    obj.Ocorrencia = f"INSERIDA NO ROMANEIO {romaneio.Romaneio}"
    obj.idNotasClientes_id = id_not
    obj.save()
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    obj = nota
    obj.StatusNota = "EM ROTA"
    obj.save(update_fields=["StatusNota"])


def altera_status_remove_romaneio(id_rom, id_not, hoje):
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    obj = NotasOcorrencias()
    obj.DataOcorrencia = hoje
    obj.TipoOcorrencia = "PENDENTE"
    obj.DataAgendada = hoje
    obj.Ocorrencia = f"REMOVIDA DO ROMANEIO {romaneio.Romaneio}"
    obj.idNotasClientes_id = id_not
    obj.save()
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    obj = nota
    obj.StatusNota = "PENDENTE"
    obj.save(update_fields=["StatusNota"])


# TODO FUNÇÃO NÃO ESTÁ SENDO USADA - VERIFICAR NECESSIDADE 28/03/2023
def update_ocorrencia(ocorrencia_form, id_ocor):
    ocorrencia = NotasOcorrencias.objects.get(idNotasOcorrencia=id_ocor)
    obj = ocorrencia
    obj.DataOcorrencia = ocorrencia_form["data_ocorrencia"]
    obj.TipoOcorrencia = ocorrencia_form["tipo_ocorrencia"]
    obj.DataAgendada = ocorrencia_form["data_agendade"]
    obj.Ocorrencia = ocorrencia_form["ocorrencia"]
    obj.idNotasClientes_id = ocorrencia_form["idnotaclientes"]
    obj.save()


def delete_ocorrencia(idnotasocorrencia, idnota):
    ocorrencia = NotasOcorrencias.objects.get(idNotasOcorrencia=idnotasocorrencia)
    obj = ocorrencia
    obj.delete()
    ultimo_status = (
        NotasOcorrencias.objects.filter(idNotasClientes_id=idnota)
        .values("TipoOcorrencia")
        .last()
    )
    nota = NotasClientes.objects.get(idNotasClientes=idnota)
    obj = nota
    if not ultimo_status:
        obj.StatusNota = "PENDENTE"
    else:
        obj.StatusNota = ultimo_status["TipoOcorrencia"]
    obj.save(update_fields=["StatusNota"])


def update_notas_cliente(nota_form, id_not):
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    obj = nota
    obj.LocalColeta = nota_form["local_coleta"]
    obj.Emitente = nota_form["emitente"]
    obj.Endereco_emi = nota_form["endereco_emi"]
    obj.CEP_emi = nota_form["cep_emi"]
    obj.Bairro_emi = nota_form["bairro_emi"]
    obj.Cidade_emi = nota_form["cidade_emi"]
    obj.Estado_emi = nota_form["estado_emi"]
    obj.DataColeta = nota_form["data_nota"]
    obj.SerieNota = nota_form["serie_nota"]
    obj.NumeroNota = nota_form["numero_nota"]
    obj.Destinatario = nota_form["destinatario"]
    obj.CNPJ = nota_form["cnpj"]
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


def delete_nota_romaneio(id_romaneio_nota):
    nota_romaneio = RomaneioNotas.objects.get(idRomaneioNotas=id_romaneio_nota)
    nota_romaneio.delete()


def create_data_edita_nota(request, contexto):
    data = dict()
    html_form_notas_cliente(request, contexto, data)
    return JsonResponse(data)


def create_data_edita_romaneio(request, contexto):
    data = dict()
    html_form_romaneios(request, contexto, data)
    return JsonResponse(data)


def read_romaneio_post(request):
    romaneio = dict()
    romaneio["data_romaneio"] = request.POST.get("data_romaneio")
    romaneio["motorista"] = request.POST.get("motorista")
    romaneio["veiculo"] = request.POST.get("veiculo")
    romaneio["cliente"] = request.POST.get("idCliente")
    return romaneio


def read_romaneio_database(id_rom):
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    romaneio_database = dict()
    romaneio_database["idromaneio"] = romaneio.idRomaneio
    romaneio_database["DataRomaneio"] = datetime.datetime.strftime(
        romaneio.DataRomaneio, "%Y-%m-%d"
    )
    romaneio_database["motorista"] = romaneio.idMotorista
    romaneio_database["veiculo"] = romaneio.idVeiculo
    romaneio_database["cliente"] = romaneio.idCliente
    return romaneio_database


def save_romaneio(romaneio):
    num_rom = Romaneios.objects.aggregate(numero=Max("Romaneio"))
    numero = 1
    if num_rom["numero"]:
        numero += num_rom["numero"]
    obj = Romaneios()
    obj.Romaneio = numero
    obj.DataRomaneio = romaneio["data_romaneio"]
    obj.idMotorista_id = romaneio["motorista"]
    obj.idVeiculo_id = romaneio["veiculo"]
    obj.idCliente_id = romaneio["cliente"]
    obj.save()


def update_romaneio(romaneio_form, id_rom):
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    obj = romaneio
    obj.DataRomaneio = romaneio_form["data_romaneio"]
    obj.idMotorista_id = romaneio_form["motorista"]
    obj.idVeiculo_id = romaneio_form["veiculo"]
    obj.save()


def create_contexto_romaneios(idcliente):
    romaneios = Romaneios.objects.filter(idCliente=idcliente, Fechado=False).order_by(
        "-Romaneio"
    )
    lista = [
        {
            "idromaneio": x.idRomaneio,
            "romaneio": x.Romaneio,
            "data_romaneio": x.DataRomaneio,
            "motorista": x.idMotorista,
            "veiculo": x.idVeiculo,
        }
        for x in romaneios
    ]
    if lista:
        for index, itens in enumerate(lista):
            if lista[index]["motorista"]:
                lista[index]["apelido"] = nome_curto(lista[index]["motorista"].Nome)
    return lista


def create_contexto_notas_romaneio(idromaneio):
    notas_romaneio = RomaneioNotas.objects.filter(idRomaneio=idromaneio)
    lista = [
        {
            "idromaneionotas": x.idRomaneioNotas,
            "idnotasclientes": x.idNotasClientes,
        }
        for x in notas_romaneio
    ]
    return lista


def create_contexto_romaneio_tem_nota(idnota):
    romaneio = RomaneioNotas.objects.filter(idNotasClientes=idnota)
    numero_romaneio = None
    if romaneio:
        romaneio = romaneio.latest("idRomaneio_id")
        numero_romaneio = romaneio.idRomaneio.Romaneio
    return numero_romaneio


def create_data_lista_notas_romaneio(request, contexto):
    data = dict()
    html_lista_notas_cliente(request, contexto, data)
    html_lista_notas_romaneio(request, contexto, data)
    html_quantidade_notas(request, contexto, data)
    return JsonResponse(data)


def html_lista_notas_romaneio(request, contexto, data):
    data["html_lista_notas_romaneio"] = render_to_string(
        "romaneios/html_lista_notas_romaneio.html", contexto, request=request
    )
    return data


def html_filtro_notas_romaneios(request, contexto, data):
    data["html_filtro_notas_romaneios"] = render_to_string(
        "romaneios/html_filtro_notas_romaneios.html", contexto, request=request
    )
    return data


def create_contexto_filtro_status():
    status_nota = (
        NotasClientes.objects.values("StatusNota").distinct().order_by("StatusNota")
    )
    return status_nota


def create_contexto_quantidades_status(idcliente):
    notas = NotasClientes.objects.filter(idCliente=idcliente)
    rota = len(notas.filter(StatusNota="EM ROTA"))
    cadastrada = len(notas.filter(StatusNota="NOTA CADASTRADA"))
    pendente = len(notas.filter(StatusNota="PENDENTE"))
    recusada = len(notas.filter(StatusNota="RECUSADA"))
    coletada = len(notas.filter(StatusNota="COLETADA"))
    lista = [
        {
            "rota": rota,
            "cadastrada": cadastrada,
            "pendente": pendente,
            "recusada": recusada,
            "coletada": coletada,
        }
    ]
    return lista


def create_contexto_seleciona_romaneio(id_rom):
    romaneio = Romaneios.objects.filter(idRomaneio=id_rom)
    lista = [
        {
            "idromaneio": x.idRomaneio,
            "romaneio": x.Romaneio,
            "data_romaneio": x.DataRomaneio,
            "motorista": x.idMotorista,
            "veiculo": x.idVeiculo,
            "fechado": x.Fechado,
        }
        for x in romaneio
    ]
    if lista:
        for index, itens in enumerate(lista):
            if lista[index]["motorista"]:
                lista[index]["apelido"] = nome_curto(lista[index]["motorista"].Nome)
    return lista


def lista_locais():
    destinatarios = (
        NotasClientes.objects.values("Destinatario").distinct().order_by("Destinatario")
    )
    emitentes = NotasClientes.objects.values("Emitente").distinct().order_by("Emitente")
    lista = []
    for x in destinatarios:
        if x["Destinatario"]:
            lista.append(x["Destinatario"].strip())
    for x in emitentes:
        if x["Emitente"]:
            lista.append(x["Emitente"].strip())
    lista = list(set(lista))
    lista.sort()
    return lista


def lista_enderecos():
    destinatarios = (
        NotasClientes.objects.values("Endereco").distinct().order_by("Endereco")
    )
    emitentes = (
        NotasClientes.objects.values("Endereco_emi").distinct().order_by("Endereco_emi")
    )
    lista = []
    for x in destinatarios:
        if x["Endereco"]:
            lista.append(x["Endereco"])
    for x in emitentes:
        if x["Endereco_emi"]:
            lista.append(x["Endereco_emi"])
    lista = list(set(lista))
    lista.sort()
    return lista


def lista_bairros():
    destinatarios = NotasClientes.objects.values("Bairro").distinct().order_by("Bairro")
    emitentes = (
        NotasClientes.objects.values("Bairro_emi").distinct().order_by("Bairro_emi")
    )
    lista = []
    for x in destinatarios:
        if x["Bairro"]:
            lista.append(x["Bairro"])
    for x in emitentes:
        if x["Bairro_emi"]:
            lista.append(x["Bairro_emi"])
    lista = list(set(lista))
    lista.sort()
    return lista


def create_data_busca_endereco(local):
    destinatarios = NotasClientes.objects.filter(Destinatario=local)
    emitentes = NotasClientes.objects.filter(Emitente=local)
    lista = []
    for x in destinatarios:
        if x.Endereco:
            lista.append(
                {
                    "endereco": x.Endereco,
                    "bairro": x.Bairro,
                    "cep": x.CEP,
                    "cidade": x.Cidade,
                    "estado": x.Estado,
                }
            )
    for x in emitentes:
        if x.Endereco_emi:
            lista.append(
                {
                    "endereco": x.Endereco_emi,
                    "bairro": x.Bairro_emi,
                    "cep": x.CEP_emi,
                    "cidade": x.Cidade_emi,
                    "estado": x.Estado_emi,
                }
            )
    endereco_completo = []
    msg = False
    if len(lista) > 0:
        # Remove dicionários repetidos usando um loop e set()
        lista_sem_repeticao = list(
            set(tuple(sorted(dicionario.items())) for dicionario in lista)
        )
        # Converte os dicionários de volta para sua forma original
        lista_sem_repeticao = [dict(item) for item in lista_sem_repeticao]
        endereco_completo = lista_sem_repeticao[-1]
        if len(lista_sem_repeticao) > 1:
            msg = "ESTE EMITENTE POSSUI MAIS DE UM ENDEREÇO, VERIFIQUE SE ESTÁ CORRETO"
    contexto = {"endereco": endereco_completo, "mensagem": msg}
    return JsonResponse(contexto)


def save_nota_romaneio(id_nota, id_romaneio):
    obj = RomaneioNotas()
    obj.idNotasClientes_id = id_nota
    obj.idRomaneio_id = id_romaneio
    obj.save()


def ler_nota_xml(nota):
    tree = ET.parse(nota)
    doc = tree.getroot()
    nfe = "{http://www.portalfiscal.inf.br/nfe}NFe"
    infnfe = "{http://www.portalfiscal.inf.br/nfe}infNFe"
    ide = "{http://www.portalfiscal.inf.br/nfe}ide"
    dhemi = "{http://www.portalfiscal.inf.br/nfe}dhEmi"
    serie = "{http://www.portalfiscal.inf.br/nfe}serie"
    nnf = "{http://www.portalfiscal.inf.br/nfe}nNF"
    emit = "{http://www.portalfiscal.inf.br/nfe}emit"
    ender_emit = "{http://www.portalfiscal.inf.br/nfe}enderEmit"
    dest = "{http://www.portalfiscal.inf.br/nfe}dest"
    xcnpj = "{http://www.portalfiscal.inf.br/nfe}CNPJ"
    xnome = "{http://www.portalfiscal.inf.br/nfe}xNome"
    ender_dest = "{http://www.portalfiscal.inf.br/nfe}enderDest"
    xlgr = "{http://www.portalfiscal.inf.br/nfe}xLgr"
    nro = "{http://www.portalfiscal.inf.br/nfe}nro"
    xcpl = "{http://www.portalfiscal.inf.br/nfe}xCpl"
    xbairro = "{http://www.portalfiscal.inf.br/nfe}xBairro"
    xcep = "{http://www.portalfiscal.inf.br/nfe}CEP"
    xmun = "{http://www.portalfiscal.inf.br/nfe}xMun"
    estado = "{http://www.portalfiscal.inf.br/nfe}UF"
    telefone = "{http://www.portalfiscal.inf.br/nfe}Telefone"
    inf_adic = "{http://www.portalfiscal.inf.br/nfe}infAdic"
    inf_cpl = "{http://www.portalfiscal.inf.br/nfe}infCpl"
    transp = "{http://www.portalfiscal.inf.br/nfe}transp"
    vol = "{http://www.portalfiscal.inf.br/nfe}vol"
    qvol = "{http://www.portalfiscal.inf.br/nfe}qVol"
    peso_bruto = "{http://www.portalfiscal.inf.br/nfe}pesoB"
    icms_total = "{http://www.portalfiscal.inf.br/nfe}ICMSTot"
    total = "{http://www.portalfiscal.inf.br/nfe}total"
    valor_nf = "{http://www.portalfiscal.inf.br/nfe}vNF"
    lista = {
        'emitente': xml_emitente(
            doc,
            f"{nfe}/{infnfe}/{emit}/{xnome}",
        ),
        'endereco_emi': xml_endereco_emi(
            doc,
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{xlgr}",
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{nro}",
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{xcpl}",
        ),
        'bairro_emi': xml_bairro_emi(
            doc,
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{xbairro}",
        ),
        'cep_emi': xml_cep_emi(
            doc,
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{xcep}",
        ),
        'cidade_emi': xml_cidade_emi(
            doc,
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{xmun}",
        ),
        'estado_emi': xml_estado_emi(
            doc,
            f"{nfe}/{infnfe}/{emit}/{ender_emit}/{estado}",
        ),
        'data_nf': xml_data_nf(
            doc,
            f"{nfe}/{infnfe}/{ide}/{dhemi}",
        ),
        'serie_nf': xml_serie_nf(
            doc,
            f"{nfe}/{infnfe}/{ide}/{serie}",
        ),
        'numero_nf': xml_numero_nf(
            doc,
            f"{nfe}/{infnfe}/{ide}/{nnf}",
        ),
        'cnpj': xml_cnpj(
            doc,
            f"{nfe}/{infnfe}/{dest}/{xcnpj}",
        ),
        'destinatario': xml_destinatario(
            doc,
            f"{nfe}/{infnfe}/{dest}/{xnome}",
        ),
        'endereco': xml_endereco(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{xlgr}",
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{nro}",
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{xcpl}",
        ),
        'bairro': xml_bairro(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{xbairro}",
        ),
        'cep': xml_cep(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{xcep}",
        ),
        'cidade': xml_cidade(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{xmun}",
        ),
        'estado': xml_estado(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{estado}",
        ),
        'telefone': xml_telefone(
            doc,
            f"{nfe}/{infnfe}/{dest}/{ender_dest}/{telefone}",
        ),
        'informa': xml_informa(
            doc,
            f"{nfe}/{infnfe}/{inf_adic}/{inf_cpl}",
        ),
        'volume': xml_volume(
            doc,
            f"{nfe}/{infnfe}/{transp}/{vol}/{qvol}",
        ),
        'peso': xml_peso(
            doc,
            f"{nfe}/{infnfe}/{transp}/{vol}/{peso_bruto}",
        ),
        'valor': xml_valor(
            doc,
            f"{nfe}/{infnfe}/{total}/{icms_total}/{valor_nf}",
        ),
    }
    return lista


def xml_emitente(doc, caminho_emitente):
    nodefind = doc.find(caminho_emitente)
    if nodefind is not None:
        emitente = nodefind.text
    else:
        emitente = ""
    return emitente


def xml_endereco_emi(doc, caminho_endereco_emi, caminho_numero_emi, caminho_complemento_emi):
    nodefind = doc.find(caminho_endereco_emi)
    if nodefind is not None:
        endereco_emi = nodefind.text
    else:
        endereco_emi = ""
    nodefind = doc.find(caminho_numero_emi)
    if nodefind is not None:
        numero_emi = nodefind.text
    else:
        numero_emi = ""
    nodefind = doc.find(caminho_complemento_emi)
    if nodefind is not None:
        complemento_emi = nodefind.text
        endereco_emi = f"{endereco_emi}, {numero_emi}{complemento_emi}"
    else:
        endereco_emi = f"{endereco_emi}, {numero_emi}"
    return endereco_emi


def xml_bairro_emi(doc, caminho_bairro_emi):
    nodefind = doc.find(caminho_bairro_emi)
    if nodefind is not None:
        bairro_emi = nodefind.text
    else:
        bairro_emi = ""
    return bairro_emi


def xml_cep_emi(doc, caminho_cep_emi):
    nodefind = doc.find(caminho_cep_emi)
    if nodefind is not None:
        cep_emi = nodefind.text
    else:
        cep_emi = ""
    return cep_emi


def xml_cidade_emi(doc, caminho_cidade_emi):
    nodefind = doc.find(caminho_cidade_emi)
    if nodefind is not None:
        cidade_emi = nodefind.text
    else:
        cidade_emi = ""
    return cidade_emi


def xml_estado_emi(doc, caminho_estado_emi):
    nodefind = doc.find(caminho_estado_emi)
    if nodefind is not None:
        estado_emi = nodefind.text
    else:
        estado_emi = ""
    return estado_emi


def xml_data_nf(doc, caminho_dhemi):
    nodefind = doc.find(caminho_dhemi)
    if nodefind is not None:
        data_nf = datetime.datetime.strptime(
            nodefind.text[0:10], "%Y-%m-%d").date()
    else:
        data_nf = ""
    return data_nf


def xml_serie_nf(doc, caminho_serie):
    nodefind = doc.find(caminho_serie)
    if nodefind is not None:
        serie_nf = nodefind.text
    else:
        serie_nf = ""
    return serie_nf


def xml_numero_nf(doc, caminho_numero_nf):
    nodefind = doc.find(caminho_numero_nf)
    if nodefind is not None:
        numero_nf = nodefind.text
    else:
        numero_nf = ""
    return numero_nf


def xml_cnpj(doc, caminho_cnpj):
    nodefind = doc.find(caminho_cnpj)
    if nodefind is not None:
        cnpj = nodefind.text
    else:
        cnpj = ""
    return cnpj


def xml_destinatario(doc, caminho_destinatario):
    nodefind = doc.find(caminho_destinatario)
    if nodefind is not None:
        destinatario = nodefind.text
    else:
        destinatario = ""
    return destinatario


def xml_endereco(doc, caminho_endereco, caminho_numero, caminho_complemento):
    nodefind = doc.find(caminho_endereco)
    if nodefind is not None:
        endereco = nodefind.text
    else:
        endereco = ""
    nodefind = doc.find(caminho_numero)
    if nodefind is not None:
        numero = nodefind.text
    else:
        numero = ""
    nodefind = doc.find(caminho_complemento)
    if nodefind is not None:
        complemento = nodefind.text
        endereco = f"{endereco}, {numero}{complemento}"
    else:
        endereco = f"{endereco}, {numero}"
    return endereco


def xml_bairro(doc, caminho_bairro):
    nodefind = doc.find(caminho_bairro)
    if nodefind is not None:
        bairro = nodefind.text
    else:
        bairro = ""
    return bairro


def xml_cep(doc, caminho_cep):
    nodefind = doc.find(caminho_cep)
    if nodefind is not None:
        cep = nodefind.text
    else:
        cep = ""
    return cep


def xml_cidade(doc, caminho_cidade):
    nodefind = doc.find(caminho_cidade)
    if nodefind is not None:
        cidade = nodefind.text
    else:
        cidade = ""
    return cidade


def xml_estado(doc, caminho_estado):
    nodefind = doc.find(caminho_estado)
    if nodefind is not None:
        estado = nodefind.text
    else:
        estado = ""
    return estado


def xml_telefone(doc, caminho_telefone):
    nodefind = doc.find(caminho_telefone)
    if nodefind is not None:
        telefone = nodefind.text
    else:
        telefone = ""
    return telefone


def xml_informa(doc, caminho_info):
    nodefind = doc.find(caminho_info)
    if nodefind is not None:
        informa = nodefind.text
    else:
        informa = ""
    return informa


def xml_volume(doc, caminho_volume):
    nodefind = doc.find(caminho_volume)
    if nodefind is not None:
        volume = nodefind.text
    else:
        volume = 0
    return volume


def xml_peso(doc, caminho_peso):
    nodefind = doc.find(caminho_peso)
    if nodefind is not None:
        peso = nodefind.text
    else:
        peso = 0.000
    return peso


def xml_valor(doc, caminho_valor):
    nodefind = doc.find(caminho_valor)
    if nodefind is not None:
        valor = nodefind.text
    else:
        valor = 0.00
    return valor


def create_contexto_imprime_romaneio(idromaneio, idcliente):
    romaneio = Romaneios.objects.get(idRomaneio=idromaneio)
    cliente = Cliente.objects.get(idCliente=idcliente)
    notas = RomaneioNotas.objects.filter(idRomaneio=idromaneio)
    notas_romaneio = create_contexto_notas_romaneio(idromaneio)
    (
        quantidade_entregas,
        quantidade_falta,
    ) = create_contexto_quantidade_entregas(notas_romaneio)
    return {
        "romaneio": romaneio,
        "cliente": cliente,
        "notas": notas,
        "quantidade_entregas": quantidade_entregas,
        "quantidade_falta": quantidade_falta,
    }


def create_contexto_filtro_nota(nota, idcliente):
    notas = NotasClientes.objects.filter(NumeroNota=nota, idCliente=idcliente)
    lista = create_lista_notas_clientes(notas)
    return lista


def create_contexto_filtro_emitente(emitente, idcliente):
    notas = NotasClientes.objects.filter(Emitente=emitente, idCliente=idcliente)
    lista = create_lista_notas_clientes(notas)
    return lista


def create_contexto_filtro_destinatario(destinatario, idcliente):
    notas = NotasClientes.objects.filter(Destinatario=destinatario, idCliente=idcliente)
    lista = create_lista_notas_clientes(notas)
    return lista


def fecha_romaneio_cliente(idromaneio):
    romaneio = Romaneios.objects.get(idRomaneio=idromaneio)
    obj = romaneio
    obj.Fechado = True
    obj.save(update_fields=["Fechado"])


def reabre_romaneio_cliente(idromaneio):
    romaneio = Romaneios.objects.get(idRomaneio=idromaneio)
    obj = romaneio
    obj.Fechado = False
    obj.save(update_fields=["Fechado"])


def last_chat_id_telegram(token):
    try:
        url = f"https://api.telegram.org/bot{token}/getUpdates"
        response = requests.get(url)
        if response.status_code == 200:
            json_msg = response.json()
            for json_result in reversed(json_msg["result"]):
                message_keys = json_result["message"].keys()
                if ("new_chat_member") in message_keys or (
                    "group_chat_created" in message_keys
                ):
                    return json_result["message"]["chat"]["id"]
            print("Nenhum grupo encontrado")
        else:
            print(f"A resposta falhou, código de status {response.status_code}")
    except Exception as e:
        print("Erro no getUpdates:", e)


# enviar mensagens utilizando o bot para um gruppo específico
def send_message(message, idcliente):
    token = "5778267083:AAEha8jgzCRYr_niZ7JM4EB5MWDX2Zkk98o"
    if idcliente == "11":
        chat_id = "-666092318"  # Telegram Transefetiva - LogCatavento
    elif idcliente == "7":
        chat_id = "-994748069"  # Telegram Transefetiva - Kite
    else:
        chat_id = "-785462150"  # Telegram TransEfetiva - Operacional
    try:
        data = {"chat_id": chat_id, "text": message}
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        requests.post(url, data)
    except Exception as e:
        print("Erro no sendMessage:", e)


def send_arquivo(romaneio, idcliente):
    token = "5778267083:AAEha8jgzCRYr_niZ7JM4EB5MWDX2Zkk98o"
    if idcliente == "11":
        chat_id = "-666092318"  # Telegram Transefetiva - LogCatavento
    elif idcliente == "7":
        chat_id = "-994748069"  # Telegram Transefetiva - Kite
    else:
        chat_id = "-785462150"  # Telegram TransEfetiva - Operacional
    rom_numero = str(romaneio).zfill(5)
    descricao_arquivo = f"Romaneio_{str(rom_numero).zfill(5)}.pdf"
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    url = f"https://api.telegram.org/bot{token}/sendDocument?chat_id={chat_id}"
    payload = {}
    file = os.path.join(arquivo[0].uploadFile.path)
    if arquivo:
        files = [("document", open(file, "rb"))]
    headers = []
    requests.request("POST", url, headers=headers, data=payload, files=files)


def send_arquivo_relatorio(sort_status, idcliente):
    token = "5778267083:AAEha8jgzCRYr_niZ7JM4EB5MWDX2Zkk98o"
    if idcliente == "11":
        chat_id = "-666092318"  # Telegram Transefetiva - LogCatavento
    elif idcliente == "7":
        chat_id = "-994748069"  # Telegram Transefetiva - Kite
    else:
        chat_id = "-785462150"  # Telegram TransEfetiva - Operacional
    descricao_arquivo = f"Notas {sort_status}.pdf"
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    url = f"https://api.telegram.org/bot{token}/sendDocument?chat_id={chat_id}"
    payload = {}
    file = os.path.join(arquivo[0].uploadFile.path)
    if arquivo:
        files = [("document", open(file, "rb"))]
    headers = []
    requests.request("POST", url, headers=headers, data=payload, files=files)


def create_data_send_arquivo():
    data = dict()
    data["send_arquivo"] = "OK"
    data = JsonResponse(data)
    return data


def create_contexto_pdf_romaneio(rom):
    descricao_arquivo = f"Romaneio_{str(rom).zfill(5)}.pdf"
    arquivo = FileUpload.objects.filter(DescricaoUpload=descricao_arquivo)
    if arquivo:
        if arquivo[0].uploadFile:
            return True
        else:
            return False
    else:
        return False


def altera_status_pendente(id_not):
    nota = NotasClientes.objects.get(idNotasClientes=id_not)
    obj = nota
    obj.StatusNota = "PENDENTE"
    obj.save(update_fields=["StatusNota"])


def create_contexto_peso_romaneio(notas_romaneio):
    peso = Decimal(0.000)
    for x in notas_romaneio:
        peso += x['idnotasclientes'].Peso
    return {"peso": peso}


def create_contexto_quantidade_entregas(notas_romaneio):
    entregas = []
    falta_entregar = []
    for x in notas_romaneio:
        if x["idnotasclientes"].LocalColeta == "DESTINATÁRIO":
            entregas.append(
                f"{x['idnotasclientes'].Endereco_emi} - {x['idnotasclientes'].Bairro_emi}"
            )
        else:
            entregas.append(
                f"{x['idnotasclientes'].Endereco} - {x['idnotasclientes'].Bairro}"
            )
        if x["idnotasclientes"].StatusNota == "EM ROTA":
            if x["idnotasclientes"].LocalColeta == "DESTINATÁRIO":
                falta_entregar.append(
                    f"{x['idnotasclientes'].Endereco_emi} - {x['idnotasclientes'].Bairro_emi}"
                )
            else:
                falta_entregar.append(
                    f"{x['idnotasclientes'].Endereco} - {x['idnotasclientes'].Bairro}"
                )
    entregas = len(list(set(entregas)))
    falta_entregar = len(list(set(falta_entregar)))
    return entregas, falta_entregar


def create_lista_notas_clientes(notas):
    lista = []
    for x in notas:
        if x.CEP_emi:
            cep_emitente = f"{x.CEP_emi[0:5]}-{x.CEP_emi[5:]}"
        else:
            cep_emitente = "00000-000"
        if x.CEP:
            cep_destinatario = f"{x.CEP[0:5]}-{x.CEP[5:]}"
        else:
            cep_destinatario = "00000-000"
        lista.append(
            {
                "emitente": x.Emitente,
                "emitente_curto": nome_curto(x.Emitente),
                "endereco_emi": x.Endereco_emi,
                "endereco_compl_emi": (
                    f"{x.Endereco_emi} {x.Bairro_emi} {cep_emitente} {x.Cidade_emi} {x.Estado_emi}"
                ),
                "bairro_emi": x.Bairro_emi,
                "cep_emi": cep_emitente,
                "cidade_emi": x.Cidade_emi,
                "estado_emi": x.Estado_emi,
                "id_nota_clientes": x.idNotasClientes,
                "local_coleta": x.LocalColeta,
                "data_nota": x.DataColeta,
                "serie_nota": x.SerieNota,
                "numero_nota": x.NumeroNota,
                "destinatario": x.Destinatario,
                "destinatario_curto": nome_curto(x.Destinatario),
                "cnpj": x.CNPJ,
                "endereco": x.Endereco,
                "endereco_compl": (
                    f"{x.Endereco} {x.Bairro} {cep_destinatario} {x.Cidade} {x.Estado}"
                ),
                "bairro": x.Bairro,
                "cep": cep_destinatario,
                "cidade": x.Cidade,
                "estado": x.Estado,
                "contato": x.Contato,
                "informa": x.Informa,
                "volume": x.Volume,
                "peso": x.Peso,
                "valor": x.Valor,
                "statusnota": x.StatusNota,
                "historico": x.Historico,
                "idcliente": x.idCliente_id,
            }
        )
    return lista


def create_contexto_peso_total_notas(notas):
    peso_total = 0
    for x in notas:
        peso_total += x.Peso
    return peso_total


def create_contexto_notas(idcliente, filter_status, order_nota):
    cliente = Cliente.objects.get(idCliente=idcliente)
    notas = NotasClientes.objects.filter(
        StatusNota=filter_status, idCliente_id=idcliente
    ).order_by(order_nota)
    lista = []
    for x in notas:
        ocorrencia = None
        if x.StatusNota == "RECUSADA":
            ocorrencia = NotasOcorrencias.objects.filter(
                idNotasClientes=x.idNotasClientes, TipoOcorrencia="RECUSADA"
            )
            lista_ocorrencia = []
            for y in ocorrencia:
                data_ocorrencia = y.DataOcorrencia
                desc_ocorrencia = y.Ocorrencia
                lista_ocorrencia.append(
                    {
                        "ocorrencia": desc_ocorrencia,
                        "data_ocorrencia": data_ocorrencia,
                    }
                )
        placa_motorista = []
        romaneio_idromaneio = None
        romaneio_numero = None
        romaneio_data = None
        romaneio = None
        if x.StatusNota != "PENDENTE" or x.StatusNota != "NOTA CADASTRADA":
            romaneio = RomaneioNotas.objects.filter(
                idNotasClientes=x.idNotasClientes
            )
            if romaneio:
                romaneio.latest("idRomaneio")
                placa = romaneio[0].idRomaneio.idVeiculo.Placa
                motorista = nome_curto(romaneio[0].idRomaneio.idMotorista.Nome)
                placa_motorista.append({"motorista": motorista, "placa": placa})
        if x.CEP_emi:
            cep_emitente = f"{x.CEP_emi[0:5]}-{x.CEP_emi[5:]}"
        else:
            cep_emitente = None
        if x.CEP:
            cep_destinatario = f"{x.CEP[0:5]}-{x.CEP[5:]}"
        else:
            cep_destinatario = None
        lista.append(
            {
                "id_nota_clientes": x.idNotasClientes,
                "local_coleta": x.LocalColeta,
                "emitente": x.Emitente,
                "emitente_curto": nome_curto(x.Emitente),
                "endereco_emi": x.Endereco_emi,
                "endereco_compl_emi": (
                    f"{x.Endereco_emi} {x.Bairro_emi} {cep_emitente} {x.Cidade_emi} {x.Estado_emi}"
                ),
                "bairro_emi": x.Bairro_emi,
                "cep_emi": cep_emitente,
                "cidade_emi": x.Cidade_emi,
                "estado_emi": x.Estado_emi,
                "data_nota": x.DataColeta,
                "serie_nota": x.SerieNota,
                "numero_nota": x.NumeroNota,
                "destinatario": x.Destinatario,
                "destinatario_curto": nome_curto(x.Destinatario),
                "cnpj": x.CNPJ,
                "endereco": x.Endereco,
                "endereco_compl": (
                    f"{x.Endereco} {x.Bairro} {cep_destinatario} {x.Cidade} {x.Estado}"
                ),
                "bairro": x.Bairro,
                "cep": cep_destinatario,
                "cidade": x.Cidade,
                "estado": x.Estado,
                "contato": x.Contato,
                "informa": x.Informa,
                "volume": x.Volume,
                "peso": x.Peso,
                "valor": x.Valor,
                "statusnota": x.StatusNota,
                "historico": x.Historico,
                "idcliente": x.idCliente_id,
                "ocorrencia": ocorrencia,
                "placa_motorista": placa_motorista,
                "romaneio": romaneio,
            }
        )
    peso_total = create_contexto_peso_total_notas(notas)
    return {"notas": lista, "cliente": cliente, "sort_status": filter_status, "peso_total": peso_total}
