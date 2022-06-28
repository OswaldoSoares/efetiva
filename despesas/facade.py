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
    multas = multas_pagar()
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    context = {
        "abastecimento": abastecimento,
        "veiculos": veiculos,
        "hoje": hoje,
        "multas": multas,
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


def save_multa(multa):
    obj = Multas()
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
    obj.save()
    print(obj.DescontaMotorista)
    if obj.DescontaMotorista == "True":
        create_vale_multa(obj, multa["idpessoal"])


def update_multa(multa, _id_mul):
    multa_selecionada = Multas.objects.get(idMulta=_id_mul)
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
    obj.save()
    if obj.DescontaMotorista == "True":
        create_vale_multa(obj, multa["idpessoal"])


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


def html_multas_pagar(request, contexto, data):
    data["html_multas_pagar"] = render_to_string(
        "despesas/html_multas_pagar.html", contexto, request=request
    )
    return data


def create_data_multas_pagar(request, contexto):
    data = dict()
    html_multas_pagar(request, contexto, data)
    return JsonResponse(data)


def multas_pagar():
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
    return lista


def delete_multa(_id_mul):
    multa = Multas.objects.filter(idMulta=_id_mul)
    multa.delete()


def create_vale_multa(_obj, _id_pes):
    print(_id_pes)
    if _id_pes:
        _des = f"Multa - {_obj.NumeroDOC}"
        _dat = datetime.datetime.today().date()
        _val = _obj.ValorMulta
        _par = 1
        print(_des, _dat, _val, _par, _id_pes)
        create_vales(_des, _dat, _val, _par, _id_pes)


def busca_minutas_multa(_id_vei, _date):
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
                    "fantasia": x.idCliente.Fantasia,
                    "motorista": nome_curto(motorista[0].idPessoal.Nome),
                    "idpessoal": motorista[0].idPessoal_id,
                    "demissao": motorista[0].idPessoal.DataDemissao,
                    "admissao": motorista[0].idPessoal.DataAdmissao,
                    "placa": x.idVeiculo.Placa,
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
    if _mm:
        data["idpessoal"] = _mm[0]["idpessoal"]
    else:
        data["idpessoal"] = 0
    print(data["idpessoal"])
    return JsonResponse(data)
