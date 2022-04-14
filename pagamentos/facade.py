import calendar
import datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import DecimalField, ExpressionWrapper, F, Max, Min, Sum
from django.http import JsonResponse
from django.template.loader import render_to_string
from minutas.models import MinutaColaboradores, MinutaItens
from pessoas import facade
from pessoas.forms import CadastraContraCheque, CadastraContraChequeItens, CadastraVale
from pessoas.models import (
    CartaoPonto,
    ContaPessoal,
    ContraCheque,
    ContraChequeItens,
    Pessoal,
    Salario,
    Vales,
)
from website.facade import Feriados

from pagamentos.models import Recibo, ReciboItens

meses = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]

dias = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO",
]

estado_swith_vales = dict()


def cria_contexto_pagamentos():
    formvales = CadastraVale()
    contexto = {"formvales": formvales}
    return contexto


def create_context(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    folha = {}
    referencia = {"MesReferencia": mesreferencia, "AnoReferencia": anoreferencia}
    totalsalario = 0.00
    totalfolha = 0.00
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    for itens in mensalistas:
        folha[itens.Nome] = {
            "Salario": "0,00",
            "Liquido": "0,00",
            "ContraCheque": False,
            "CartaoPonto": False,
            "idPessoal": itens.idPessoal,
        }
        salario = get_salario(itens.idPessoal)
        totalsalario += float(salario[0].Salario)
        folha[itens.Nome]["Salario"] = salario[0].Salario
        contracheque = get_contrachequereferencia(
            mesreferencia, anoreferencia, itens.idPessoal
        )
        if contracheque:
            totais = saldo_contracheque(contracheque[0].idContraCheque)
            folha[itens.Nome]["Liquido"] = totais["Liquido"]
            totalfolha += float(totais["Liquido"])
        if busca_contracheque(mes, anoreferencia, itens.idPessoal):
            folha[itens.Nome]["ContraCheque"] = True
        if busca_cartaoponto_referencia(mesreferencia, anoreferencia, itens.idPessoal):
            folha[itens.Nome]["CartaoPonto"] = True
    totalsalario = "{0:.2f}".format(totalsalario).replace(".", ",")
    totalfolha = "{0:.2f}".format(totalfolha).replace(".", ",")
    contexto = {
        "folha": folha,
        "referencia": referencia,
        "totalsalario": totalsalario,
        "totalfolha": totalfolha,
    }
    return contexto


def create_context_formcontracheque():
    formcontracheque = CadastraContraCheque()
    contexto = {"formcontracheque": formcontracheque}
    return contexto


def create_context_avulso():
    periodo = get_periodo_pagamento_avulsos()
    # saldo = get_saldo_pagamento_avulso(periodo['DataInicial'], periodo['DataFinal'])
    contexto = {"periodo": periodo}
    return contexto


def get_periodo_pagamento_avulsos():
    periodo = (
        MinutaColaboradores.objects.filter(Pago=False)
        .exclude(idPessoal__TipoPgto="MENSALISTA")
        .aggregate(
            DataInicial=Min("idMinuta__DataMinuta"),
            DataFinal=Max("idMinuta__DataMinuta"),
        )
    )
    periodo["DataInicial"] = periodo["DataInicial"].strftime("%Y-%m-%d")
    periodo["DataFinal"] = periodo["DataFinal"].strftime("%Y-%m-%d")
    return periodo


def get_saldo_pagamento_avulso(datainicial, datafinal):
    saldo = []
    avulsos = list_avulsos_ativo()
    saldo_total = 0
    saldo_vales = 0
    total_select = 0
    for colaboradores in avulsos:
        colaborador = MinutaColaboradores.objects.filter(
            idPessoal__Nome=colaboradores.Nome, Pago=False
        ).exclude(idMinuta__StatusMinuta="ABERTA")
        saldo_colaborador = 0
        for index, itens in enumerate(colaborador):
            if itens.Cargo == "AJUDANTE":
                base_valor = ExpressionWrapper(
                    F("Valor") / F("Quantidade"), output_field=DecimalField()
                )
                ajudante = MinutaItens.objects.values(ValorAjudante=base_valor).filter(
                    TipoItens="PAGA",
                    idMinuta=itens.idMinuta,
                    Descricao="AJUDANTE",
                    idMinuta_id__DataMinuta__range=[datainicial, datafinal],
                )
                if ajudante:
                    saldo_colaborador += ajudante[0]["ValorAjudante"]
                    saldo_total += ajudante[0]["ValorAjudante"]
            elif itens.Cargo == "MOTORISTA":
                motorista = (
                    MinutaItens.objects.filter(
                        TipoItens="PAGA",
                        idMinuta=itens.idMinuta,
                        idMinuta_id__DataMinuta__range=[datainicial, datafinal],
                    )
                    .exclude(Descricao="AJUDANTE")
                    .aggregate(ValorMotorista=Sum("Valor"))
                )
                if motorista["ValorMotorista"]:
                    saldo_colaborador += motorista["ValorMotorista"]
                    saldo_total += motorista["ValorMotorista"]
        total_vales = calcula_total_vales(colaboradores.idPessoal)
        if not total_vales:
            total_vales = 0
        saldo_vales += total_vales
        dict_vale, saldo_vales_select = get_vales_select(colaboradores.idPessoal, 0)
        total_select += saldo_vales_select
        " Colocar aqui condição para mostrar apenas colaboradores com saldo ou vale"
        # if saldo_colaborador > 0 or saldo_vales > 0:
        saldo.append(
            {
                "Nome": colaboradores.Nome,
                "idPessoal": colaboradores.idPessoal,
                "Saldo": saldo_colaborador,
                "ValeSelect": saldo_vales_select,
                "ValeTotal": total_vales,
            }
        )
    return saldo, saldo_total, saldo_vales, total_select


def get_vales_select(idpessoal, idcontracheque):
    """

    :param idpessoal:
    :param idcontracheque:
    :return:
    """
    "Procura no dict 'estado_switch_vales' se existe a chave 'idpessoal, caso não exista é incluida"
    if idpessoal not in estado_swith_vales.keys():
        estado_swith_vales[str(idpessoal)] = ""
    "Cria dict vales"
    dict_vale = dict()
    vale = Vales.objects.filter(idPessoal=idpessoal, Pago=False)
    for itens in vale:
        dict_vale["id{}".format(itens.idVales)] = {
            "idVales": itens.idVales,
            "Data": itens.Data,
            "Descricao": itens.Descricao,
            "Valor": itens.Valor,
            "Checked": True,
        }

    content_descricao = None
    saldo_vales_select = 0
    "Percorre dict vales"
    for itens in dict_vale:
        "Se encontrar um vale PARCELADO, seleciona apenas a parcela mais nova"
        if dict_vale[itens]["Descricao"][-9:] == "PARCELADO":
            if content_descricao:
                dict_vale[itens]["Checked"] = True
            if content_descricao == dict_vale[itens]["Descricao"][0:-16]:
                dict_vale[itens]["Checked"] = False
            content_descricao = dict_vale[itens]["Descricao"][0:-16]
            "Busca se o vale já está no contravale, e seleciona mesmo se não for a parcela mais nova"
            if busca_contracheque_itens_vale(dict_vale[itens]["idVales"]):
                dict_vale[itens]["Checked"] = True
        "Se o usuario fez alguma alteração na seleção, é mantida"
        if "Manual" in estado_swith_vales[str(idpessoal)]:
            if str(dict_vale[itens]["idVales"]) in estado_swith_vales[str(idpessoal)]:
                dict_vale[itens]["Checked"] = True
            else:
                dict_vale[itens]["Checked"] = False
        "Busca o vale no conrracheque, se não tiver cria"
        if idcontracheque > 0:
            if dict_vale[itens]["Checked"]:
                if not busca_contracheque_itens_vale(dict_vale[itens]["idVales"]):
                    create_contracheque_itens_vales(
                        idpessoal, dict_vale[itens]["idVales"], idcontracheque
                    )
        "Calcula saldo dos vales"
        if dict_vale[itens]["Checked"]:
            saldo_vales_select += dict_vale[itens]["Valor"]
    return dict_vale, saldo_vales_select


def get_vale_id(idvales):
    vale = Vales.objects.get(idVales=idvales)
    return vale


def get_recibo_id(idrecibo):
    recibo = Recibo.objects.get(idRecibo=idrecibo)
    return recibo


def calcula_total_vales(idpessoal):
    totalvales = Vales.objects.filter(
        idPessoal=idpessoal, Pago=False, idRecibo_id="144"
    ).aggregate(ValorTotal=Sum("Valor"))
    return totalvales["ValorTotal"]


def seleciona_minutasavulso(datainicial, datafinal, idpessoal):
    data = dict()
    data["html_minutas"] = html_minutasavulso(datainicial, datafinal, idpessoal)
    data["html_recibos"] = html_recibo_avulso(datainicial, datafinal, idpessoal)
    data["html_valesavulso"] = html_vale(idpessoal, "avulso", 0)
    c_return = JsonResponse(data)
    return c_return


def html_minutasavulso(datainicial, datafinal, idpessoal):
    recibo = []
    colaborador = facade.get_pessoal(idpessoal)
    minutas = (
        MinutaColaboradores.objects.filter(
            idPessoal=idpessoal,
            Pago=False,
            idMinuta_id__DataMinuta__range=[datainicial, datafinal],
        )
        .exclude(idMinuta__StatusMinuta="ABERTA")
        .exclude(idMinuta__StatusMinuta="CONCLUIDA")
    )
    for index, itens in enumerate(minutas):
        if itens.Cargo == "AJUDANTE":
            minutaitens = MinutaItens.objects.filter(
                TipoItens="PAGA",
                idMinuta=itens.idMinuta,
                Descricao="AJUDANTE",
                idMinuta_id__DataMinuta__range=[datainicial, datafinal],
            )
            if minutaitens:
                recibo.append(
                    {
                        "Data": itens.idMinuta.DataMinuta,
                        "Minuta": itens.idMinuta.Minuta,
                        "Cliente": itens.idMinuta.idCliente.Fantasia,
                        "Descricao": minutaitens[0].Descricao,
                        "Valor": minutaitens[0].ValorBase,
                    }
                )
        elif itens.Cargo == "MOTORISTA":
            minutaitens = MinutaItens.objects.filter(
                TipoItens="PAGA",
                idMinuta=itens.idMinuta,
                idMinuta_id__DataMinuta__range=[datainicial, datafinal],
            ).exclude(Descricao="AJUDANTE")
            for minutas in minutaitens:
                recibo.append(
                    {
                        "Data": itens.idMinuta.DataMinuta,
                        "Minuta": itens.idMinuta.Minuta,
                        "Cliente": itens.idMinuta.idCliente.Fantasia,
                        "Descricao": minutas.Descricao,
                        "Valor": minutas.Valor,
                    }
                )
    context = {
        "recibo": recibo,
        "colaborador": colaborador,
        "datainicial": datainicial,
        "datafinal": datafinal,
    }
    c_return = render_to_string("pagamentos/minutasavulso.html", context)
    return c_return


def create_folha(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    for itens in mensalistas:
        create_contracheque(mesreferencia, anoreferencia, "0.00", itens.idPessoal)
        create_cartaoponto(mesreferencia, anoreferencia, itens.idPessoal)


def create_pagamento_avulso(datainicial, datafinal, idpessoal, vales):
    print("teste de test")
    recibo = []
    minutas = (
        MinutaColaboradores.objects.filter(
            idPessoal=idpessoal,
            Pago=False,
            idMinuta_id__DataMinuta__range=[datainicial, datafinal],
        )
        .exclude(idMinuta__StatusMinuta="ABERTA")
        .exclude(idMinuta__StatusMinuta="CONCLUIDA")
    )
    if minutas:
        for index, itens in enumerate(minutas):
            motorista = MinutaColaboradores.objects.filter(
                Cargo="MOTORISTA", idMinuta_id=itens.idMinuta
            )
            if motorista:
                motorista_nome = motorista[0].idPessoal
            else:
                motorista_nome = ""
            if itens.Cargo == "AJUDANTE":
                minutaitens = MinutaItens.objects.filter(
                    TipoItens="PAGA",
                    idMinuta=itens.idMinuta,
                    Descricao="AJUDANTE",
                    idMinuta_id__DataMinuta__range=[datainicial, datafinal],
                )
                if minutaitens:
                    recibo.append(
                        {
                            "Data": itens.idMinuta.DataMinuta,
                            "Minuta": itens.idMinuta.Minuta,
                            "Cliente": itens.idMinuta.idCliente.Fantasia,
                            "Descricao": minutaitens[0].Descricao,
                            "Valor": minutaitens[0].ValorBase,
                            "Motorista": motorista_nome,
                            "idMinutaItens": minutaitens[0].idMinutaItens,
                        }
                    )
            elif itens.Cargo == "MOTORISTA":
                minutaitens = MinutaItens.objects.filter(
                    TipoItens="PAGA",
                    idMinuta=itens.idMinuta,
                    idMinuta_id__DataMinuta__range=[datainicial, datafinal],
                ).exclude(Descricao="AJUDANTE")
                for x in minutaitens:
                    recibo.append(
                        {
                            "Data": itens.idMinuta.DataMinuta,
                            "Minuta": itens.idMinuta.Minuta,
                            "Cliente": itens.idMinuta.idCliente.Fantasia,
                            "Descricao": x.Descricao,
                            "Valor": x.Valor,
                            "Motorista": motorista_nome,
                            "idMinutaItens": x.idMinutaItens,
                        }
                    )
        total_recibo = 0.00
        for itens in recibo:
            total_recibo += float(itens["Valor"])
        total_vales = 0.00
        for itens in vales:
            vale = Vales.objects.get(idVales=itens[3:-5])
            total_vales += float(vale.Valor)
        # html_recibo_avulso(idpessoal)
        if total_recibo >= total_vales:
            numero_recibo = Recibo.objects.aggregate(Maior=Max("Recibo"))
            if not numero_recibo["Maior"]:
                numero_recibo = 1431
            else:
                numero_recibo = numero_recibo["Maior"] + 1
            obj = Recibo()
            obj.Recibo = numero_recibo
            obj.DataRecibo = datetime.date.today()
            obj.ValorRecibo = total_recibo - total_vales
            obj.idPessoal_id = idpessoal
            obj.save()
            new_idrecibo = obj.idRecibo
            for itens in recibo:
                obj = ReciboItens()
                obj.idRecibo_id = new_idrecibo
                obj.idMinutaItens_id = itens["idMinutaItens"]
                obj.save()
            for itens in vales:
                vale = Vales.objects.get(idVales=itens[3:-5])
                obj = vale
                obj.Pago = True
                obj.idRecibo_id = new_idrecibo
                obj.save(update_fields=["Pago", "idRecibo_id"])
            for itens in minutas:
                obj = itens
                obj.Pago = True
                obj.idRecibo_id = new_idrecibo
                obj.save(update_fields=["Pago", "idRecibo_id"])
    data = dict()
    data["html_saldoavulso"] = html_saldo_avulso(datainicial, datafinal)
    data["html_minutas"] = html_minutasavulso(datainicial, datafinal, idpessoal)
    data["html_recibos"] = html_recibo_avulso(datainicial, datafinal, idpessoal)
    data["html_valesavulso"] = html_vale(idpessoal, "avulso", 0)
    c_return = JsonResponse(data)
    return c_return


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month or int(anoreferencia) > admissao.year:
            salario = get_salario(idpessoal)
            contracheque = busca_contracheque(
                meses[int(mesreferencia) - 1], anoreferencia, idpessoal
            )
            if not contracheque:
                obj = ContraCheque()
                obj.MesReferencia = meses[int(mesreferencia) - 1]
                obj.AnoReferencia = anoreferencia
                obj.Valor = valor
                obj.idPessoal_id = idpessoal
                obj.save()
            contracheque = busca_contracheque(
                meses[int(mesreferencia) - 1], anoreferencia, idpessoal
            )
            contracheque_itens = get_contrachequeitens(
                contracheque[0].idContraCheque, "SALARIO", "C"
            )
            if not contracheque_itens:
                "Se o colaborador foi admitido neste Mês/Ano calcula salario proporcional"
                if (
                    int(anoreferencia) == admissao.year
                    and int(mesreferencia) == admissao.month
                ):
                    dias_mes = 30 - admissao.day + 1
                    salario = salario[0].Salario / 30 * dias_mes
                    create_contracheque_itens(
                        "SALARIO",
                        salario,
                        "{}d".format(dias_mes).zfill(2),
                        "C",
                        contracheque[0].idContraCheque,
                    )
                else:
                    create_contracheque_itens(
                        "SALARIO",
                        salario[0].Salario,
                        "30d",
                        "C",
                        contracheque[0].idContraCheque,
                    )
            else:
                "Se o colaborador foi admitido neste Mês/Ano calcula salario proporcional"
                if (
                    int(anoreferencia) == admissao.year
                    and int(mesreferencia) == admissao.month
                ):
                    dias_mes = 30 - admissao.day + 1
                    salario = salario[0].Salario / 30 * dias_mes
                    altera_contracheque_itens(
                        contracheque_itens, salario, "{}d".format(dias_mes).zfill(2)
                    )
                else:
                    altera_contracheque_itens(
                        contracheque_itens, salario[0].Salario, "30d"
                    )


def create_contracheque_itens(descricao, valor, referencia, registro, idcontracheque):
    if float(valor) > 0:
        saldo = saldo_contracheque(idcontracheque)
        if float(valor) <= float(saldo["Liquido"]) or descricao == "SALARIO":
            if not busca_contrachequeitens(idcontracheque, descricao, registro):
                obj = ContraChequeItens()
                obj.Descricao = descricao
                obj.Valor = valor
                obj.Referencia = referencia
                obj.Registro = registro
                obj.idContraCheque_id = idcontracheque
                obj.save()


def create_contracheque_itens_vales(idcliente, idvale, idcontracheque):
    vale = get_vale_id(idvale)
    if not busca_contracheque_itens_vale(idvale):
        obj = ContraChequeItens()
        if vale.Descricao[-9:] == "PARCELADO":
            obj.Descricao = vale.Descricao[0:-10]
            obj.Referencia = vale.Descricao[-15:-9]
        else:
            obj.Descricao = vale.Descricao
        obj.Valor = vale.Valor
        obj.Registro = "D"
        obj.idContraCheque_id = idcontracheque
        obj.Vales_id = idvale
        obj.save()


def busca_feriados(mesreferencia, anoreferencia):
    lista_feriados = Feriados("Lista", "Feriado")
    lista_feriados = lista_feriados.__dict__["feriados"]
    dias_feriado_mes = []
    for x in lista_feriados:
        feriado = datetime.datetime.strptime(x, "%Y-%m-%d")
        if int(anoreferencia) == feriado.year and int(mesreferencia) == feriado.month:
            dias_feriado_mes.append(feriado.day)
    return dias_feriado_mes


def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    dias_feriado_mes = busca_feriados(mesreferencia, anoreferencia)
    if not busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
        if int(anoreferencia) >= admissao.year:
            if (
                int(mesreferencia) >= admissao.month
                or int(anoreferencia) > admissao.year
            ):
                admissao = datetime.datetime(
                    admissao.year, admissao.month, admissao.day
                )
                referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
                for x in range(1, referencia[1] + 1):
                    dia = "{}-{}-{}".format(anoreferencia, mesreferencia, x)
                    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
                    obj = CartaoPonto()
                    obj.Dia = dia
                    obj.Entrada = "07:00"
                    obj.Saida = "17:00"
                    if dia.weekday() == 5 or dia.weekday() == 6:
                        obj.Ausencia = dias[dia.weekday()]
                    else:
                        obj.Ausencia = ""
                    if dia in dias_feriado_mes:
                        obj.Ausencia = "FERIADO"
                    if dia < admissao:
                        obj.Ausencia = "-------"
                    obj.idPessoal_id = idpessoal
                    obj.save()
    else:
        if int(mesreferencia) == admissao.month and int(anoreferencia) == admissao.year:
            confere_admissao(idpessoal, admissao)
    atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal)


def confere_admissao(idpessoal, admissao):
    cartaoponto = busca_cartaoponto_referencia(admissao.month, admissao.year, idpessoal)
    for itens in cartaoponto:
        dia_cartaoponto = get_cartaopontoid(itens.idCartaoPonto)
        obj = dia_cartaoponto
        if itens.Dia < admissao:
            obj.Ausencia = "-------"
        else:
            if itens.Dia.weekday() == 5 or itens.Dia.weekday() == 6:
                obj.Ausencia = dias[itens.Dia.weekday()]
            else:
                obj.Ausencia = ""
        obj.save(update_fields=["Ausencia"])


def cria_vale(data, descricao, valor, parcelas, idpessoal):
    if int(parcelas) > 0:
        for x in range(int(parcelas)):
            obj = Vales()
            obj.Data = data
            if int(parcelas) == 1:
                obj.Descricao = descricao
            else:
                obj.Descricao = "{} {}/{} PARCELADO".format(
                    descricao, str(x + 1).zfill(2), parcelas.zfill(2)
                )
            obj.Valor = float(valor) / int(parcelas)
            obj.idPessoal_id = idpessoal
            obj.save()


def exclui_vale(idvales):
    vale = get_vale_id(idvales)
    vale.delete()


def exclui_recibo(idrecibo, datainicial, datafinal, idpessoal):
    periodo = get_periodo_pagamento_avulsos()
    datainicial = periodo["DataInicial"]
    datafinal = periodo["DataFinal"]
    Vales.objects.filter(idRecibo_id=idrecibo).update(idRecibo_id=None, Pago=False)
    MinutaColaboradores.objects.filter(idRecibo_id=idrecibo).update(
        idRecibo_id=None, Pago=False
    )
    reciboitens = ReciboItens.objects.filter(idRecibo_id=idrecibo)
    if reciboitens:
        reciboitens.delete()
    recibo = get_recibo_id(idrecibo)
    if recibo:
        recibo.delete()
    data = dict()
    data["html_saldoavulso"] = html_saldo_avulso(datainicial, datafinal)
    data["html_minutas"] = html_minutasavulso(datainicial, datafinal, idpessoal)
    data["html_recibos"] = html_recibo_avulso(datainicial, datafinal, idpessoal)
    data["html_valesavulso"] = html_vale(idpessoal, "avulso", 0)
    c_return = JsonResponse(data)
    return c_return


def get_contracheque(idpessoal: int):
    contracheque = ContraCheque.objects.filter(idPessoal=idpessoal)
    return contracheque


def get_contrachequeid(idcontracheque: int):
    contracheque = ContraCheque.objects.filter(idContraCheque=idcontracheque)
    return contracheque


def get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    contracheque = ContraCheque.objects.filter(
        MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    return contracheque


def get_contrachequeitens(idcontracheque, descricao, registro):
    try:
        contrachequeitens = ContraChequeItens.objects.get(
            idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
        )
    except ObjectDoesNotExist:
        contrachequeitens = None
    return contrachequeitens


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


def get_cartaopontoid(idcartaoponto):
    cartaoponto = CartaoPonto.objects.get(idCartaoPonto=idcartaoponto)
    return cartaoponto


def busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = meses.index(mesreferencia) + 1
    else:
        mes = int(mesreferencia)
    dia = "{}-{}-{}".format(anoreferencia, mes, 1)
    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
    referencia = calendar.monthrange(int(anoreferencia), mes)
    diafinal = "{}-{}-{}".format(anoreferencia, mes, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, "%Y-%m-%d")
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    if cartaoponto:
        return cartaoponto


def busca_contracheque(mesreferencia, anoreferencia, idpessoal):
    contracheque = ContraCheque.objects.filter(
        MesReferencia=mesreferencia, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    return contracheque


def busca_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
    )
    return contrachequeitens


def busca_contracheque_itens_vale(idvale):
    contracheque_itens_vale = ContraChequeItens.objects.filter(Vales_id=idvale)
    if contracheque_itens_vale:
        return True


def busca_adiantamento(idcontracheque):
    if ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao="ADIANTAMENTO", Registro="D"
    ):
        return True
    else:
        return False


def delete_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
    )
    contrachequeitens.delete()


