import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.template.loader import render_to_string
from minutas.facade import nome_curto
from minutas.models import Minuta, MinutaColaboradores
from pagamentos.facade import create_vales
from pessoas.models import Pessoal, Vales
from veiculos.models import Veiculo

from despesas.models import Abastecimento, Categorias, Despesas, Multas, SubCategorias


def create_despesas_context():
    abastecimento = get_abastecimento_all()
    veiculos = Veiculo.objects.filter(Proprietario_id=17)
    multas = multas_pagar("SEM FILTRO", "")
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    motoristas = Pessoal.objects.all().exclude(Categoria="AJUDANTE")
    lista_motoristas = [
        {"idpessoal": i.idPessoal, "nome": nome_curto(i.Nome)} for i in motoristas
    ]
    veiculos = Veiculo.objects.filter(Proprietario_id=17)
    lista_veiculos = [{"idveiculo": i.idVeiculo, "placa": i.Placa} for i in veiculos]
    context = {
        "abastecimento": abastecimento,
        "veiculos": veiculos,
        "hoje": hoje,
        "multas": multas,
        "motoristas": lista_motoristas,
        "veiculos": lista_veiculos,
    }
    return context


def create_contexto_filtro_motorista(idpessoal):
    multas = multas_pagar("MOTORISTA", idpessoal)
    return {"multas": multas}


def create_contexto_filtro_veiculo(idveiculo):
    multas = multas_pagar("VEICULO", idveiculo)
    return {"multas": multas}


def create_contexto_filtro_dia_multa(dia_multa):
    multas = multas_pagar("DIA MULTA", dia_multa)
    return {"multas": multas}


def create_contexto_filtro_penalidade(penalidade):
    multas = multas_pagar("PENALIDADE", penalidade)
    return {"multas": multas}


def create_contexto_multas_pagar():
    multas = multas_pagar("SEM FILTRO", "")
    return {"multas": multas}


def get_abastecimento_all():
    return Abastecimento.objects.all()


