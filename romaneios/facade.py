import datetime
import xml.etree.ElementTree as ET
from cgitb import html
from decimal import Decimal
from xml.dom import ValidationErr

from clientes.models import Cliente
from django.db.models import Max
from django.http import JsonResponse
from django.template.loader import render_to_string
from minutas.facade import nome_curto

from romaneios.models import NotasClientes, NotasOcorrencias, RomaneioNotas, Romaneios


def create_contexto_seleciona_cliente():
    clientes = Cliente.objects.all()
    lista = [{"idcliente": x.idCliente, "fantasia": x.Fantasia} for x in clientes]
    return lista


def create_contexto_seleciona_notas(id_cli, sort_nota):
    notas = (
        NotasClientes.objects.filter(idCliente=id_cli)
        .order_by(sort_nota)
        .exclude(StatusNota__startswith="ENTREGUE")
        .exclude(StatusNota="COLETA CANCELADA")
        .exclude(StatusNota="DEVOLVIDA NO CLIENTE")
    )
    lista = [
        {
            "id_nota_clientes": x.idNotasClientes,
            "local_coleta": x.LocalColeta,
            "data_coleta": x.DataColeta,
            "numero_nota": x.NumeroNota,
            "destinatario": x.Destinatario,
            "endereco": x.Endereco,
            "endereco_compl": x.Endereco
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
            "bairro": x.Bairro,
            "cep": x.CEP[0:5] + "-" + x.CEP[5:],
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
    return JsonResponse(data)


def create_data_sort_notas(request, contexto):
    data = dict()
    html_lista_notas_cliente(request, contexto, data)
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


def html_form_romaneios(request, contexto, data):
    data["html_form_romaneios"] = render_to_string(
        "romaneios/html_form_romaneios.html", contexto, request=request
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
    obj.save()


def update_romaneio(romaneio_form, id_rom):
    romaneio = Romaneios.objects.get(idRomaneio=id_rom)
    obj = romaneio
    obj.DataRomaneio = romaneio_form["data_romaneio"]
    obj.idMotorista_id = romaneio_form["motorista"]
    obj.idVeiculo_id = romaneio_form["veiculo"]
    obj.save()


def create_contexto_romaneios():
    romaneios = Romaneios.objects.all()
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


def create_contexto_notas_romaneio(id_rom):
    notas_romaneio = RomaneioNotas.objects.filter(idRomaneio=id_rom)
    lista = [
        {
            "idromaneionotas": x.idRomaneioNotas,
            "idnotasclientes": x.idNotasClientes,
        }
        for x in notas_romaneio
    ]
    return lista


def create_data_lista_notas_romaneio(request, contexto):
    data = dict()
    html_lista_notas_romaneio(request, contexto, data)
    return JsonResponse(data)


def html_lista_notas_romaneio(request, contexto, data):
    data["html_lista_notas_romaneio"] = render_to_string(
        "romaneios/html_lista_notas_romaneio.html", contexto, request=request
    )
    return data


def create_contexto_seleciona_romaneio(id_rom):
    romaneio = Romaneios.objects.filter(idRomaneio=id_rom)
    lista = [
        {
            "idromaneio": x.idRomaneio,
            "romaneio": x.Romaneio,
            "data_romaneio": x.DataRomaneio,
            "motorista": x.idMotorista,
            "veiculo": x.idVeiculo,
        }
        for x in romaneio
    ]
    if lista:
        for index, itens in enumerate(lista):
            if lista[index]["motorista"]:
                lista[index]["apelido"] = nome_curto(lista[index]["motorista"].Nome)
    return lista


def lista_destinatarios():
    destinatarios = (
        NotasClientes.objects.values("Destinatario").distinct().order_by("Destinatario")
    )
    lista = []
    for x in destinatarios:
        lista.append(x["Destinatario"])
    return lista


def lista_enderecos():
    destinatarios = (
        NotasClientes.objects.values("Endereco").distinct().order_by("Endereco")
    )
    lista = []
    for x in destinatarios:
        lista.append(x["Endereco"])
    return lista


def lista_bairros():
    destinatarios = NotasClientes.objects.values("Bairro").distinct().order_by("Bairro")
    lista = []
    for x in destinatarios:
        lista.append(x["Bairro"])
    return lista


def save_nota_romaneio(id_nota, id_romaneio):
    obj = RomaneioNotas()
    obj.idNotasClientes_id = id_nota
    obj.idRomaneio_id = id_romaneio
    obj.save()


def ler_nota_xml(nota):
    tree = ET.parse(nota)
    doc = tree.getroot()
    NFe = "{http://www.portalfiscal.inf.br/nfe}NFe"
    infNFe = "{http://www.portalfiscal.inf.br/nfe}infNFe"
    ide = "{http://www.portalfiscal.inf.br/nfe}ide"
    nNF = "{http://www.portalfiscal.inf.br/nfe}nNF"
    dest = "{http://www.portalfiscal.inf.br/nfe}dest"
    xNome = "{http://www.portalfiscal.inf.br/nfe}xNome"
    enderDest = "{http://www.portalfiscal.inf.br/nfe}enderDest"
    xLgr = "{http://www.portalfiscal.inf.br/nfe}xLgr"
    nro = "{http://www.portalfiscal.inf.br/nfe}nro"
    xCpl = "{http://www.portalfiscal.inf.br/nfe}xCpl"
    xBairro = "{http://www.portalfiscal.inf.br/nfe}xBairro"
    xCEP = "{http://www.portalfiscal.inf.br/nfe}CEP"
    xMun = "{http://www.portalfiscal.inf.br/nfe}xMun"
    uf = "{http://www.portalfiscal.inf.br/nfe}UF"
    telefone = "{http://www.portalfiscal.inf.br/nfe}Telefone"
    infAdic = "{http://www.portalfiscal.inf.br/nfe}infAdic"
    infCpl = "{http://www.portalfiscal.inf.br/nfe}infCpl"
    transp = "{http://www.portalfiscal.inf.br/nfe}transp"
    vol = "{http://www.portalfiscal.inf.br/nfe}vol"
    qVol = "{http://www.portalfiscal.inf.br/nfe}qVol"
    pesoB = "{http://www.portalfiscal.inf.br/nfe}pesoB"
    ICMSTot = "{http://www.portalfiscal.inf.br/nfe}ICMSTot"
    total = "{http://www.portalfiscal.inf.br/nfe}total"
    vNF = "{http://www.portalfiscal.inf.br/nfe}vNF"
    caminho_numero_nf = f"{NFe}/{infNFe}/{ide}/{nNF}"
    nodefind = doc.find(caminho_numero_nf)
    if not nodefind is None:
        numero_nf = nodefind.text
    else:
        numero_nf = ""
    caminho_destinatario = f"{NFe}/{infNFe}/{dest}/{xNome}"
    nodefind = doc.find(caminho_destinatario)
    if not nodefind is None:
        destinatario = nodefind.text
    else:
        destinatario = ""
    caminho_endereco = f"{NFe}/{infNFe}/{dest}/{enderDest}/{xLgr}"
    nodefind = doc.find(caminho_endereco)
    if not nodefind is None:
        endereco = nodefind.text
    else:
        endereco = ""
    caminho_numero = f"{NFe}/{infNFe}/{dest}/{enderDest}/{nro}"
    nodefind = doc.find(caminho_numero)
    if not nodefind is None:
        numero = nodefind.text
    else:
        numero = ""
    caminho_complemento = f"{NFe}/{infNFe}/{dest}/{enderDest}/{xCpl}"
    nodefind = doc.find(caminho_complemento)
    if not nodefind is None:
        complemento = nodefind.text
        endereco = f"{endereco}, {numero}{complemento}"
    else:
        endereco = f"{endereco}, {numero}"
    caminho_bairro = f"{NFe}/{infNFe}/{dest}/{enderDest}/{xBairro}"
    nodefind = doc.find(caminho_bairro)
    if not nodefind is None:
        bairro = nodefind.text
    else:
        bairro = ""
    caminho_CEP = f"{NFe}/{infNFe}/{dest}/{enderDest}/{xCEP}"
    nodefind = doc.find(caminho_CEP)
    if not nodefind is None:
        cep = nodefind.text
    else:
        cep = ""
    caminho_cidade = f"{NFe}/{infNFe}/{dest}/{enderDest}/{xMun}"
    nodefind = doc.find(caminho_cidade)
    if not nodefind is None:
        cidade = nodefind.text
    else:
        cidade = ""
    caminho_estado = f"{NFe}/{infNFe}/{dest}/{enderDest}/{uf}"
    nodefind = doc.find(caminho_estado)
    if not nodefind is None:
        estado = nodefind.text
    else:
        estado = ""
    caminho_telefone = f"{NFe}/{infNFe}/{dest}/{enderDest}/{telefone}"
    nodefind = doc.find(caminho_telefone)
    if not nodefind is None:
        telefone = nodefind.text
    else:
        telefone = ""
    caminho_info = f"{NFe}/{infNFe}/{infAdic}/{infCpl}"
    nodefind = doc.find(caminho_info)
    if not nodefind is None:
        informa = nodefind.text
    else:
        informa = ""
    caminho_volume = f"{NFe}/{infNFe}/{transp}/{vol}/{qVol}"
    nodefind = doc.find(caminho_volume)
    if not nodefind is None:
        volume = nodefind.text
    else:
        volume = 0
    caminho_peso = f"{NFe}/{infNFe}/{transp}/{vol}/{pesoB}"
    nodefind = doc.find(caminho_peso)
    if not nodefind is None:
        peso = nodefind.text
    else:
        peso = 0.000
    caminho_valor = f"{NFe}/{infNFe}/{total}/{ICMSTot}/{vNF}"
    nodefind = doc.find(caminho_valor)
    if not nodefind is None:
        valor = nodefind.text
    else:
        valor = 0.00
    lista = {
        "numero_nf": numero_nf,
        "destinatario": destinatario,
        "endereco": endereco,
        "bairro": bairro,
        "cep": cep,
        "cidade": cidade,
        "estado": estado,
        "telefone": telefone,
        "informa": informa,
        "volume": volume,
        "peso": peso,
        "valor": valor,
    }
    return JsonResponse(lista)