def delete_contracheque_itens_vale(idvale):
    contracheque_itens_vale = ContraChequeItens.objects.filter(Vales_id=idvale)
    contracheque_itens_vale.delete()


def seleciona_folha(mesreferencia, anoreferencia):
    data = dict()
    data["html_folha"] = html_folha(mesreferencia, anoreferencia)
    c_return = JsonResponse(data)
    return c_return


def seleciona_contracheque(mesreferencia, anoreferencia, idpessoal, request):
    data = dict()
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    data["html_folha"] = html_folha(mesreferencia, anoreferencia)
    data["html_minutascontracheque"] = html_minutascontracheque(
        mesreferencia, anoreferencia, idpessoal
    )
    data["html_vales"] = html_vale(
        idpessoal, "mensalista", contracheque[0].idContraCheque
    )
    data["html_formccitens"] = html_formccitens(contracheque, request)
    data["html_formccadianta"] = html_formccadianta(contracheque, request)
    data["html_adiantamento"] = busca_adiantamento(contracheque[0].idContraCheque)
    data["html_contracheque"] = html_contracheque(
        mesreferencia, anoreferencia, idpessoal
    )
    data["html_cartaoponto"] = html_cartaoponto(mesreferencia, anoreferencia, idpessoal)
    c_return = JsonResponse(data)
    return c_return