def form_despesa(request, c_form, c_idobj, c_url, c_view):
    data = dict()
    c_instance = None
    form = c_form(instance=c_instance)
    contexto = {"form": form, "c_idobj": c_idobj, "c_url": c_url, "c_view": c_view}
    data["html_html"] = render_to_string(
        "despesas/formdespesa.html", contexto, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def valida_multa(request):
    msg = dict()
    error = False
    # Valida Número AIT
    _ait = request.POST.get("ait")
    if not _ait:
        msg["erro_ait"] = "Obrigatório o número AIT."
        error = True
    # Valida Número DOC
    _doc = request.POST.get("doc")
    if not _doc:
        msg["erro_doc"] = "Obrigatório o número da penalidade."
        error = True
    # Valida Data da infração
    _data = datetime.datetime.strptime(request.POST.get("data"), "%Y-%m-%d").date()
    _hoje = datetime.datetime.today().date()
    if _data >= _hoje:
        msg["erro_data"] = "Data da infração tem que ser anterior a hoje."
        error = True
    # Valida infração
    _infracao = request.POST.get("infracao")
    if not _infracao:
        msg["erro_infracao"] = "Obrigatório o tipo de infração."
        error = True
    # Valida local da infração
    _local = request.POST.get("local")
    if not _local:
        msg["erro_local"] = "Obrigatório o local da infração."
        error = True
    # Valida valor da infração
    _valor = request.POST.get("valor")
    if Decimal(_valor) < Decimal("0.01"):
        msg["erro_valor"] = "Obrigatório o valor da multa."
        error = True
    # Valida vencimento da infração
    _vencimento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    if _vencimento == _data:
        msg[
            "erro_vencimento"
        ] = "A data de vencimento não pode ser a mesma da infração."
        error = True
    if _vencimento < _data:
        msg[
            "erro_vencimento"
        ] = "A data de vencimento não pode ser anterior a data da infração."
        error = True
    # Valida veículo da infração
    _veiculo = request.POST.get("veiculo")
    if int(_veiculo) == 0:
        msg["erro_veiculo"] = "Obrigatório selecionar um veículo."
        error = True
    # Valida quem paga a infração
    _desconta = request.POST.get("desconta")
    if not _desconta:
        msg["erro_desconta"] = "Obrigatório selecionar quem paga a multa."
        error = True
    # TODO Linha Digitavel Boleto
    _linha = None
    # # valida linha LinhaDigitavel
    # _linha = f'{request.POST.get("linha1")}{request.POST.get("linha2")}'
    # _linha = _linha.replace(".", "")
    # _linha = _linha.replace(" ", "")
    # if not len(_linha) == 47:
    #     msg["erro_linha"] = "A quantidade de digitos tem que ser igual a 47."
    #     error = True
    # valida linha LinhaDigitavel SP
    _linha_sp = f'{request.POST.get("linhasp1")}{request.POST.get("linhasp2")}'
    _linha_sp = _linha_sp.replace(".", "")
    _linha_sp = _linha_sp.replace(" ", "")
    if not len(_linha_sp) == 48:
        msg["erro_linha_sp"] = "A quantidade de digitos tem que ser igual a 48."
        error = True
    return error, msg


def save_multa(multa, idmulta):
    idvale = None
    idpessoal = None
    idcliente = None
    veiculo = Veiculo.objects.get(idVeiculo=multa["idveiculo"])
    minuta = busca_minutas_multa(multa["data_multa"])
    minuta_filtro = list(filter(lambda x: x["placa"] == veiculo.Placa, minuta))
    numero_doc = multa["numero_doc"]
    valor = multa["valor_multa"]
    if minuta_filtro:
        idpessoal = minuta_filtro[0]["idpessoal"]
        idcliente = minuta_filtro[0]["idcliente"]
        if multa["desconta_motorista"] == "True":
            idvale = busca_vale_multa(numero_doc)
            if not idvale:
                vale_salva = create_vale_multa(numero_doc, valor, idpessoal)
                idvale = vale_salva.idVales
    if not idmulta:
        obj = Multas()
    else:
        multa_selecionada = Multas.objects.get(idMulta=idmulta)
        obj = Multas(multa_selecionada)
        obj.idMulta = multa_selecionada.idMulta
    obj.NumeroAIT = multa["numero_ait"]
    obj.NumeroDOC = multa["numero_doc"]
    obj.DataMulta = datetime.datetime.strptime(multa["data_multa"], "%Y-%m-%d").date()
    obj.HoraMulta = datetime.datetime.strptime(multa["hora_multa"], "%H:%M").time()
    obj.ValorMulta = multa["valor_multa"]
    obj.Vencimento = datetime.datetime.strptime(multa["vencimento"], "%Y-%m-%d").date()
    obj.Infracao = multa["infracao"]
    obj.Local = multa["local"]
    obj.DescontaMotorista = multa["desconta_motorista"]
    obj.idVeiculo_id = multa["idveiculo"]
    obj.LinhaDigitavel = multa["linha_digitavel"]
    obj.LinhaDigitavelSP = multa["linha_digitavel_sp"]
    obj.DataPagamento = datetime.datetime.strptime(
        multa["vencimento"], "%Y-%m-%d"
    ).date()
    obj.idPessoal_id = idpessoal
    obj.idVales_id = idvale
    obj.idCliente_id = idcliente
    obj.save()


def busca_vale_multa(_des):
    try:
        vale = Vales.objects.filter(Descricao__startswith=f"MULTA - {_des}").get()
        return vale.idVales
    except Vales.DoesNotExist:
        return False


def read_multa_post(request):
    multa_post = dict()
    multa_post["idmulta"] = request.POST.get("idMulta")
    multa_post["numero_doc"] = request.POST.get("doc")
    multa_post["numero_ait"] = request.POST.get("ait")
    multa_post["data_multa"] = request.POST.get("data")
    multa_post["hora_multa"] = request.POST.get("hora")
    multa_post["valor_multa"] = request.POST.get("valor")
    multa_post["vencimento"] = request.POST.get("vencimento")
    multa_post["infracao"] = request.POST.get("infracao")
    multa_post["local"] = request.POST.get("local")
    multa_post["desconta_motorista"] = request.POST.get("desconta")
    multa_post["idveiculo"] = int(request.POST.get("veiculo"))
    multa_post["linha_digitavel"] = None
    _linha_sp = f'{request.POST.get("linhasp1")}{request.POST.get("linhasp2")}'
    _linha_sp = _linha_sp.replace(".", "")
    _linha_sp = _linha_sp.replace(" ", "")
    multa_post["linha_digitavel_sp"] = _linha_sp
    multa_post["idpessoal"] = request.POST.get("idpessoal")
    return multa_post


def read_multa_database(_id_mul):
    multa = Multas.objects.get(idMulta=_id_mul)
    multa_database = dict()
    multa_database["idmulta"] = multa.idMulta
    multa_database["numero_doc"] = multa.NumeroDOC
    multa_database["numero_ait"] = multa.NumeroAIT
    multa_database["data_multa"] = datetime.datetime.strftime(
        multa.DataMulta, "%Y-%m-%d"
    )
    multa_database["hora_multa"] = multa.HoraMulta
    multa_database["valor_multa"] = str(multa.ValorMulta)
    multa_database["vencimento"] = datetime.datetime.strftime(
        multa.Vencimento, "%Y-%m-%d"
    )
    multa_database["infracao"] = multa.Infracao
    multa_database["local"] = multa.Local
    multa_database["pago"] = multa.Pago
    multa_database["desconta_motorista"] = multa.DescontaMotorista
    multa_database["data_pagamento"] = multa.DataPagamento
    multa_database["idveiculo"] = multa.idVeiculo_id
    multa_database["linha_digitavel"] = multa.LinhaDigitavel
    multa_database["linha_digitavel_sp"] = multa.LinhaDigitavelSP
    return multa_database


def html_form_multas(request, contexto, data):
    data["html_form_multas"] = render_to_string(
        "despesas/html_form_multas.html", contexto, request=request
    )
    return data


def create_data_form_multa(request, contexto):
    data = dict()
    html_form_multas(request, contexto, data)
    html_multas_pagar(request, contexto, data)
    return JsonResponse(data)


def create_data_edita_multa(request, contexto):
    data = dict()
    html_form_multas(request, contexto, data)
    html_multas_pagar(request, contexto, data)
    html_minutas_multa(request, contexto, data)
    return JsonResponse(data)


def html_multas_pagar(request, contexto, data):
    data["html_multas_pagar"] = render_to_string(
        "despesas/html_multas_pagar.html", contexto, request=request
    )
    return data


def create_data_multas_pagar(request, contexto):
    data = dict()
    html_multas_pagar(request, contexto, data)
    return JsonResponse(data)


def multas_pagar(filtro, valor):
    multas = Multas.objects.filter(Pago=False).order_by("-Vencimento")
    lista = []
    for x in multas:
        multa = f"MULTA - {x.NumeroDOC}"
        try:
            motorista = nome_curto(x.idPessoal.Nome)
        except AttributeError:
            motorista = "NÃO MENCIONADO"
        vale = False
        try:
            vale = Vales.objects.filter(Descricao__startswith=multa).get()
            vale_mensagem = "VALE ENCONTRADO"
        except Vales.DoesNotExist:
            vale_mensagem = "VALE NÃO ENCONTRADO"
        adiciona_lista = False
        if filtro == "SEM FILTRO":
            adiciona_lista = True
        elif filtro == "MOTORISTA":
            if x.idPessoal_id == int(valor):
                adiciona_lista = True
        elif filtro == "VEICULO":
            if x.idVeiculo_id == int(valor):
                adiciona_lista = True
        elif filtro == "DIA MULTA":
            if x.DataMulta == datetime.datetime.strptime(valor, "%Y-%m-%d").date():
                adiciona_lista = True
        elif filtro == "PENALIDADE":
            if x.NumeroDOC == valor:
                adiciona_lista = True
        if adiciona_lista:
            lista.append(
                {
                    "id_multa": x.idMulta,
                    "vencimento": x.Vencimento,
                    "valor": x.ValorMulta,
                    "doc": x.NumeroDOC,
                    "ait": x.NumeroAIT,
                    "data": x.DataMulta,
                    "hora": x.HoraMulta,
                    "placa": x.idVeiculo.Placa,
                    "infracao": x.Infracao,
                    "local": x.Local,
                    "digitavel": x.LinhaDigitavel,
                    "digitavel_sp": x.LinhaDigitavelSP,
                    "desconta": x.DescontaMotorista,
                    "motorista": motorista,
                    "vale": vale,
                    "vale_mensagem": vale_mensagem,
                    "cliente": x.idCliente,
                }
            )
    return lista


def delete_multa(_id_mul):
    multa = Multas.objects.filter(idMulta=_id_mul)
    multa.delete()


def create_vale_multa(_obj, idpessoal):
    if idpessoal:
        descricao = f"Multa - {_obj.NumeroDOC}"
        data = datetime.datetime.today().date()
        valor = _obj.ValorMulta
        parcelas = 1
        return create_vales(descricao, data, valor, parcelas, idpessoal)


def busca_minutas_multa(_date):
    _date = datetime.datetime.strptime(_date, "%Y-%m-%d")
    minutas = Minuta.objects.filter(DataMinuta=_date)
    lista = []
    for x in minutas:
        motorista = MinutaColaboradores.objects.filter(
            idMinuta_id=x.idMinuta, Cargo="MOTORISTA"
        )
        if len(motorista) > 0:
            lista.append(
                {
                    "minuta": x.Minuta,
                    "inicio": x.HoraInicial,
                    "final": x.HoraFinal,
                    "data_minuta": x.DataMinuta,
                    "idcliente": x.idCliente_id,
                    "fantasia": x.idCliente.Fantasia,
                    "motorista": nome_curto(motorista[0].idPessoal.Nome),
                    "idpessoal": motorista[0].idPessoal_id,
                    "demissao": motorista[0].idPessoal.DataDemissao,
                    "admissao": motorista[0].idPessoal.DataAdmissao,
                    "placa": x.idVeiculo.Placa,
                    "idveiculo": x.idVeiculo,
                }
            )
    return lista


def html_minutas_multa(request, contexto, data):
    data["html_minutas_multa"] = render_to_string(
        "despesas/html_minutas_multa.html", contexto, request=request
    )
    return data


def create_data_minutas_multa(request, contexto):
    data = dict()
    html_minutas_multa(request, contexto, data)
    return JsonResponse(data)


def save_despesa(_des):
    obj = Despesas()
    obj.Cedente = _des["cedente"]
    obj.Categoria_id = _des["categoria"]
    obj.SubCategoria_id = _des["subcategoria"]
    obj.Descricao = _des["descricao"]
    obj.Valor = _des["valor"]
    obj.Vencimento = datetime.datetime.strptime(_des["vencimento"], "%Y-%m-%d").date()
    obj.DataPgto = datetime.datetime.strptime("2001-01-01", "%Y-%m-%d").date()
    obj.save()


def valida_despesa(request):
    msg = dict()
    error = False
    # Valida Cedente
    _cedente = request.POST.get("cedente")
    if not _cedente:
        msg["erro_cedente"] = "Obrigatório o nome do cedente."
        error = True
    # Valida Categoria
    _categoria = request.POST.get("categoria")
    if int(_categoria) == 0:
        msg["erro_categoria"] = "Obrigatório selecionar uma categoria."
        error = True
    # Valida SubCategoria
    _subcategoria = request.POST.get("subcategoria")
    if int(_subcategoria) == 0:
        msg["erro_subcategoria"] = "Obrigatório selecionar uma sub-categoria."
        error = True
    # Valida descrição
    _descricao = request.POST.get("descricao")
    if not _descricao:
        msg["erro_descricao"] = "Obrigatório inserir a descrição da despesa."
        error = True
    # Valida valor
    _valor = request.POST.get("valor")
    if Decimal(_valor) < Decimal("0.01"):
        msg["erro_valor"] = "Obrigatório o valor da despesa."
        error = True
    return error, msg


def read_despesa_post(request):
    despesa_post = dict()
    despesa_post["cedente"] = request.POST.get("cedente")
    despesa_post["categoria"] = int(request.POST.get("categoria"))
    despesa_post["subcategoria"] = int(request.POST.get("subcategoria"))
    despesa_post["descricao"] = request.POST.get("descricao")
    despesa_post["valor"] = request.POST.get("valor")
    despesa_post["vencimento"] = request.POST.get("vencimento")
    return despesa_post


def create_data_form_despesa(request, contexto):
    data = dict()
    html_form_despesas(request, contexto, data)
    # html_multas_pagar(request, contexto, data)
    return JsonResponse(data)


def html_form_despesas(request, contexto, data):
    data["html_form_despesas"] = render_to_string(
        "despesas/html_form_despesas.html", contexto, request=request
    )
    return data


def create_contexto_categoria():
    categorias = Categorias.objects.all().order_by("Categoria")
    lista = [
        {"idcategoria": x.idCategoria, "categoria": x.Categoria} for x in categorias
    ]
    return lista


def save_categoria(_cat):
    obj = Categorias()
    obj.Categoria = _cat["categoria"]
    obj.save()


def valida_categoria(request):
    msg = dict()
    error = False
    # Valida Categoria
    _categoria = request.POST.get("categoria")
    if not _categoria:
        msg["erro_categoria"] = "Obrigatório inserir uma categoria."
        error = True
    return error, msg


def read_categoria_post(request):
    categoria_post = dict()
    categoria_post["idcategoria"] = request.POST.get("idMulta")
    categoria_post["categoria"] = request.POST.get("categoria")
    return categoria_post


def create_data_form_categoria(request, contexto):
    data = dict()
    html_form_categoria(request, contexto, data)
    return JsonResponse(data)


def html_form_categoria(request, contexto, data):
    data["html_form_categorias"] = render_to_string(
        "despesas/html_form_categorias.html", contexto, request=request
    )
    return data


def create_contexto_subcategoria(_cat):
    subcategorias = SubCategorias.objects.filter(idCategoria_id=_cat).order_by(
        "SubCategoria"
    )
    lista = [
        {"idsubcategoria": x.idSubCategoria, "subcategoria": x.SubCategoria}
        for x in subcategorias
    ]
    return lista


def save_subcategoria(_cat):
    obj = SubCategorias()
    obj.idCategoria_id = _cat["categoria"]
    obj.SubCategoria = _cat["subcategoria"]
    obj.save()


def valida_subcategoria(request):
    msg = dict()
    error = False
    # Valida Categoria
    _categoria = request.POST.get("categoria")
    if int(_categoria) == 0:
        msg["erro_categoria"] = "Obrigatório inserir uma categoria."
        error = True
    # Valida SubCategoria
    _subcategoria = request.POST.get("subcategoria")
    if not _subcategoria:
        msg["erro_subcategoria"] = "Obrigatório inserir uma subcategoria."
        error = True
    return error, msg


def read_subcategoria_post(request):
    subcategoria_post = dict()
    subcategoria_post["idsubcategoria"] = request.POST.get("idMulta")
    subcategoria_post["categoria"] = request.POST.get("categoria")
    subcategoria_post["subcategoria"] = request.POST.get("subcategoria")
    return subcategoria_post


def create_data_form_subcategoria(request, contexto):
    data = dict()
    html_form_subcategoria(request, contexto, data)
    return JsonResponse(data)


def html_form_subcategoria(request, contexto, data):
    data["html_form_subcategorias"] = render_to_string(
        "despesas/html_form_subcategorias.html", contexto, request=request
    )
    return data


def create_data_choice_subcategoria(request, contexto):
    data = dict()
    html_choice_subcategoria(request, contexto, data)
    return JsonResponse(data)


def html_choice_subcategoria(request, contexto, data):
    data["html_choice_subcategorias"] = render_to_string(
        "despesas/html_choice_subcategorias.html", contexto, request=request
    )
    return data


def create_contexto_despesas():
    despesas = Despesas.objects.filter(DataPgto="2001-01-01").order_by("-Vencimento")
    lista = [
        {
            "id_despesa": x.id_Despesa,
            "cedente": x.Cedente,
            "categoria": x.Categoria,
            "subcategoria": x.SubCategoria,
            "valor": x.Valor,
            "vencimento": x.Vencimento,
        }
        for x in despesas
    ]
    return lista
