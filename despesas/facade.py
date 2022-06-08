import datetime
from decimal import Decimal

from django.http import JsonResponse
from django.template.loader import render_to_string
from minutas.facade import nome_curto
from minutas.models import Minuta, MinutaColaboradores
from pagamentos.facade import create_vales
from pessoas.models import Vales
from veiculos.models import Veiculo

from despesas.models import Abastecimento, Multas


def create_despesas_context():
    abastecimento = get_abastecimento_all()
    veiculos = Veiculo.objects.filter(Proprietario_id=17)
    multas = Multas.objects.filter(Pago=False).order_by("-Vencimento")
    lista = []
    for x in multas:
        multa = f"MULTA - {x.NumeroDOC}"
        motorista = None
        if x.DescontaMotorista:
            motorista = Vales.objects.filter(Descricao__startswith=multa)
            if motorista:
                motorista = nome_curto(motorista[0].idPessoal.Nome)
            else:
                motorista = "VALE NÃO ENCONTRADO"
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
            }
        )
    print(lista)
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    context = {
        "abastecimento": abastecimento,
        "veiculos": veiculos,
        "hoje": hoje,
        "multas": lista,
    }
    return context


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
        msg["erro_doc"] = "Obrigatório o número DOC."
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
    print(_veiculo)
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

    # _id_pes = request.POST.get("idpessoal")
    # contexto = create_despesas_context()
    # contexto.update(msg)
    # contexto.update({"error": error})
    # data = read_multa(request, None)
    # # data["html_form_multas"] = render_to_string(
    # #     "despesas/html_form_multas.html", contexto, request=request
    # # )
    # if not error:
    #     save_multa(request, _linha, _linha_sp, _id_pes)
    # # return JsonResponse(data)
    # return data


def save_multa(request, _linha, _linha_sp, _id_pes):
    obj = Multas()
    obj.NumeroAIT = request.POST.get("ait")
    obj.NumeroDOC = request.POST.get("doc")
    obj.DataMulta = datetime.datetime.strptime(
        request.POST.get("data"), "%Y-%m-%d"
    ).date()
    obj.HoraMulta = datetime.datetime.strptime(request.POST.get("hora"), "%H:%M").time()
    obj.ValorMulta = request.POST.get("valor")
    obj.Vencimento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    obj.LinhaDigitavel = request.POST.get("linha_digitavel")
    obj.DataPagamento = datetime.datetime.strptime(
        request.POST.get("vencimento"), "%Y-%m-%d"
    ).date()
    obj.Infracao = request.POST.get("infracao")
    obj.Local = request.POST.get("local")
    obj.DescontaMotorista = request.POST.get("desconta")
    obj.idVeiculo_id = request.POST.get("veiculo")
    obj.LinhaDigitavel = _linha
    obj.LinhaDigitavelSP = _linha_sp
    obj.save()
    if obj.DescontaMotorista == "True":
        create_vale_multa(obj, _id_pes)


def update_multa(request, _id_mul):
    multa = Multas.objects.filter(idMulta=_id_mul)
    dados_multa = read_multa(request, _id_mul)


def read_multa(request, _id_mul):
    veiculos = Veiculo.objects.filter(Proprietario_id=17)
    error = False
    msg = dict()
    if _id_mul:
        multa = Multas.objects.get(idMulta=_id_mul)
        idmulta = multa.idMulta
        numero_doc = multa.NumeroDOC
        numero_ait = multa.NumeroAIT
        data_multa = datetime.datetime.strftime(multa.DataMulta, "%Y-%m-%d")
        hora_multa = multa.HoraMulta
        valor_multa = str(multa.ValorMulta)
        vencimento = datetime.datetime.strftime(multa.Vencimento, "%Y-%m-%d")
        infracao = multa.Infracao
        local = multa.Local
        pago = multa.Pago
        desconta_motorista = multa.DescontaMotorista
        data_pagamento = multa.DataPagamento
        idveiculo = multa.idVeiculo_id
        linha_digitavel = multa.LinhaDigitavel
        linha_digitavel_sp = multa.LinhaDigitavelSP
    else:
        idmulta = None
        numero_doc = request.POST.get("doc")
        numero_ait = request.POST.get("ait")
        data_multa = request.POST.get("data")
        hora_multa = request.POST.get("hora")
        valor_multa = request.POST.get("valor")
        vencimento = request.POST.get("vencimento")
        infracao = request.POST.get("infracao")
        local = request.POST.get("local")
        pago = None
        desconta_motorista = request.POST.get("desconta")
        data_pagamento = None
        idveiculo = int(request.POST.get("veiculo"))
        linha_digitavel = None
        _linha_sp = f'{request.POST.get("linhasp1")}{request.POST.get("linhasp2")}'
        _linha_sp = _linha_sp.replace(".", "")
        _linha_sp = _linha_sp.replace(" ", "")
        linha_digitavel_sp = _linha_sp
        error, msg = valida_multa(request)
    multa = dict()
    multa["idmulta"] = idmulta
    multa["numero_doc"] = numero_doc
    multa["numero_ait"] = numero_ait
    multa["data_multa"] = data_multa
    multa["hora_multa"] = hora_multa
    multa["valor_multa"] = valor_multa
    multa["vencimento"] = vencimento
    multa["infracao"] = infracao
    multa["local"] = local
    multa["pago"] = pago
    multa["desconta_motorista"] = desconta_motorista
    multa["data_pagamento"] = data_pagamento
    multa["idveiculo"] = idveiculo
    multa["linha_digitavel"] = linha_digitavel
    multa["linha_digitavel_sp"] = linha_digitavel_sp

    data = dict()
    contexto = {"multa": multa, "veiculos": veiculos, "error": error}
    contexto.update(msg)
    data["html_form_multas"] = render_to_string(
        "despesas/html_form_multas.html", contexto, request=request
    )
    return JsonResponse(data)


def delete_multa(_id_mul):
    multa = Multas.objects.filter(idMulta=_id_mul)
    multa.delete()


def create_vale_multa(_obj, _id_pes):
    if _id_pes:
        _des = f"Multa - {_obj.NumeroDOC}"
        _dat = datetime.datetime.today().date()
        _val = _obj.ValorMulta
        _par = 1
        create_vales(_des, _dat, _val, _par, _id_pes)


def busca_minutas_multa(_id_vei, _date):
    _date = datetime.datetime.strptime(_date, "%Y-%m-%d")
    minutas = Minuta.objects.filter(idVeiculo_id=_id_vei, DataMinuta=_date)
    lista = []
    for x in minutas:
        morotista = MinutaColaboradores.objects.get(
            idMinuta_id=x.idMinuta, Cargo="MOTORISTA"
        )
        lista.append(
            {
                "minuta": x.Minuta,
                "inicio": x.HoraInicial,
                "final": x.HoraFinal,
                "fantasia": x.idCliente.Fantasia,
                "motorista": nome_curto(morotista.idPessoal.Nome),
                "idpessoal": morotista.idPessoal_id,
                "demissao": morotista.idPessoal.DataDemissao,
            }
        )
    return lista


def html_minutas_multa(request, _mm):
    data = dict()
    contexto = {
        "minutas": _mm,
    }
    data["html_minutas_multa"] = render_to_string(
        "despesas/html_minutas_multa.html", contexto, request=request
    )
    data["idpessoal"] = _mm[0]["idpessoal"]
    return JsonResponse(data)