def seleciona_saldoavulso(datainicial, datafinal):
    data = dict()
    data["html_saldoavulso"] = html_saldo_avulso(datainicial, datafinal)
    c_return = JsonResponse(data)
    return c_return


def periodo_cartaoponto(mesreferencia, anoreferencia):
    if mesreferencia in meses:
        mesreferencia = meses.index(mesreferencia) + 1
    dia = "{}-{}-{}".format(anoreferencia, mesreferencia, 1)
    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
    referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
    diafinal = "{}-{}-{}".format(anoreferencia, mesreferencia, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, "%Y-%m-%d")
    return dia, diafinal


def seleciona_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    context = {
        "cartaoponto": cartaoponto,
        "mesreferencia": mesreferencia,
        "anoreferencia": anoreferencia,
        "idpessoal": idpessoal,
    }
    return render_to_string("pagamentos/cartaoponto.html", context)


def seleciona_vales(idpessoal):
    data = dict()
    colaborador = facade.get_pessoal(idpessoal)
    if colaborador[0].TipoPgto == "MENSALISTA":
        data["html_vales"] = html_vale(idpessoal, "mensalista", 0)
    else:
        data["html_valesavulso"] = html_vale(idpessoal, "avulso", 0)
    c_return = JsonResponse(data)
    return c_return


def select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    minutas = (
        MinutaColaboradores.objects.filter(
            idPessoal=idpessoal, idMinuta_id__DataMinuta__range=(dia, diafinal)
        )
        .exclude(idMinuta_id__StatusMinuta="ABERTA")
        .order_by("idMinuta_id__DataMinuta")
        .values(
            "idMinuta_id__DataMinuta",
            "idMinuta_id__Minuta",
            "idMinuta_id__idCliente__Fantasia",
            "idMinuta_id__HoraInicial",
            "idMinuta_id__HoraFinal",
            "idPessoal",
        )
    )
    minutas = list(minutas)
    horaentrada = datetime.timedelta(hours=7, minutes=0)
    horasaida = datetime.timedelta(hours=17, minutes=0)
    for itens in minutas:
        extra_entrada = datetime.timedelta(hours=0, minutes=0)
        horainicial = datetime.timedelta(
            hours=itens["idMinuta_id__HoraInicial"].hour,
            minutes=itens["idMinuta_id__HoraInicial"].minute,
        )
        if horainicial < horaentrada:
            extra_entrada = horaentrada - horainicial
        extra_saida = datetime.timedelta(hours=0, minutes=0)
        if itens["idMinuta_id__HoraFinal"]:
            horafinal = datetime.timedelta(
                hours=itens["idMinuta_id__HoraFinal"].hour,
                minutes=itens["idMinuta_id__HoraFinal"].minute,
            )
            if horafinal > horasaida:
                extra_saida = horafinal - horasaida
        extra = extra_entrada + extra_saida
        itens["Extra"] = str(extra)[:-3].zfill(5)
    return minutas


def html_recibo_avulso(datainicial, datafinal, idpessoal):
    recibos = Recibo.objects.filter(idPessoal_id=idpessoal).order_by(
        "-DataRecibo", "-Recibo"
    )
    context = {
        "recibos": recibos,
        "idpessoal": idpessoal,
        "datainicial": datainicial,
        "datafinal": datafinal,
    }
    c_return = render_to_string("pagamentos/reciboavulso.html", context)
    return c_return


def html_minutascontracheque(mesreferencia, anoreferencia, idpessoal):
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    context = {"minutas": minutas, "idPessoal": idpessoal}
    c_return = render_to_string("pagamentos/minutascontracheque.html", context)
    return c_return


def atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    demissao = colaborador[0].DataDemissao
    totalextra = 0
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month or int(anoreferencia) > admissao.year:
            minutas = select_minutas_contracheque(
                mesreferencia, anoreferencia, idpessoal
            )
            for x in minutas:
                cartaoponto = CartaoPonto.objects.get(
                    Dia=x["idMinuta_id__DataMinuta"], idPessoal_id=x["idPessoal"]
                )
                obj = cartaoponto
                horaentrada = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
                horasaida = datetime.datetime.strptime("17:00:00", "%H:%M:%S").time()
                if obj.Alteracao == "ROBOT" and obj.Ausencia != "FALTA":
                    if x["idMinuta_id__HoraInicial"]:
                        if x["idMinuta_id__HoraInicial"] != obj.Entrada:
                            if x["idMinuta_id__HoraInicial"] < horaentrada:
                                obj.Entrada = x["idMinuta_id__HoraInicial"]
                                obj.save(update_fields=["Entrada"])
                    if x["idMinuta_id__HoraFinal"]:
                        if x["idMinuta_id__HoraFinal"] != obj.Saida:
                            if x["idMinuta_id__HoraFinal"] > horasaida:
                                obj.Saida = x["idMinuta_id__HoraFinal"]
                                obj.save(update_fields=["Saida"])
            totalextra = calcula_horas_extras(mesreferencia, anoreferencia, idpessoal)
            calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
            cartao_ponto = busca_cartaoponto_referencia(
                mesreferencia, anoreferencia, idpessoal
            )
            dias_feriado_mes = busca_feriados(mesreferencia, anoreferencia)
            for itens in cartao_ponto:
                obj = itens
                if itens.Dia.day in dias_feriado_mes:
                    obj.Ausencia = "FERIADO"
                    obj.save(update_fields=["Ausencia"])
            if demissao:
                for itens in cartao_ponto:
                    obj = itens
                    if itens.Dia > demissao:
                        obj.Ausencia = "-------"
                        obj.save(update_fields=["Ausencia"])
                calcula_faltas(mesreferencia, anoreferencia, idpessoal)
    return totalextra


def altera_horario_manual(idcartaoponto, horaentrada, horasaida):
    obj = get_cartaopontoid(idcartaoponto)
    obj.Entrada = horaentrada
    obj.Saida = horasaida
    obj.save(update_fields=["Entrada", "Saida"])


def altera_contracheque_itens(contrachequeitens, valorhoraextra, referencia):
    if float(valorhoraextra) > 0:
        obj = contrachequeitens
        obj.Valor = valorhoraextra
        obj.Referencia = referencia
        obj.save(update_fields=["Valor", "Referencia"])


def altera_falta(mesreferencia, anoreferencia, idpessoal, idcartaoponto, request):
    data = dict()
    cartaoponto = CartaoPonto.objects.get(idCartaoPonto=idcartaoponto)
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    obj = cartaoponto
    if obj.Ausencia == "FALTA":
        obj.Ausencia = ""
        obj.Alteracao = "ROBOT"
    else:
        obj.Ausencia = "FALTA"
        obj.Alteracao = "ROBOT"
    obj.Entrada = "07:00:00"
    obj.Saida = "17:00:00"
    obj.save(update_fields=["Ausencia", "Alteracao", "Entrada", "Saida"])
    calcula_faltas(mesreferencia, anoreferencia, idpessoal)
    atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal)
    calcula_conducao(mesreferencia, anoreferencia, idpessoal)
    data["html_adiantamento"] = busca_adiantamento(contracheque[0].idContraCheque)
    data["html_folha"] = html_folha(mesreferencia, anoreferencia)
    data["html_contracheque"] = html_contracheque(
        mesreferencia, anoreferencia, idpessoal
    )
    data["html_cartaoponto"] = html_cartaoponto(mesreferencia, anoreferencia, idpessoal)
    data["html_formccadianta"] = html_formccadianta(contracheque, request)
    data["html_formccitens"] = html_formccitens(contracheque, request)
    data["html_minutascontracheque"] = html_minutascontracheque(
        mesreferencia, anoreferencia, idpessoal
    )
    data["html_vales"] = html_vale(
        idpessoal, "mensalista", contracheque[0].idContraCheque
    )
    c_return = JsonResponse(data)
    return c_return


def html_folha(mesreferencia, anoreferencia):
    contexto = create_context(mesreferencia, anoreferencia)
    c_return = render_to_string("pagamentos/folhapgto.html", contexto)
    return c_return


def html_contracheque(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    contracheque = ContraCheque.objects.filter(
        MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque
    ).order_by("Registro")
    totais = saldo_contracheque(contracheque[0].idContraCheque)
    context = {
        "qs_contracheque": contracheque,
        "qs_contrachequeitens": contrachequeitens,
        "totais": totais,
        "mesreferencia": mesreferencia,
        "anoreferencia": anoreferencia,
    }
    c_return = render_to_string("pagamentos/contracheque.html", context)
    return c_return


def html_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    context = {
        "cartaoponto": cartaoponto,
        "mesreferencia": mesreferencia,
        "anoreferencia": anoreferencia,
        "idpessoal": idpessoal,
    }
    c_return = render_to_string("pagamentos/cartaoponto.html", context)
    return c_return


def html_vale(idpessoal, tipopgto, idcontracheque):
    dict_vale, saldo_vale_select = get_vales_select(idpessoal, idcontracheque)
    context = {
        "dict_vale": dict_vale,
        "idPessoal": idpessoal,
        "TipoPgto": tipopgto,
        "idcontracheque": idcontracheque,
    }
    c_return = render_to_string("pagamentos/vale.html", context)
    return c_return


def print_contracheque_context(idcontracheque, mesreferencia, anoreferencia, idpessoal):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = facade.get_contracheque_itens(idcontracheque)
    colaborador = facade.get_pessoal(contracheque[0].idPessoal_id)
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    credito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if not debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
        "minutas": minutas,
    }
    return contexto


def print_contracheque_adiantamento_context(
    idcontracheque, mesreferencia, anoreferencia, idpessoal
):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = facade.get_contracheque_itens(idcontracheque)
    colaborador = facade.get_pessoal(contracheque[0].idPessoal_id)
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    credito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque,
        Descricao="ADIANTAMENTO",
        Registro="D",
    ).aggregate(Total=Sum("Valor"))
    debito = Decimal("0.00")
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito,
        "Liquido": credito["Total"] - debito,
    }
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
        "minutas": minutas,
    }
    return contexto


def print_contracheque_valetransporte_context(
    idcontracheque, mesreferencia, anoreferencia, idpessoal
):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = facade.get_contracheque_itens(idcontracheque)
    colaborador = facade.get_pessoal(contracheque[0].idPessoal_id)
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    credito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque,
        Descricao="VALE TRANSPORTE",
        Registro="C",
    ).aggregate(Total=Sum("Valor"))
    debito = Decimal("0.00")
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito,
        "Liquido": credito["Total"] - debito,
    }
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
        "minutas": minutas,
    }
    return contexto


def html_formccadianta(contracheque, request):
    formcontrachequeitens = CadastraContraChequeItens()
    contextform = {
        "formcontrachequeitens": formcontrachequeitens,
        "contracheque": contracheque,
    }
    c_return = render_to_string(
        "pagamentos/contrachequeadianta.html", contextform, request=request
    )
    return c_return


def html_formccitens(contracheque, request):
    formcontrachequeitens = CadastraContraChequeItens()
    contextform = {
        "formcontrachequeitens": formcontrachequeitens,
        "contracheque": contracheque,
    }
    c_return = render_to_string(
        "pagamentos/contrachequeitens.html", contextform, request=request
    )
    return c_return


def calcula_faltas(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    demissao = colaborador[0].DataDemissao
    mes_dias = 30
    if int(anoreferencia) == admissao.year and int(mesreferencia) == admissao.month:
        mes_dias -= admissao.day - 1
        dia = admissao
    if demissao:
        if int(anoreferencia) == demissao.year and int(mesreferencia) == demissao.month:
            mes_dias -= 30 - demissao.day
            diafinal = demissao
    faltas = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal, Ausencia="FALTA"
    ).count()
    salario = get_salario(idpessoal)
    desconto = float(salario[0].Salario) / 30 * int(faltas) * 2
    if mes_dias < 30:
        salario = (float(salario[0].Salario) / 30 * mes_dias) - desconto
    else:
        salario = float(salario[0].Salario) - desconto
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    contrachequeitens = get_contrachequeitens(
        contracheque[0].idContraCheque, "SALARIO", "C"
    )
    altera_contracheque_itens(contrachequeitens, salario, f"{mes_dias-faltas}d")


def calcula_horas_extras(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalextra = total_horas_extras(mesreferencia, anoreferencia, idpessoal)
    horazero = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraextra = (
        float(salario[0].Salario) / 30 / 9 / 60 / 60 * 1.5 * totalextra.seconds
    )
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    if totalextra > horazero:
        if contracheque:
            contrachequeitens = get_contrachequeitens(
                contracheque[0].idContraCheque, "HORA EXTRA", "C"
            )
            if contrachequeitens:
                altera_contracheque_itens(contrachequeitens, valorhoraextra, totalextra)
            else:
                if valorhoraextra > 0:
                    create_contracheque_itens(
                        "HORA EXTRA",
                        valorhoraextra,
                        totalextra,
                        "C",
                        contracheque[0].idContraCheque,
                    )
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, "HORA EXTRA", "C")
    return totalextra


def total_horas_extras(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    totalextra = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horaentradapadrao = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
        horaentradapadrao = datetime.timedelta(
            hours=horaentradapadrao.hour, minutes=horaentradapadrao.minute
        )
        horaentradareal = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        if horaentradareal < horaentradapadrao:
            totalextra += horaentradapadrao - horaentradareal
        horasaidapadrao = datetime.datetime.strptime("17:00:00", "%H:%M:%S").time()
        horasaidapadrao = datetime.timedelta(
            hours=horasaidapadrao.hour, minutes=horasaidapadrao.minute
        )
        horasaidareal = datetime.timedelta(hours=x.Saida.hour, minutes=x.Saida.minute)
        if horasaidareal > horasaidapadrao:
            totalextra += horasaidareal - horasaidapadrao
    return totalextra


def calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalatrazo = total_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
    horazero = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraatrazo = float(salario[0].Salario) / 30 / 9 / 60 / 60 * totalatrazo.seconds
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    if totalatrazo > horazero:
        if contracheque:
            contrachequeitens = get_contrachequeitens(
                contracheque[0].idContraCheque, "ATRAZO", "D"
            )
            if contrachequeitens:
                altera_contracheque_itens(
                    contrachequeitens, valorhoraatrazo, totalatrazo
                )
            else:
                if valorhoraatrazo > 0:
                    create_contracheque_itens(
                        "ATRAZO",
                        valorhoraatrazo,
                        totalatrazo,
                        "D",
                        contracheque[0].idContraCheque,
                    )
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, "ATRAZO", "D")
    return totalatrazo


def total_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    totalatrazo = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horaentradapadrao = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
        horaentradapadrao = datetime.timedelta(
            hours=horaentradapadrao.hour, minutes=horaentradapadrao.minute
        )
        horaentradareal = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        if horaentradareal > horaentradapadrao:
            totalatrazo += horaentradareal - horaentradapadrao
    return totalatrazo


def calcula_conducao(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal, Ausencia=""
    ).count()
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    salario = get_salario(idpessoal)
    valorconducao = salario[0].ValeTransporte
    valetransporte = float(cartaoponto) * float(valorconducao)
    if cartaoponto > 0:
        if contracheque:
            contrachequeitens = get_contrachequeitens(
                contracheque[0].idContraCheque, "VALE TRANSPORTE", "C"
            )
            if contrachequeitens:
                if valetransporte == 0:
                    delete_contrachequeitens(
                        contracheque[0].idContraCheque, "VALE TRANSPORTE", "C"
                    )
                else:
                    altera_contracheque_itens(
                        contrachequeitens, valetransporte, "{}d".format(cartaoponto)
                    )
            else:
                if valetransporte > 0:
                    create_contracheque_itens(
                        "VALE TRANSPORTE",
                        valetransporte,
                        "{}d".format(cartaoponto),
                        "C",
                        contracheque[0].idContraCheque,
                    )
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, "VALE TRANSPORTE", "C")
    return valetransporte


def saldo_contracheque(idcontracheque):
    credito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if not debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    return totais


def lista_mensaalista_ativos():
    return facade.get_pessoal_mensalista_ativo()


def list_avulsos_ativo():
    return facade.get_pessoal_nao_mensalista_ativo()


def form_pagamento(
    request,
    c_form,
    c_idobj,
    c_url,
    c_view,
    idcartaoponto,
    mesreferencia,
    anoreferencia,
    idpessoal,
):
    data = dict()
    c_instance = None
    if c_view == "edita_cartaoponto":
        if c_idobj:
            c_instance = CartaoPonto.objects.get(idCartaoPonto=c_idobj)
    if request.method == "POST":
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
        calcula_horas_extras(mesreferencia, anoreferencia, idpessoal)
        calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
        contracheque = get_contrachequereferencia(
            mesreferencia, anoreferencia, idpessoal
        )
        data["html_adiantamento"] = busca_adiantamento(contracheque[0].idContraCheque)
        data["html_folha"] = html_folha(mesreferencia, anoreferencia)
        data["html_contracheque"] = html_contracheque(
            mesreferencia, anoreferencia, idpessoal
        )
        data["html_cartaoponto"] = html_cartaoponto(
            mesreferencia, anoreferencia, idpessoal
        )
        data["html_formccadianta"] = html_formccadianta(contracheque, request)
        data["html_formccitens"] = html_formccitens(contracheque, request)
        data["html_minutascontracheque"] = html_minutascontracheque(
            mesreferencia, anoreferencia, idpessoal
        )
        data["html_vales"] = html_vale(
            idpessoal, "mensalista", contracheque[0].idContraCheque
        )
    else:
        form = c_form(instance=c_instance)
    context = {
        "form": form,
        "c_idobj": c_idobj,
        "c_url": c_url,
        "c_view": c_view,
        "idcartaoponto": idcartaoponto,
        "idcategoriaveiculo": request.GET.get("idcategoriaveiculo"),
    }
    data["html_form"] = render_to_string(
        "pagamentos/formpagamento.html", context, request=request
    )
    c_return = JsonResponse(data)
    return c_return


def print_recibo(idrecibo):
    reciboitens = []
    recibo = Recibo.objects.get(idRecibo=idrecibo)
    colaborador = Pessoal.objects.get(idPessoal=recibo.idPessoal_id)
    conta_colaborador = ContaPessoal.objects.filter(idPessoal=recibo.idPessoal_id)
    minutaitens = ReciboItens.objects.filter(idRecibo_id=idrecibo).annotate(
        idMinuta=F("idMinutaItens_id__idMinuta_id"),
        DataMinuta=F("idMinutaItens_id__idMinuta_id__DataMinuta"),
        Minuta=F("idMinutaItens_id__idMinuta_id__Minuta"),
        Cliente=F("idMinutaItens_id__idMinuta_id__idCliente__Fantasia"),
        Descricao=F("idMinutaItens_id__Descricao"),
        Valor=F("idMinutaItens_id__Valor"),
        ValorBase=F("idMinutaItens_id__ValorBase"),
    )
    for itens in minutaitens:
        motorista = MinutaColaboradores.objects.filter(
            Cargo="MOTORISTA", idMinuta_id=itens.idMinuta
        )
        if motorista:
            motorista_nome = motorista[0].idPessoal
        else:
            motorista_nome = ""
        if itens.Descricao == "AJUDANTE":
            reciboitens.append(
                {
                    "Data": itens.DataMinuta,
                    "Minuta": itens.Minuta,
                    "Cliente": itens.Cliente,
                    "Descricao": itens.Descricao,
                    "Valor": itens.ValorBase,
                    "Motorista": motorista_nome,
                }
            )
        else:
            reciboitens.append(
                {
                    "Data": itens.DataMinuta,
                    "Minuta": itens.Minuta,
                    "Cliente": itens.Cliente,
                    "Descricao": itens.Descricao,
                    "Valor": itens.Valor,
                    "Motorista": motorista_nome,
                }
            )
    vales = Vales.objects.filter(idRecibo_id=idrecibo)
    contexto = {
        "recibo": recibo,
        "colaborador": colaborador,
        "reciboitens": reciboitens,
        "vales": vales,
        "conta_colaborador": conta_colaborador,
    }
    return contexto


def html_saldo_avulso(datainicial, datafinal):
    """
    utiliza a 'get_saldo_pagameto_avulso' para carregar as variáveis de saldo dos colaboradores que não são
    considerados mensalistas, conforme período definido pelo usuário. E retorna um 'render_to_string', do template
    'pagamentos/saldavulso.html'
    :param datainicial:
    :param datafinal:
    :return: render_to_string através da variável c_return
    """
    saldo, saldototal, saldovales, totalselect = get_saldo_pagamento_avulso(
        datainicial, datafinal
    )
    context = {
        "saldo": saldo,
        "saldototal": saldototal,
        "saldovales": saldovales,
        "totalselect": totalselect,
        "datainicial": datainicial,
        "datafinal": datafinal,
    }
    c_return = render_to_string("pagamentos/saldoavulso.html", context)
    return c_return
