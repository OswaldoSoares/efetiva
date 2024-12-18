import calendar
import datetime
import locale
import os

from dateutil.relativedelta import relativedelta
from decimal import Decimal, ROUND_HALF_UP
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import DecimalField, ExpressionWrapper, F, Max, Min, Sum
from django.http import JsonResponse
from django.template.loader import render_to_string
from core.constants import MESES
from core.tools import gerar_data_html, primeiro_e_ultimo_dia_do_mes
from despesas.models import Multas
from minutas.facade import nome_curto, nome_curto_underscore
from minutas.models import MinutaColaboradores, MinutaItens
from pessoas.classes import Colaborador
from pessoas.forms import CadastraContraChequeItens
from pessoas.models import Agenda, CartaoPonto, ContaPessoal, ContraCheque
from pessoas.models import ContraChequeItens, Pessoal, Salario, Vales


from pessoas.facade import (
    get_contra_cheque_mes_ano_pagamento,
    get_contra_cheque_mes_ano_adiantamento,
    get_colaborador,
    create_contexto_contra_cheque_colaborador,
    get_vales_colaborador,
    update_contra_cheque_obs,
)
from website.facade import (
    DiasFeriados,
    Feriados,
    converter_mes_ano,
    extremos_mes,
    busca_arquivo_descricao,
)
from website.models import FileUpload, Parametros

from pagamentos.forms import CadastraCartaoPonto, FormAgenda
from pagamentos.models import FolhaPagamento, Recibo, ReciboItens
from pagamentos import html_data

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


def create_contexto_meses_pagamento() -> dict:
    locale.setlocale(locale.LC_TIME, "pt_BR.UTF-8")
    hoje = datetime.datetime.today()
    meses = [
        (hoje - relativedelta(months=i)).strftime("%B/%Y") for i in range(3)
    ]
    return {"meses": meses}


def obter_itens_contra_cheque(contra_cheques_itens, id_contra_cheque):
    return {
        item
        for item in contra_cheques_itens
        if item.idContraCheque_id == id_contra_cheque
    }


def calcular_saldo_contra_cheque(contra_cheque_itens):
    return sum(
        item.Valor if item.Registro == "C" else -item.Valor
        for item in contra_cheque_itens
    )


def processar_folha_pagamento(
    colaboradores, contra_cheques, contra_cheques_itens, descricao
):
    saldo_por_colaborador = {}
    for colaborador in colaboradores:
        contra_cheque_colaborador = {
            item
            for item in contra_cheques
            if item.idPessoal_id == colaborador.idPessoal
        }
        if contra_cheque_colaborador:
            cheque = next(iter(contra_cheque_colaborador))

            contra_cheque_itens = obter_itens_contra_cheque(
                contra_cheques_itens, cheque.idContraCheque
            )

            saldo = calcular_saldo_contra_cheque(contra_cheque_itens)
            saldo_por_colaborador[colaborador.idPessoal] = {
                "nome": colaborador.Nome,
                "nome_curto": nome_curto(colaborador.Nome),
                descricao: saldo,
            }
        else:
            saldo_por_colaborador[colaborador.idPessoal] = {
                "nome": colaborador.Nome,
                "nome_curto": nome_curto(colaborador.Nome),
                descricao: Decimal(0.00),
            }
    return saldo_por_colaborador


def saldo_contra_cheques_de_colaboradores(colaboradores, descricao, mes, ano):
    id_colaboradores_list = [item.idPessoal for item in colaboradores]
    contra_cheques = set(
        ContraCheque.objects.filter(
            idPessoal_id__in=id_colaboradores_list,
            MesReferencia=MESES.get(mes),
            AnoReferencia=ano,
            Descricao=descricao,
        )
    )

    id_contra_cheques_list = [item.idContraCheque for item in contra_cheques]
    contra_cheques_itens = set(
        ContraChequeItens.objects.filter(
            idContraCheque_id__in=id_contra_cheques_list
        )
    )

    return processar_folha_pagamento(
        colaboradores, contra_cheques, contra_cheques_itens, descricao
    )


def unir_saldo_contra_cheque_pagamento_e_adiantamento(
    colaboradores, dict_pagamento, dict_adiantamento
):
    result = {}
    for colaborador, valores_pagamento in dict_pagamento.items():
        if colaborador in dict_adiantamento:
            result[colaborador] = {
                "nome": valores_pagamento["nome"],
                "nome_curto": valores_pagamento["nome_curto"],
                "pagamento": valores_pagamento["PAGAMENTO"],
                "adiantamento": dict_adiantamento[colaborador]["ADIANTAMENTO"],
            }
        else:
            result[colaborador] = {
                "nome": valores_pagamento["nome"],
                "nome_curto": valores_pagamento["nome_curto"],
                "pagamento": valores_pagamento["PAGAMENTO"],
                "adiantamento": Decimal("0"),
            }

    for colaborador, valores_adiantamento in dict_adiantamento.items():
        if colaborador not in result:
            result[colaborador] = {
                "nome": valores_pagamento["nome"],
                "nome_curto": valores_pagamento["nome_curto"],
                "pagamento": Decimal("0"),
                "adiantamento": valores_adiantamento["ADIANTAMENTO"],
            }

    return result


def get_salarios_grupo_colaboradores(colaboradores):
    id_colaboradores_list = [item.idPessoal for item in colaboradores]
    return set(Salario.objects.filter(idPessoal_id__in=id_colaboradores_list))


def adicionar_info_folha(folha, salarios) -> dict:
    for id_pessoal in folha:
        salario = {
            item for item in salarios if item.idPessoal_id == id_pessoal
        }
        valor = next(iter(salario)).Salario if salario else Decimal(0.00)
        folha[id_pessoal]["adiantamento"] = folha[id_pessoal][
            "adiantamento"
        ] or (valor / 100 * 40)
        folha[id_pessoal]["pagamento"] = (
            folha[id_pessoal]["pagamento"] or valor
        )
        folha[id_pessoal]["salario"] = valor

    return folha


def get_totais_folha(folha: dict) -> dict:
    soma = {}
    soma["adiantamento"] = sum(info["adiantamento"] for info in folha.values())
    soma["pagamento"] = sum(info["pagamento"] for info in folha.values())
    soma["saldo"] = soma["adiantamento"] + soma["pagamento"]

    return soma


def create_contexto_folha_pagamento(request):
    meses_invertido = {v: k for k, v in MESES.items()}
    mes, ano = request.GET.get("mes_ano").split("/")
    mes = meses_invertido.get(mes)
    primeiro_e_ultimo = primeiro_e_ultimo_dia_do_mes(int(mes), int(ano))

    colaboradores = Pessoal.objects.filter(
        TipoPgto="MENSALISTA", DataAdmissao__lte=primeiro_e_ultimo[1]
    ).exclude(DataDemissao__lte=primeiro_e_ultimo[0])
    pagamento = saldo_contra_cheques_de_colaboradores(
        colaboradores, "PAGAMENTO", mes, ano
    )
    adiantamento = saldo_contra_cheques_de_colaboradores(
        colaboradores, "ADIANTAMENTO", mes, ano
    )

    folha_sem_salarios = unir_saldo_contra_cheque_pagamento_e_adiantamento(
        colaboradores, pagamento, adiantamento
    )
    salarios = get_salarios_grupo_colaboradores(colaboradores)
    folha = adicionar_info_folha(folha_sem_salarios, salarios)
    totais = get_totais_folha(folha)

    mensagem = f"O mês {mes}/{ano} foi selecionado"

    return {
        "folha": folha,
        "mes": mes,
        "ano": ano,
        "totais": totais,
        "mensagem": mensagem,
    }


def folha_pagamento_html_data(request, contexto):
    data = {}
    html_functions = [
        html_data.html_card_colaboradores,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def gerar_cartao_de_ponto_do_colaborador(colaborador, mes, ano):
    id_pessoal = colaborador.id_pessoal
    admissao = colaborador.dados_profissionais.data_admissao
    demissao = colaborador.dados_profissionais.data_demissao
    vale_transporte = colaborador.salarios.salarios.ValeTransporte
    feriados = DiasFeriados().feriados
    primeiro_dia, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)

    def is_weekend(day):
        return day.weekday() in {5, 6}

    registros = []

    for dia in (
        primeiro_dia + relativedelta(days=i)
        for i in range((ultimo_dia - primeiro_dia).days + 1)
    ):
        obj = {
            "Dia": dia,
            "Entrada": "07:00",
            "Saida": "17:00",
            "Remunerado": True,
            "idPessoal_id": id_pessoal,
        }

        if dia.date() < admissao or (demissao and dia.date() > demissao):
            obj["Ausencia"] = "-------"
            obj["Remunerado"] = False
            obj["Conducao"] = False
        elif dia in feriados:
            obj["Ausencia"] = "FERIADO"
            obj["Conducao"] = False
        elif is_weekend(dia):
            obj["Ausencia"] = "SABADO" if dia.weekday() == 5 else "DOMINGO"
            obj["Conducao"] = False
        else:
            obj["Ausencia"] = ""
            obj["Conducao"] = vale_transporte > Decimal(0.00)

        registros.append(CartaoPonto(**obj))

    return CartaoPonto.objects.bulk_create(registros)


def obter_cartao_de_ponto_do_colaborador(colaborador, mes, ano):
    id_pessoal = colaborador.id_pessoal
    primeiro_dia, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)

    cartao_ponto = CartaoPonto.objects.filter(
        Dia__range=[primeiro_dia, ultimo_dia], idPessoal=id_pessoal
    )

    return cartao_ponto or gerar_cartao_de_ponto_do_colaborador(
        colaborador, mes, ano
    )


def create_contexto_colaborador(request):
    id_pessoal = request.GET.get("id_pessoal")
    mes = int(request.GET.get("mes"))
    ano = int(request.GET.get("ano"))
    colaborador = Colaborador(id_pessoal)
    salario = colaborador.salarios.salarios.Salario
    vale_transporte = colaborador.salarios.salarios.ValeTransporte
    primeiro_dia, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)

    cartao_ponto = obter_cartao_de_ponto_do_colaborador(colaborador, mes, ano)

    verifica_feriados(cartao_ponto, mes, ano)
    minutas = get_minutas_periodo_contra_cheque(
        id_pessoal, primeiro_dia, ultimo_dia
    )
    vales = get_vales_colaborador(id_pessoal)
    atualiza_cartao_ponto_transporte(cartao_ponto, vale_transporte)
    atualiza_cartao_ponto_minutas(cartao_ponto, minutas)
    cartao_ponto = obter_cartao_de_ponto_do_colaborador(colaborador, mes, ano)
    #  atualiza_itens_contra_cheque_pagamento(
    #  colaborador, cartao_ponto, minutas, salario, vale_transporte, mes, ano
    #  )
    contexto = {
        "colaborador": colaborador,
        "nome_curto": nome_curto(colaborador.nome),
        "nome_underscore": nome_curto_underscore(colaborador.nome),
        "idpessoal": id_pessoal,
        "cartao_ponto": cartao_ponto,
        "vales": vales,
    }
    #  agenda = contexto_agenda_colaborador(idpessoal, mes_ano)
    #  contexto.update(agenda)
    return contexto


class FolhaContraCheque:
    def __init__(self, _mes, _ano):
        self.ano = _ano
        self.funcionarios = self.get_funcionarios(_mes, _ano)
        self.mes = _mes
        self.paga = False
        self.total_adiantamento = self.get_total_adiantamento(
            self.funcionarios
        )
        self.total_pagamento = self.get_total_pagamento(self.funcionarios)

    @staticmethod
    def get_funcionarios(_mes, _ano):
        _pdm, _udm = extremos_mes(_mes, _ano)
        _func = Pessoal.objects.filter(
            TipoPgto="MENSALISTA", DataAdmissao__lte=_udm
        ).exclude(DataDemissao__lte=_pdm)
        lista = dict()
        for itens in _func:
            v_salario_base = salario_base(itens.idPessoal)
            lista[nome_curto(itens.Nome)] = {
                "idpessoal": itens.idPessoal,
                "nome_curto": nome_curto(itens.Nome),
                "salario_base": v_salario_base,
                "adiantamento": v_salario_base * 40 / 100,
                "saldo_mes": get_saldo_folha(itens.idPessoal, _mes, _ano),
            }
        return lista

    @staticmethod
    def get_total_adiantamento(funcionarios):
        total_adiantamento = Decimal(0.00)
        for x in funcionarios:
            total_adiantamento += funcionarios[x]["adiantamento"]
        return total_adiantamento

    @staticmethod
    def get_total_pagamento(funcionarios):
        total_pagamento = Decimal(0.00)
        for x in funcionarios:
            total_pagamento += funcionarios[x]["saldo_mes"]
        return total_pagamento


def get_saldo_folha(idpessoal, mes, ano):
    var = dict()
    get_pessoa(idpessoal, var)
    var["mes"] = mes
    var["ano"] = ano
    cc = contra_cheque(var)
    contra_cheque_id = cc["idcontracheque"]
    vencimentos = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_id, Registro="C"
    ).aggregate(soma=Sum("Valor"))
    descontos = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_id, Registro="D"
    ).aggregate(soma=Sum("Valor"))
    if not vencimentos["soma"]:
        vencimentos["soma"] = Decimal(0.00)
    if not descontos["soma"]:
        descontos["soma"] = Decimal(0.00)
    saldo = vencimentos["soma"] - descontos["soma"]
    return saldo


def get_pessoa(idpessoal, var):
    colaborador = Pessoal.objects.filter(idPessoal=idpessoal)
    for x in colaborador:
        var["admissao"] = x.DataAdmissao
        var["bloqueado"] = x.StatusPessoal
        var["categoria"] = x.Categoria
        var["conducao"] = conducao(x.idPessoal)
        var["demissao"] = x.DataDemissao
        var["id_pessoal"] = x.idPessoal
        var["nome"] = x.Nome
        var["nome_curto"] = nome_curto(x.Nome)
        var["nome_curto_u"] = nome_curto_underscore(x.Nome)
        var["salario_base"] = salario_base(x.idPessoal)
    return var


def dias_falta(cartao_ponto):
    total_dias = 0
    for dia in cartao_ponto:
        if dia["Ausencia"] == "FALTA" and dia["Alteracao"] == "ROBOT":
            total_dias += 1
    return total_dias


def dias_remunerado(cartao_ponto, ultimo_dia):
    total_dias = 0
    for dia in cartao_ponto:
        if dia.Remunerado:
            total_dias += 1
    if ultimo_dia.day == 31:
        total_dias -= 1
    if ultimo_dia.day == 29:
        total_dias += 1
    if ultimo_dia.day == 28:
        total_dias += 2
    return total_dias


def dias_transporte(cartao_ponto):
    total_dias = 0
    for dia in cartao_ponto:
        if dia.Conducao:
            total_dias += 1
    return total_dias


def dias_carro_empresa(cartao_ponto):
    total_dias = 0
    for dia in cartao_ponto:
        if dia.CarroEmpresa:
            total_dias += 1
    return total_dias


def dias_trabalhado(cartao_ponto):
    total_dias = 0
    for dia in cartao_ponto:
        if dia.Ausencia == "":
            total_dias += 1
    return total_dias


def cartao_ponto(var):
    # Revisão Inicio - 10/01/2023
    cartao_de_ponto = CartaoPonto.objects.filter(
        Dia__range=[var["primeiro_dia"], var["ultimo_dia"]],
        idPessoal=var["id_pessoal"],
    ).values(
        "idPessoal",
        "Dia",
        "Entrada",
        "Saida",
        "Conducao",
        "Remunerado",
        "CarroEmpresa",
    )
    if not cartao_de_ponto:
        create_cartao_ponto(
            var["id_pessoal"],
            var["primeiro_dia"],
            var["ultimo_dia"],
            var["admissao"],
            var["demissao"],
            var,
        )
    # Revisão Final - 10/01/2023
    idpessoal = var["id_pessoal"]
    pdm = var["primeiro_dia"]
    udm = var["ultimo_dia"]
    adm = var["admissao"]
    dem = var["demissao"]
    cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
    if not cp:
        create_cartao_ponto(idpessoal, pdm, udm, adm, dem, var)
    else:
        var["cartao_ponto"] = cp
        # BUG
        # update_cartao_ponto(var)
    cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
    verifica_falta(cp)
    cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
    lista = [
        {
            "idcartaoponto": x.idCartaoPonto,
            "alteracao": x.Alteracao,
            "ausencia": x.Ausencia,
            "dia": x.Dia,
            "entrada": x.Entrada,
            "saida": x.Saida,
            "transporte": x.Conducao,
            "remunerado": x.Remunerado,
            "carro_empresa": x.CarroEmpresa,
        }
        for x in cp
    ]
    return lista


def contra_cheque(var: dict) -> dict:
    """Retorna dados do contra cheque.

    Args:
        var (dict): Um dicionario com variáveis

    Returns:
        dict: Um dicionario contendo as informação do contra cheque, referente ao
        funcionário, mês e ano selecionados.
    """
    idpessoal = var["id_pessoal"]
    mes = meses[int(var["mes"]) - 1]
    ano = var["ano"]
    contra_cheque = ContraCheque.objects.filter(
        idPessoal=idpessoal, MesReferencia=mes, AnoReferencia=ano
    ).values("idContraCheque", "Valor", "Pago")
    if not contra_cheque:
        create_contra_cheque(idpessoal, mes, ano)
        contra_cheque = ContraCheque.objects.filter(
            idPessoal=idpessoal, MesReferencia=mes, AnoReferencia=ano
        ).values("idContraCheque", "Valor", "Pago")
    dict_contra_cheque = {
        "idpessoal": idpessoal,
        "idcontracheque": contra_cheque[0]["idContraCheque"],
        "valor": contra_cheque[0]["Valor"],
        "pago": contra_cheque[0]["Pago"],
    }
    return dict_contra_cheque


def create_contra_cheque(idpessoal, mes, ano):
    v_salario = Salario.objects.get(idPessoal=idpessoal)
    obj = ContraCheque()
    obj.MesReferencia = mes
    obj.AnoReferencia = ano
    obj.Valor = v_salario.Salario
    obj.idPessoal_id = idpessoal
    obj.save()


def contra_cheque_itens(var):
    contra_cheque_id = var["id_contra_cheque"]
    salario_base = var["salario_base"]
    dias_remunerado = var["dias_remunerado"]
    dias_transporte = var["dias_transporte"]
    dias_carro_empresa = var["dias_carro_empresa"]
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_id, Descricao="SALARIO"
    )
    if not contra_cheque_itens:
        create_contra_cheque_itens(
            contra_cheque_id, "SALARIO", salario_base, "C", "30d", "0"
        )
    if dias_remunerado < 32:
        contra_cheque_itens = ContraChequeItens.objects.filter(
            idContraCheque=contra_cheque_id, Descricao="SALARIO"
        )
        if dias_remunerado == int(
            datetime.datetime.strftime(var["ultimo_dia"], "%d")
        ):
            dias_remunerado = 30
        salario = salario_base / 30 * int(dias_remunerado)
        if contra_cheque_itens:
            obj = contra_cheque_itens[0]
            obj.Valor = salario
            obj.Referencia = f"{dias_remunerado}d"
            obj.save(update_fields=["Valor", "Referencia"])
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_id, Descricao="VALE TRANSPORTE"
    )
    dias_transporte = dias_transporte - dias_carro_empresa
    if var["conducao"] == Decimal(0.00):
        dias_transporte = 0
    if dias_transporte > 0:
        conducao = var["conducao"] * int(dias_transporte)
        if contra_cheque_itens:
            obj = contra_cheque_itens[0]
            obj.Valor = conducao
            obj.Referencia = f"{dias_transporte}d"
            obj.save(update_fields=["Valor", "Referencia"])
        else:
            create_contra_cheque_itens(
                contra_cheque_id,
                "VALE TRANSPORTE",
                conducao,
                "C",
                f"{dias_transporte}d",
                "0",
            )
    else:
        if contra_cheque_itens:
            delete_contra_cheque_itens(
                contra_cheque_itens[0].idContraChequeItens
            )
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_id
    )
    lista = [
        {
            "idcontrachequeitens": x.idContraChequeItens,
            "descricao": x.Descricao,
            "valor": x.Valor,
            "registro": x.Registro,
            "referencia": x.Referencia,
        }
        for x in contra_cheque_itens
    ]
    return lista


def create_contra_cheque_itens(
    id: int, des: str, val: str, reg: str, ref: str, id_val: str
) -> None:
    """Salva novo item do contra cheque no Banco de Dados

    Args:
        id (int): id do Contra Cheque
        des (str): Descrição do Item
        val (str): Valor do Item
        reg (str): Registro do Item - Débito ou Crédito
        ref (str): Referencia do Item
    """
    obj = ContraChequeItens()
    obj.Descricao = des
    obj.Valor = val
    obj.Referencia = ref
    obj.Registro = reg
    obj.idContraCheque_id = id
    obj.Vales_id = id_val
    obj.save()


def salario_base(id_pessoal):
    v_qs = Salario.objects.filter(idPessoal=id_pessoal)
    salario = v_qs[0].Salario
    return salario


def conducao(id_pessoal):
    v_qs = Salario.objects.filter(idPessoal=id_pessoal)
    conducao = v_qs[0].ValeTransporte
    return conducao


class FolhaFuncionarios:
    def __init__(self, nome):
        self.vales = FolhaVale("oswaldo")


class FolhaVale:
    def __init__(self, nome):
        self.data = "2020-01-01"
        self.descricao = "VALE"
        self.nome = nome
        self.valor = Decimal(1.00)


def create_contexto_folha(mes_ano: str) -> JsonResponse:
    mes, ano = converter_mes_ano(mes_ano)
    folha = FolhaContraCheque(mes, ano).__dict__
    contexto = {"v_folha": folha}
    return contexto


def create_contexto_agenda(minutas, agenda):
    for x in agenda:
        minutas.append(
            {
                "idMinuta_id__DataMinuta": x.Dia,
                "idMinuta_id__Minuta": "",
                "idMinuta_id__idCliente__Fantasia": x.Descricao,
                "idMinuta_id__HoraInicial": datetime.time(0, 0),
                "idMinuta_id__HoraFinal": datetime.time(0, 0),
                "idPessoal": "",
                "Extra": "00:00",
            }
        )
    newlist = sorted(minutas, key=lambda d: d["idMinuta_id__DataMinuta"])
    return newlist


def create_contexto_funcionario(mes_ano, id) -> JsonResponse:
    var = dict()
    get_pessoa(id, var)
    var["mes"], var["ano"] = converter_mes_ano(mes_ano)
    var["primeiro_dia"], var["ultimo_dia"] = extremos_mes(
        var["mes"], var["ano"]
    )
    # TODO Necessário inverter as posições do _cartao_ponto e Minutas.
    # com minuta antes, não é calculado a hora extra
    _cartao_ponto = cartao_ponto(var)
    minutas = minutas_contra_cheque(var)
    var["dias_falta"] = dias_falta(_cartao_ponto)
    var["dias_remunerado"] = dias_remunerado(_cartao_ponto, var["ultimo_dia"])
    var["dias_transporte"] = dias_transporte(_cartao_ponto)
    var["dias_carro_empresa"] = dias_carro_empresa(_cartao_ponto)
    var["dias_trabalhado"] = dias_trabalhado(_cartao_ponto)
    _cc = contra_cheque(var)
    var["id_contra_cheque"] = _cc["idcontracheque"]
    atrazo(var)
    hora_extra(var)
    _adiantamento = False
    if busca_item_contra_cheque(var["id_contra_cheque"], "ADIANTAMENTO"):
        _adiantamento = True
    _cci = contra_cheque_itens(var)
    _tv, _td, _st = totais_contra_cheque(var)
    vales = vales_funcionario(var)
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    files = FileUpload.objects.filter(
        DescricaoUpload__startswith=f"{var['nome_curto_u']}_MES_{var['mes']}_{var['ano']}"
    )
    agenda = Agenda.objects.filter(
        idPessoal=var["id_pessoal"],
        Dia__range=[var["primeiro_dia"], var["ultimo_dia"]],
    )
    contexto = {
        "cartao_ponto": _cartao_ponto,
        "mes_ano": mes_ano,
        "nome": var["nome_curto"],
        "nome_underscore": var["nome_curto_u"],
        "idpessoal": var["id_pessoal"],
        "admissao": var["admissao"],
        "demissao": var["demissao"],
        "categoria": var["categoria"],
        "contra_cheque": _cc,
        "contra_cheque_itens": _cci,
        "vencimentos": _tv,
        "descontos": _td,
        "saldo": _st,
        "adiantamento": _adiantamento,
        "dias_admitido": dias_admitido(var),
        "dias_remunerado": var["dias_remunerado"],
        "dias_trabalhado": var["dias_trabalhado"],
        "dias_transporte": var["dias_transporte"] - var["dias_carro_empresa"],
        "valor_dia": var["salario_base"] / 30,
        "valor_hora": var["salario_base"] / 30 / 9,
        "valor_extra": var["salario_base"] / 30 / 9 * Decimal(1.5),
        "minutas": minutas,
        "vales": vales,
        "hoje": hoje,
        "files": files,
        "agenda": agenda,
    }
    return contexto


def create_data_seleciona_funcionario(request, contexto):
    data = dict()
    html_cartao_ponto(request, contexto, data)
    html_funcionario(request, contexto, data)
    html_contra_cheque(request, contexto, data)
    html_minutas(request, contexto, data)
    html_vales_pagamento(request, contexto, data)
    html_agenda(request, contexto, data)
    html_files_pagamento(request, contexto, data)
    html_vales(request, contexto, data)
    html_itens_agenda_pagamento(request, contexto, data)
    html_itens_contra_cheque(request, contexto, data)
    return JsonResponse(data)


# Excluir sem uso
def create_data_ausencia_falta(request, contexto):
    data = dict()
    html_card_folha_pagamento(request, contexto, data)
    html_cartao_ponto(request, contexto, data)
    html_funcionario(request, contexto, data)
    return JsonResponse(data)


def create_data_altera_horario(request, contexto):
    data = dict()
    html_cartao_ponto(request, contexto, data)
    html_contra_cheque(request, contexto, data)
    return JsonResponse(data)


# Excluir sem uso
def create_data_atestada(request, contexto):
    data = dict()
    html_cartao_ponto(request, contexto, data)
    html_funcionario(request, contexto, data)
    html_contra_cheque(request, contexto, data)
    return JsonResponse(data)


# Excluir sem uso
def create_data_altera_carro(request, contexto):
    data = dict()
    html_cartao_ponto(request, contexto, data)
    html_funcionario(request, contexto, data)
    html_contra_cheque(request, contexto, data)
    return JsonResponse(data)


def create_data_altera_cartao_ponto(request, contexto):
    data = dict()
    html_card_folha_pagamento(request, contexto, data)
    html_cartao_ponto(request, contexto, data)
    html_funcionario(request, contexto, data)
    return JsonResponse(data)


def create_data_cci(request, contexto):
    data = dict()
    html_contra_cheque(request, contexto, data)
    html_vales_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_vale(request, contexto):
    data = dict()
    html_vales(request, contexto, data)
    html_vales_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_seleciona_vale(request, contexto):
    data = dict()
    html_contra_cheque(request, contexto, data)
    html_vales_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_remove_vale(request, contexto):
    data = dict()
    html_vales_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_save_file(request, contexto):
    data = dict()
    html_files_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_delete_file(request, contexto):
    data = dict()
    html_files_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_gera_agenda(request, contexto):
    data = dict()
    html_agenda(request, contexto, data)
    html_itens_agenda_pagamento(request, contexto, data)
    return JsonResponse(data)


def create_data_delete_agenda(request, contexto):
    data = dict()
    html_itens_agenda_pagamento(request, contexto, data)
    return JsonResponse(data)


def nome_arquivo(_nome_curto, _mes_ano, _tipo):
    _mes, _ano = converter_mes_ano(_mes_ano)
    if _tipo == "adiantamento":
        _tipo_file = "ADIANTAMENTO"
    elif _tipo == "contracheque":
        _tipo_file = "CONTRA-CHEQUE"
    else:
        _tipo_file = "DIVERSOS"
    lista = []
    files = FileUpload.objects.filter(
        DescricaoUpload__startswith=f"{_nome_curto}_MES_{_mes}_{_ano}_{_tipo_file}"
    )
    seguencia = [itens + 1 for itens in range(99)]
    for itens in files:
        lista.append(int(itens.DescricaoUpload[-2:]))
    lista = sorted(lista)
    proxima_nota = str(list(set(seguencia) - set(lista))[0]).zfill(2)
    descricao = f"{_nome_curto}_MES_{_mes}_{_ano}_{_tipo_file}_{proxima_nota}"
    return descricao


def salva_arquivo(_arquivo, _descricao):
    msg = dict()
    ext_file = _arquivo.name.split(".")[-1]
    name_file = f"{_descricao}.{ext_file}"
    _arquivo.name = name_file
    obj = FileUpload()
    obj.DescricaoUpload = _descricao
    obj.uploadFile = _arquivo
    try:
        obj.save()
        msg["text_mensagem"] = "Arquivo enviado ao servidor com sucesso"
        msg["type_mensagem"] = "SUCESSO"
    except:
        msg["text_mensagem"] = "Falha ao salvar seu arquivo, tente novamente"
        msg["type_mensagem"] = "ERROR"


def exclui_arquivo(id):
    file = FileUpload.objects.filter(idFileUpload=id)
    if file:
        file.delete()


def vales_funcionario(_var):
    _id_pes = _var["id_pessoal"]
    vale = Vales.objects.filter(idPessoal=_id_pes, Pago=False)
    lista = []
    for x in vale:
        _checked = False
        if ContraChequeItens.objects.filter(Vales_id=x.idVales):
            _checked = True
        lista.append(
            {
                "idvales": x.idVales,
                "data": x.Data,
                "descricao": x.Descricao,
                "valor": x.Valor,
                "checked": _checked,
            }
        )
    return lista


def insere_vale_contra_cheque(idvale, idcontracheque):
    vale = Vales.objects.get(idVales=idvale)
    descricao = (
        f"{vale.Descricao} {datetime.datetime.strftime(vale.Data, '%d/%m/%Y')}"
    )
    create_contra_cheque_itens(
        idcontracheque,
        descricao,
        vale.Valor,
        "D",
        "",
        idvale,
    )


def delete_vales(_id_val):
    vale = Vales.objects.get(idVales=_id_val)
    vale.delete()


def dias_admitido(admissao, demissao):
    data_hoje = datetime.datetime.now().date()
    if demissao:
        total_dias = demissao - admissao
    else:
        total_dias = data_hoje - admissao
    return total_dias.days


def hora_extra(_var):
    _id_cc = _var["id_contra_cheque"]
    _tempo_extra, _acrescimo_extra = calcula_extras(_var)
    _obj = busca_item_contra_cheque(_id_cc, "HORA EXTRA")
    if _obj:
        if not f"{_obj.Valor:.2f}" == f"{_acrescimo_extra:.2f}":
            update_contra_cheque_itens(_obj, _tempo_extra, _acrescimo_extra)
        if _acrescimo_extra == 0:
            delete_contra_cheque_itens(_obj.idContraChequeItens)
    else:
        if _acrescimo_extra > 0:
            create_contra_cheque_itens(
                _id_cc, "HORA EXTRA", _acrescimo_extra, "C", _tempo_extra, "0"
            )


def atrazo(_var):
    _id_cc = _var["id_contra_cheque"]
    _tempo_atrazo, _desconto_atrazo = calcula_atrazo(_var)
    _obj = busca_item_contra_cheque(_id_cc, "ATRAZO")
    if _obj:
        if not f"{_obj.Valor:.2f}" == f"{_desconto_atrazo:.2f}":
            update_contra_cheque_itens(_obj, _tempo_atrazo, _desconto_atrazo)
        if _desconto_atrazo == 0:
            delete_contra_cheque_itens(_obj.idContraChequeItens)
    else:
        if _desconto_atrazo > 0:
            create_contra_cheque_itens(
                _id_cc, "ATRAZO", _desconto_atrazo, "D", _tempo_atrazo, "0"
            )


def delete_contra_cheque_itens(_id_cci):
    _cci = ContraChequeItens.objects.filter(idContraChequeItens=_id_cci)
    _cci.delete()


def update_contra_cheque_itens(_obj, _ref, _val: float):
    obj = _obj
    obj.Referencia = _ref
    obj.Valor = _val
    obj.save()


def totais_contra_cheque(_var):
    _id_cc = _var["id_contra_cheque"]
    _vencimentos = ContraChequeItens.objects.filter(
        idContraCheque=_id_cc, Registro="C"
    ).aggregate(soma=Sum("Valor"))
    _descontos = ContraChequeItens.objects.filter(
        idContraCheque=_id_cc, Registro="D"
    ).aggregate(soma=Sum("Valor"))
    if not _vencimentos["soma"]:
        _vencimentos["soma"] = Decimal(0.00)
    if not _descontos["soma"]:
        _descontos["soma"] = Decimal(0.00)
    _saldo = _vencimentos["soma"] - _descontos["soma"]
    return _vencimentos, _descontos, _saldo


def minutas_contra_cheque(_var):
    _pdm = _var["primeiro_dia"]
    _udm = _var["ultimo_dia"]
    minutas = MinutaColaboradores.objects.filter(
        idPessoal=_var["id_pessoal"],
        idMinuta_id__DataMinuta__range=(_pdm, _udm),
    ).exclude(idMinuta_id__StatusMinuta="ABERTA")
    lista = []
    lista_filtrada = []
    _he = datetime.timedelta(hours=7, minutes=0)
    _hs = datetime.timedelta(hours=17, minutes=0)
    _cp = CartaoPonto.objects.filter(
        Dia__range=[_pdm, _udm], idPessoal=_var["id_pessoal"]
    )
    if not _cp:
        create_cartao_ponto(
            _var["id_pessoal"],
            _var["primeiro_dia"],
            _var["ultimo_dia"],
            _var["admissao"],
            _var["demissao"],
            _var,
        )
    for x in minutas:
        _hez = datetime.timedelta(hours=0, minutes=0)
        _hi = x.idMinuta.HoraInicial
        _hi = datetime.timedelta(hours=_hi.hour, minutes=_hi.minute)
        if _hi < _he:
            _hez = _he - _hi
            _cp = CartaoPonto.objects.get(
                Dia=x.idMinuta.DataMinuta, idPessoal=_var["id_pessoal"]
            )
            obj = _cp
            obj.Entrada = x.idMinuta.HoraInicial
            if obj.Alteracao == "ROBOT":
                obj.save(update_fields=["Entrada"])
        _hsz = datetime.timedelta(hours=0, minutes=0)
        if x.idMinuta.HoraFinal:
            _hf = x.idMinuta.HoraFinal
            _hf = datetime.timedelta(hours=_hf.hour, minutes=_hf.minute)
            if _hf > _hs:
                _hsz = _hf - _hs
                _cp = CartaoPonto.objects.get(
                    Dia=x.idMinuta.DataMinuta, idPessoal=_var["id_pessoal"]
                )
                obj = _cp
                obj.Saida = x.idMinuta.HoraFinal
                if obj.Alteracao == "ROBOT":
                    obj.save(update_fields=["Saida"])
        extra = _hez + _hsz
        verifica_lista = next(
            (
                i
                for i, y in enumerate(lista)
                if y["minuta"] == x.idMinuta.Minuta
            ),
            None,
        )
        if verifica_lista == None:
            lista.append(
                {
                    "data_minuta": x.idMinuta.DataMinuta,
                    "minuta": x.idMinuta.Minuta,
                    "fantasia": x.idMinuta.idCliente.Fantasia,
                    "hora_inicial": x.idMinuta.HoraInicial,
                    "hora_final": x.idMinuta.HoraFinal,
                    "hora_extra": str(extra)[:-3].zfill(5),
                }
            )
    return lista


def create_vales(_des, _dat, _val, _par, _id_pes):
    if int(_par) > 0:
        for x in range(int(_par)):
            obj = Vales()
            obj.Data = _dat
            if int(_par) == 1:
                obj.Descricao = _des
            else:
                obj.Descricao = (
                    f"{_des} {str(x + 1).zfill(2)}/{_par.zfill(2)} PARCELADO"
                )
            obj.Valor = Decimal(_val) / int(_par)
            obj.idPessoal_id = _id_pes
            obj.save()
    return obj


def create_agenda(_des, _dat, _id_pes):
    if not _des == "":
        obj = Agenda()
        obj.Dia = _dat
        obj.Descricao = _des
        obj.idPessoal_id = _id_pes
        obj.save()


def update_agenda(_des, _dat, _id_age):
    agenda = Agenda.objects.get(idAgenda=_id_age)
    obj = agenda
    obj.Dia = _dat
    obj.Descricao = _des
    obj.save(update_fields=["Dia", "Descricao"])


def read_agenda(request, _id_age, _id_pes, _mes_ano):
    _var = dict()
    get_pessoa(_id_pes, _var)
    data = dict()
    agenda = Agenda.objects.filter(idAgenda=_id_age)
    contexto = {
        "agenda": agenda,
        "nome": _var["nome_curto"],
        "editar": True,
        "idpessoal": _var["id_pessoal"],
        "mes_ano": _mes_ano,
    }
    data["html_agenda_pagamento"] = render_to_string(
        "pagamentos/html_agenda.html", contexto, request=request
    )
    return JsonResponse(data)


def delete_agenda(_id_age):
    agenda = Agenda.objects.filter(idAgenda=_id_age)
    agenda.delete()


def cria_contexto_pagamentos():
    # formvales = CadastraVale()
    v_mes_ano = seleciona_mes_ano_folha()
    contexto = {
        # "formvales": formvales,
        "mes_ano": v_mes_ano,
    }
    return contexto


def update_cartao_ponto(_var):
    _cp = _var["cartao_ponto"]
    _adm = _var["admissao"]
    _dem = _var["demissao"]
    feriados = DiasFeriados().__dict__["feriados"]
    for x in _cp:
        cartaoponto = CartaoPonto.objects.get(idCartaoPonto=x.idCartaoPonto)
        obj = cartaoponto
        if x.Dia < _adm:
            if x.Ausencia != "-------":
                obj.Ausencia = "-------"
                obj.Conducao = False
                obj.Remunerado = False
                obj.Alteracao = "ROBOT"
                obj.Entrada = "07:00:00"
                obj.Saida = "17:00:00"
        else:
            if x.Ausencia == "-------":
                if x.Dia.weekday() == 5 or x.Dia.weekday() == 6:
                    obj.Ausencia = dias[x.Dia.weekday()]
                    obj.Conducao = False
                else:
                    obj.Ausencia = ""
                    obj.Conducao = True
                obj.Remunerado = True
            obj.Alteracao = "ROBOT"
            obj.Entrada = "07:00:00"
            obj.Saida = "17:00:00"
            if x.Dia in feriados and x.Ausencia != "FERIADO":
                obj.Ausencia = "FERIADO"
                obj.Alteracao = "ROBOT"
                obj.Conducao = False
                obj.Remunerado = True
                obj.Entrada = "07:00:00"
                obj.Saida = "17:00:00"
            if _var["conducao"] == Decimal(0.00):
                obj.Conducao = False
        if x.Ausencia == "FÉRIAS":
            obj.Conducao = False
            obj.Remunerado = False
            obj.Alteracao = "ROBOT"
            obj.Entrada = "07:00:00"
            obj.Saida = "17:00:00"
        if not _dem is None:
            if x.Dia > _dem:
                if obj.Ausencia != "-------":
                    obj.Ausencia = "-------"
                    obj.Conducao = False
                    obj.Remunerado = False
                    obj.Alteracao = "ROBOT"
                    obj.Entrada = "07:00:00"
                    obj.Saida = "17:00:00"
        obj.save(
            update_fields=[
                "Ausencia",
                "Alteracao",
                "Entrada",
                "Saida",
                "Conducao",
                "Remunerado",
            ]
        )


# Atualizada em 14/12/2023 - Manter
def altera_ausencia_falta(idcartaoponto, ausencia):
    registros_cartao_ponto = []
    if ausencia != "FERIAS":
        if ausencia == "FALTA":
            registros_cartao_ponto.append(
                CartaoPonto(
                    Ausencia="",
                    Alteracao="ROBOT",
                    Conducao=True,
                    Remunerado=True,
                    idCartaoPonto=idcartaoponto,
                )
            )
        else:
            registros_cartao_ponto.append(
                CartaoPonto(
                    Ausencia="FALTA",
                    Alteracao="MANUAL",
                    Conducao=False,
                    Remunerado=False,
                    idCartaoPonto=idcartaoponto,
                )
            )
        CartaoPonto.objects.bulk_update(
            registros_cartao_ponto,
            [
                "Ausencia",
                "Alteracao",
                "Conducao",
                "Remunerado",
            ],
        )


def falta_remunerada(idcartaoponto, remunerado):
    registros_cartao_ponto = []
    registros_cartao_ponto.append(
        CartaoPonto(
            Alteracao="MANUAL",
            Remunerado=False if remunerado == "True" else True,
            idCartaoPonto=idcartaoponto,
        )
    )
    CartaoPonto.objects.bulk_update(
        registros_cartao_ponto, ["Alteracao", "Remunerado"]
    )


def altera_carro_empresa(idcartaoponto, carro_empresa):
    registros_cartao_ponto = []
    registros_cartao_ponto.append(
        CartaoPonto(
            Alteracao="MANUAL",
            Conducao=True if carro_empresa == "True" else False,
            CarroEmpresa=False if carro_empresa == "True" else True,
            idCartaoPonto=idcartaoponto,
        )
    )
    CartaoPonto.objects.bulk_update(
        registros_cartao_ponto, ["Alteracao", "CarroEmpresa", "Conducao"]
    )


def verifica_falta(v_cartao_ponto):
    faltas = len(
        v_cartao_ponto.filter(Ausencia__exact="FALTA", Alteracao="ROBOT")
    )
    # for itens in v_cartao_ponto:
    #     if not itens.Ausencia == "-------":
    #         if not itens.Ausencia == "FÉRIAS":
    #             if itens.Dia.weekday() == 5 or itens.Dia.weekday() == 6:
    #                 obj = CartaoPonto.objects.get(idCartaoPonto=itens.idCartaoPonto)
    #                 obj.Remunerado = True
    #                 obj.save(update_fields=["Remunerado"])
    #             if itens.Ausencia == "FERIADO":
    #                 obj = CartaoPonto.objects.get(idCartaoPonto=itens.idCartaoPonto)
    #                 obj.Remunerado = True
    #                 obj.save(update_fields=["Remunerado"])
    if faltas > 0:
        for itens in v_cartao_ponto:
            if not itens.Ausencia == "-------":
                if not itens.Ausencia == "FÉRIAS":
                    if itens.Dia.weekday() == 5 or itens.Dia.weekday() == 6:
                        obj = CartaoPonto.objects.get(
                            idCartaoPonto=itens.idCartaoPonto
                        )
                        obj.Remunerado = False
                        obj.save(update_fields=["Remunerado"])
                        faltas -= 1
                        if faltas == 0:
                            break
        if faltas > 0:
            for itens in v_cartao_ponto:
                if not itens.Ausencia == "-------":
                    if not itens.Ausencia == "FÉRIAS":
                        if itens.Ausencia == "FERIADO":
                            obj = CartaoPonto.objects.get(
                                idCartaoPonto=itens.idCartaoPonto
                            )
                            obj.Remunerado = False
                            obj.save(update_fields=["Remunerado"])
                            faltas -= 1
                            if faltas == 0:
                                break


# TODO Melhorar código
def imprime_contra_cheque_pagamento(_id_cc, tipo):
    _cc = ContraCheque.objects.filter(idContraCheque=_id_cc)
    _var = dict()
    get_pessoa(_cc[0].idPessoal_id, _var)
    _banco = ContaPessoal.objects.filter(idPessoal=_var["id_pessoal"])
    _vc = False
    if len(_banco) > 1:
        _vc = True
    _mes = meses.index(_cc[0].MesReferencia) + 1
    _ano = _cc[0].AnoReferencia
    _var["mes"], _var["ano"] = _mes, _ano
    _var["primeiro_dia"], _var["ultimo_dia"] = extremos_mes(
        _var["mes"], _var["ano"]
    )
    # minutas = minutas_contra_cheque(_var)
    _carto_ponto = cartao_ponto(_var)
    minutas = select_minutas_contracheque(_mes, _ano, _cc[0].idPessoal_id)
    _var["dias_falta"] = dias_falta(_carto_ponto)
    _var["dias_remunerado"] = dias_remunerado(_carto_ponto, _var["ultimo_dia"])
    _var["dias_transporte"] = dias_transporte(_carto_ponto)
    _var["dias_carro_empresa"] = dias_carro_empresa(_carto_ponto)
    _var["id_contra_cheque"] = _id_cc
    # atrazo(_var)
    # hora_extra(_var)
    _cci = contra_cheque_itens(_var)
    _tv, _td, _st = totais_contra_cheque(_var)
    if tipo == "adian":
        credito = ContraChequeItens.objects.filter(
            idContraCheque=_id_cc, Descricao="ADIANTAMENTO", Registro="D"
        ).aggregate(Total=Sum("Valor"))
        debito = dict()
        debito["Total"] = Decimal("0.00")
    elif tipo == "transp":
        credito = ContraChequeItens.objects.filter(
            idContraCheque=_id_cc, Descricao="VALE TRANSPORTE", Registro="C"
        ).aggregate(Total=Sum("Valor"))
        debito = dict()
        debito["Total"] = Decimal("0.00")
    else:
        credito = ContraChequeItens.objects.filter(
            idContraCheque=_id_cc, Registro="C"
        ).aggregate(Total=Sum("Valor"))
        debito = ContraChequeItens.objects.filter(
            idContraCheque=_id_cc, Registro="D"
        ).aggregate(Total=Sum("Valor"))
        if debito["Total"] == None:
            debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    vales = vales_funcionario(_var)
    hoje = datetime.datetime.today()
    hoje = datetime.datetime.strftime(hoje, "%Y-%m-%d")
    colaborador = facade.get_pessoal(_cc[0].idPessoal_id)
    contrachequeitens = facade.get_contracheque_itens(_id_cc)
    lista_agenda_minuta = []
    agenda = Agenda.objects.filter(
        idPessoal=_var["id_pessoal"],
        Dia__range=[_var["primeiro_dia"], _var["ultimo_dia"]],
    )
    for x in agenda:
        lista_agenda_minuta.append({"dia": x.Dia, "descricao": x.Descricao})
    for x in minutas:
        lista_agenda_minuta.append(
            {
                "dia": x["idMinuta_id__DataMinuta"],
                "descricao": "minuta",
                "minuta": x["idMinuta_id__Minuta"],
                "cliente": x["idMinuta_id__idCliente__Fantasia"],
                "inicio": x["idMinuta_id__HoraInicial"],
                "final": x["idMinuta_id__HoraFinal"],
                "extra": x["Extra"],
            }
        )
    newlist = sorted(lista_agenda_minuta, key=lambda d: d["dia"])
    new_minutas = create_contexto_agenda(minutas, agenda)
    lista_multas = []
    for x in contrachequeitens:
        if x.Descricao[0:8] == "MULTA - ":
            multas = Multas.objects.filter(NumeroDOC=x.Descricao[8:])
            for y in multas:
                lista_multas.append(
                    {
                        "numero_doc": y.NumeroDOC,
                        "data": y.DataMulta,
                        "hora": y.HoraMulta,
                        "infracao": y.Infracao,
                        "local": y.Local,
                        "placa": y.idVeiculo.Placa,
                    }
                )
    contexto = {
        "contracheque": _cc,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
        "minutas": new_minutas,
        "salario_base": str(_var["salario_base"]),
        "cartao_ponto": _carto_ponto,
        "banco": _banco,
        "mais_banco": _vc,
        "multas": lista_multas,
    }
    return contexto


def calcula_extras(_var):
    _id_pes = _var["id_pessoal"]
    _sb = _var["salario_base"]
    _pdm = _var["primeiro_dia"]
    _udm = _var["ultimo_dia"]
    _cp = CartaoPonto.objects.filter(
        Dia__range=[_pdm, _udm], idPessoal=_id_pes
    )
    _hz = datetime.timedelta(hours=0, minutes=0)
    _te = _hz
    for x in _cp:
        _he = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
        _he = datetime.timedelta(hours=_he.hour, minutes=_he.minute)
        _hfe = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        _te += _he - _hfe if _hfe < _he else _hz
        _hs = datetime.datetime.strptime("17:00:00", "%H:%M:%S").time()
        _hs = datetime.timedelta(hours=_hs.hour, minutes=_hs.minute)
        _hfs = datetime.timedelta(hours=x.Saida.hour, minutes=x.Saida.minute)
        _te += _hfs - _hs if _hfs > _hs else _hz
    _vda = Decimal(_sb) / 30 / 9 / 60 / 60 * Decimal(1.5) * _te.seconds
    return _te, _vda


def calcula_atrazo(_var):
    """Calcula o tempo de atrazo do funcionário em um mês, referente a
       hora de entrada.
       Verifica o cartão de ponto dia após dia, se a hora de entrada do
       funcionário for maior que '07:00:00' adiciona no total de atrazo.

    Abreviaturas das variáveis:
        _id_pes: Variavel id do Funcionario
        _sb: Variavel salario base
        _pdm: Variavel primeiro dia do mês
        _udm: Variavel último dia do mês
        _cp: Variavel cartão de ponto do mês de pagamento
        _hz: Variavel hora zerada
        _ta: Variavel tempo de atrazo
        _he: Variavel hora de entrada (Hora que funcionário tem que entrar - '07:00:00')
        _hfe: Variavel hora que funcionário entrou

    Args:
        v_var (dict): dicionario de variáveis

    Returns:
        datetime.timedelta, decimal: Tempo e Valor a ser descontado no contra cheque
    """
    _id_pes = _var["id_pessoal"]
    _sb = _var["salario_base"]
    _pdm = _var["primeiro_dia"]
    _udm = _var["ultimo_dia"]
    _cp = CartaoPonto.objects.filter(
        Dia__range=[_pdm, _udm], idPessoal=_id_pes
    )
    _hz = datetime.timedelta(hours=0, minutes=0)
    _ta = _hz
    for x in _cp:
        _he = datetime.datetime.strptime("07:00:00", "%H:%M:%S").time()
        _he = datetime.timedelta(hours=_he.hour, minutes=_he.minute)
        _hfe = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        _ta += _hfe - _he if _hfe > _he else _hz
    _vda = Decimal(_sb) / 30 / 9 / 60 / 60 * _ta.seconds
    return _ta, _vda


def busca_item_contra_cheque(v_id: int, v_des: str):
    """Verifica se um item já existe no Banco de Dados

    Abreviaturas:
        v_cci: Variavel Contra Cheque Itens
        obj: object ContraChequeItens

    Args:
        v_id (int): idContraCheque
        v_des (str): Descrição do Item

    Returns:
        obj: ContraChequeItens ou None
    """
    obj = None
    v_cci = ContraChequeItens.objects.filter(
        idContraCheque=v_id, Descricao=v_des
    )
    if v_cci:
        obj = v_cci[0]
    return obj


def create_context_avulso():
    periodo = get_periodo_pagamento_avulsos()
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


def create_contexto_avulsos_a_receber(datainicial, datafinal):
    saldo = []
    saldo_total = 0
    saldo_vales = 0
    total_select = 0
    avulsos = (
        MinutaColaboradores.objects.filter(Pago=False)
        .exclude(idPessoal__TipoPgto="MENSALISTA")
        .values("idPessoal__Nome", "idPessoal_id")
        .distinct()
        .order_by("idPessoal")
    )
    for colaboradores in avulsos:
        colaborador = MinutaColaboradores.objects.filter(
            idPessoal__Nome=colaboradores["idPessoal__Nome"], Pago=False
        ).exclude(idMinuta__StatusMinuta="ABERTA")
        _banco = ContaPessoal.objects.filter(
            idPessoal=colaboradores["idPessoal_id"]
        )
        _vc = False
        if len(_banco) > 1:
            _vc = True
        saldo_colaborador = 0
        for itens in colaborador:
            if itens.Cargo == "AJUDANTE":
                base_valor = ExpressionWrapper(
                    F("Valor") / F("Quantidade"), output_field=DecimalField()
                )
                ajudante = MinutaItens.objects.values(
                    ValorAjudante=base_valor
                ).filter(
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
                        idMinuta_id__DataMinuta__range=[
                            datainicial,
                            datafinal,
                        ],
                    )
                    .exclude(Descricao="AJUDANTE")
                    .aggregate(ValorMotorista=Sum("Valor"))
                )
                if motorista["ValorMotorista"]:
                    saldo_colaborador += motorista["ValorMotorista"]
                    saldo_total += motorista["ValorMotorista"]
        if saldo_colaborador > 0:
            saldo.append(
                {
                    "Nome": colaboradores["idPessoal__Nome"],
                    "Nome_Curto": nome_curto(colaboradores["idPessoal__Nome"]),
                    "idPessoal": colaborador[0].idPessoal_id,
                    "Saldo": f"{saldo_colaborador}",
                    "banco": _banco,
                    "mais_banco": _vc,
                }
            )
    return saldo, saldo_total, saldo_vales, total_select


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
    data["html_minutas"] = html_minutasavulso(
        datainicial, datafinal, idpessoal
    )
    data["html_recibos"] = html_recibo_avulso(
        datainicial, datafinal, idpessoal
    )
    c_return = JsonResponse(data)
    return c_return


def create_pagamento_avulso(datainicial, datafinal, idpessoal, zerado):
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
    new_idrecibo = 0
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
        if total_recibo > 0.00:
            numero_recibo = Recibo.objects.aggregate(Maior=Max("Recibo"))
            if not numero_recibo["Maior"]:
                numero_recibo = 1431
            else:
                numero_recibo = numero_recibo["Maior"] + 1
            obj = Recibo()
            obj.Recibo = numero_recibo
            obj.DataRecibo = datetime.date.today()
            if zerado:
                obj.ValorRecibo = Decimal(0.00)
            else:
                obj.ValorRecibo = total_recibo
            obj.idPessoal_id = idpessoal
            obj.save()
            new_idrecibo = obj.idRecibo
            for itens in recibo:
                obj = ReciboItens()
                obj.idRecibo_id = new_idrecibo
                obj.idMinutaItens_id = itens["idMinutaItens"]
                obj.save()
            for itens in minutas:
                obj = itens
                obj.Pago = True
                obj.idRecibo_id = new_idrecibo
                obj.save(update_fields=["Pago", "idRecibo_id"])
    data = dict()
    data["html_minutas"] = html_minutasavulso(
        datainicial, datafinal, idpessoal
    )
    data["html_recibos"] = html_recibo_avulso(
        datainicial, datafinal, idpessoal
    )
    data["numero_recibo"] = new_idrecibo
    c_return = JsonResponse(data)
    return c_return


def create_contexto_itens_pagamento_avulso(datainicial, datafinal, idpessoal):
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
                            "Motorista": "",
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
                            "Motorista": "",
                            "idMinutaItens": x.idMinutaItens,
                        }
                    )
    data = dict()
    data["html_minutas"] = html_minutasavulso(
        datainicial, datafinal, idpessoal
    )
    data["html_recibos"] = html_recibo_avulso(
        datainicial, datafinal, idpessoal
    )
    c_return = JsonResponse(data)
    return c_return


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if (
            int(mesreferencia) >= admissao.month
            or int(anoreferencia) > admissao.year
        ):
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
                        contracheque_itens,
                        salario,
                        "{}d".format(dias_mes).zfill(2),
                    )
                else:
                    altera_contracheque_itens(
                        contracheque_itens, salario[0].Salario, "30d"
                    )


# TODO Função valido para as duas versões
def create_contracheque_itens(
    descricao, valor, referencia, registro, idcontracheque
):
    if float(valor) > 0:
        saldo = saldo_contracheque(idcontracheque)
        if float(valor) <= float(saldo["Liquido"]) or descricao == "SALARIO":
            if not busca_contrachequeitens(
                idcontracheque, descricao, registro
            ):
                obj = ContraChequeItens()
                obj.Descricao = descricao
                obj.Valor = valor
                obj.Referencia = referencia
                obj.Registro = registro
                obj.idContraCheque_id = idcontracheque
                obj.save()


def busca_feriados(mesreferencia, anoreferencia):
    lista_feriados = Feriados("Lista", "Feriado")
    lista_feriados = lista_feriados.__dict__["feriados"]
    dias_feriado_mes = []
    for x in lista_feriados:
        feriado = datetime.datetime.strptime(x, "%Y-%m-%d")
        if (
            int(anoreferencia) == feriado.year
            and int(mesreferencia) == feriado.month
        ):
            dias_feriado_mes.append(feriado.day)
    return dias_feriado_mes


# TODO Função será excluida após refatoração 24-04-2022
def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    dias_feriado_mes = busca_feriados(mesreferencia, anoreferencia)
    if not busca_cartaoponto_referencia(
        mesreferencia, anoreferencia, idpessoal
    ):
        if int(anoreferencia) >= admissao.year:
            if (
                int(mesreferencia) >= admissao.month
                or int(anoreferencia) > admissao.year
            ):
                admissao = datetime.datetime(
                    admissao.year, admissao.month, admissao.day
                )
                referencia = calendar.monthrange(
                    int(anoreferencia), int(mesreferencia)
                )
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
        if (
            int(mesreferencia) == admissao.month
            and int(anoreferencia) == admissao.year
        ):
            confere_admissao(idpessoal, admissao)


def confere_admissao(idpessoal, admissao):
    cartaoponto = busca_cartaoponto_referencia(
        admissao.month, admissao.year, idpessoal
    )
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


def exclui_recibo(idrecibo):
    Vales.objects.filter(idRecibo_id=idrecibo).update(
        idRecibo_id=None, Pago=False
    )
    MinutaColaboradores.objects.filter(idRecibo_id=idrecibo).update(
        idRecibo_id=None, Pago=False
    )
    reciboitens = ReciboItens.objects.filter(idRecibo_id=idrecibo)
    if reciboitens:
        reciboitens.delete()
    recibo = get_recibo_id(idrecibo)
    if recibo:
        recibo.delete()


def create_data_form_paga_recibo_colaborador(request, contexto):
    data = dict()
    html_form_paga_recibo_colaborador(request, contexto, data)
    return JsonResponse(data)


def html_form_paga_recibo_colaborador(request, contexto, data):
    data["html_form_paga_recibo_colaborador"] = render_to_string(
        "pagamentos/html_form_paga_recibo_colaborador.html",
        contexto,
        request=request,
    )
    return data


def paga_recibo_colabotador(idrecibo, datapgto):
    recibo = Recibo.objects.get(idRecibo=idrecibo)
    obj = recibo
    obj.StatusRecibo = "PAGO"
    obj.DataPagamento = datetime.datetime.strptime(datapgto, "%Y-%m-%d")
    obj.save(update_fields=["StatusRecibo", "DataPagamento"])


def create_data_estorna_recibo_colaborador(request, contexto):
    pass


def create_data_html_recibos_colaborador(request, contexto):
    data = dict()
    # BUG data["html_minutas"] = html_minutasavulso(datainicial, datafinal, idpessoal)
    # BUG data["html_recibos"] = html_recibo_avulso(datainicial, datafinal, idpessoal)
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
            idContraCheque=idcontracheque,
            Descricao=descricao,
            Registro=registro,
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
        MesReferencia=mesreferencia,
        AnoReferencia=anoreferencia,
        idPessoal=idpessoal,
    )
    return contracheque


def busca_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
    )
    return contrachequeitens


def busca_adiantamento(idcontracheque):
    if ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao="ADIANTAMENTO", Registro="D"
    ):
        return True
    else:
        return False


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


# TODO EXCLUIR função não está mais sendo usada.
def calcula_faltas(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    demissao = colaborador[0].DataDemissao
    mes_dias = 30
    if (
        int(anoreferencia) == admissao.year
        and int(mesreferencia) == admissao.month
    ):
        mes_dias -= admissao.day - 1
        dia = admissao
    if demissao:
        if (
            int(anoreferencia) == demissao.year
            and int(mesreferencia) == demissao.month
        ):
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
    contracheque = get_contrachequereferencia(
        mesreferencia, anoreferencia, idpessoal
    )
    contrachequeitens = get_contrachequeitens(
        contracheque[0].idContraCheque, "SALARIO", "C"
    )
    altera_contracheque_itens(
        contrachequeitens, salario, f"{mes_dias-faltas}d"
    )


def calcula_horas_extras(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalextra = total_horas_extras(mesreferencia, anoreferencia, idpessoal)
    horazero = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraextra = (
        float(salario[0].Salario) / 30 / 9 / 60 / 60 * 1.5 * totalextra.seconds
    )
    contracheque = get_contrachequereferencia(
        mesreferencia, anoreferencia, idpessoal
    )
    if totalextra > horazero:
        if contracheque:
            contrachequeitens = get_contrachequeitens(
                contracheque[0].idContraCheque, "HORA EXTRA", "C"
            )
            if contrachequeitens:
                altera_contracheque_itens(
                    contrachequeitens, valorhoraextra, totalextra
                )
            else:
                if valorhoraextra > 0:
                    create_contracheque_itens(
                        "HORA EXTRA",
                        valorhoraextra,
                        totalextra,
                        "C",
                        contracheque[0].idContraCheque,
                    )
    return totalextra


def total_horas_extras(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    totalextra = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horaentradapadrao = datetime.datetime.strptime(
            "07:00:00", "%H:%M:%S"
        ).time()
        horaentradapadrao = datetime.timedelta(
            hours=horaentradapadrao.hour, minutes=horaentradapadrao.minute
        )
        horaentradareal = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        if horaentradareal < horaentradapadrao:
            totalextra += horaentradapadrao - horaentradareal
        horasaidapadrao = datetime.datetime.strptime(
            "17:00:00", "%H:%M:%S"
        ).time()
        horasaidapadrao = datetime.timedelta(
            hours=horasaidapadrao.hour, minutes=horasaidapadrao.minute
        )
        horasaidareal = datetime.timedelta(
            hours=x.Saida.hour, minutes=x.Saida.minute
        )
        if horasaidareal > horasaidapadrao:
            totalextra += horasaidareal - horasaidapadrao
    return totalextra


def calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalatrazo = total_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
    horazero = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraatrazo = (
        float(salario[0].Salario) / 30 / 9 / 60 / 60 * totalatrazo.seconds
    )
    contracheque = get_contrachequereferencia(
        mesreferencia, anoreferencia, idpessoal
    )
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
    return totalatrazo


def total_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    totalatrazo = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horaentradapadrao = datetime.datetime.strptime(
            "07:00:00", "%H:%M:%S"
        ).time()
        horaentradapadrao = datetime.timedelta(
            hours=horaentradapadrao.hour, minutes=horaentradapadrao.minute
        )
        horaentradareal = datetime.timedelta(
            hours=x.Entrada.hour, minutes=x.Entrada.minute
        )
        if horaentradareal > horaentradapadrao:
            totalatrazo += horaentradareal - horaentradapadrao
    return totalatrazo


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


def modal_horario_cartao_ponto(request):
    data = dict()
    if request.method == "POST":
        registros_cartao_ponto = []
        registros_cartao_ponto.append(
            CartaoPonto(
                Alteracao="MANUAL",
                Entrada=request.POST.get("Entrada"),
                Saida=request.POST.get("Saida"),
                idCartaoPonto=request.POST.get("idcartaoponto"),
            )
        )
        CartaoPonto.objects.bulk_update(
            registros_cartao_ponto, ["Alteracao", "Entrada", "Saida"]
        )
    else:
        cartao_ponto = CartaoPonto.objects.get(
            idCartaoPonto=request.GET.get("idcartaoponto")
        )
        contexto = {
            "form": CadastraCartaoPonto(instance=cartao_ponto),
            "mes_ano": request.GET.get("mes_ano"),
            "idcartaoponto": request.GET.get("idcartaoponto"),
        }
        data["html_modal"] = render_to_string(
            "pagamentos/modal_horario_cartao_ponto.html",
            contexto,
            request=request,
        )
    return JsonResponse(data)


# Excluir sem uso
def form_modal_horario(request, _id_cp, _mes_ano):
    data = dict()
    c_instance = None
    if _id_cp:
        c_instance = CartaoPonto.objects.get(idCartaoPonto=_id_cp)
    if request.method == "POST":
        form = CadastraCartaoPonto(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
    else:
        form = CadastraCartaoPonto(instance=c_instance)
    _url = "/pagamentos/altera_horario_cartao_ponto"
    _view = "altera_horario_cartao_ponto"
    context = {
        "url": _url,
        "view": _view,
        "form": form,
        "idcartaoponto": _id_cp,
        "mes_ano": _mes_ano,
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
    conta_colaborador = ContaPessoal.objects.filter(
        idPessoal=recibo.idPessoal_id
    )
    _banco = ContaPessoal.objects.filter(idPessoal=recibo.idPessoal_id)
    _vc = False
    if len(_banco) > 1:
        _vc = True
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
        "banco": _banco,
        "mais_banco": _vc,
    }
    return contexto


def create_contexto_imprime_relatorio_saldo_avulso(datainicial, datafinal):
    contexto = create_contexto_saldo_avulso(datainicial, datafinal)
    return contexto


def create_contexto_saldo_avulso(datainicial, datafinal):
    (
        saldo,
        saldototal,
        saldovales,
        totalselect,
    ) = create_contexto_avulsos_a_receber(datainicial, datafinal)
    contexto = {
        "saldo_colaborador": saldo,
        "saldo_total": saldototal,
        "data_inicial": datainicial,
        "data_final": datafinal,
    }
    for x in contexto["saldo_colaborador"]:
        pagar = create_contexto_minutas_avulso_receber(
            datainicial, datafinal, x["idPessoal"]
        )
        x["pagar"] = pagar
    return contexto


def create_contexto_minutas_avulso_receber(datainicial, datafinal, idpessoal):
    pagar = []
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
    _banco = ContaPessoal.objects.filter(idPessoal=idpessoal)
    _vc = False
    if len(_banco) > 1:
        _vc = True
    for index, itens in enumerate(minutas):
        if itens.Cargo == "AJUDANTE":
            minutaitens = MinutaItens.objects.filter(
                TipoItens="PAGA",
                idMinuta=itens.idMinuta,
                Descricao="AJUDANTE",
                idMinuta_id__DataMinuta__range=[datainicial, datafinal],
            )
            if minutaitens:
                pagar.append(
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
                pagar.append(
                    {
                        "Data": itens.idMinuta.DataMinuta,
                        "Minuta": itens.idMinuta.Minuta,
                        "Cliente": itens.idMinuta.idCliente.Fantasia,
                        "Descricao": minutas.Descricao,
                        "Valor": minutas.Valor,
                    }
                )
    context = {
        "pagar": pagar,
        "colaborador": colaborador,
        "datainicial": datainicial,
        "datafinal": datafinal,
    }
    return context["pagar"]


def html_agenda(request, contexto, data):
    data["html_agenda"] = render_to_string(
        "pagamentos/html_agenda.html", contexto, request=request
    )
    return data


def html_cartao_ponto(request, contexto, data):
    data["html_cartao_ponto"] = render_to_string(
        "pagamentos/html_cartao_ponto.html", contexto, request=request
    )
    return data


def html_contra_cheque(request, contexto, data):
    data["html_contra_cheque"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_files_contra_cheque(request, contexto, data):
    data["html_files_contra_cheque"] = render_to_string(
        "pessoas/html_files_contra_cheque.html", contexto, request=request
    )
    return data


def html_files_pagamento(request, contexto, data):
    data["html_files_pagamento"] = render_to_string(
        "pagamentos/html_files.html", contexto, request=request
    )
    return data


def html_card_folha_pagamento(request, contexto, data):
    data["html_card_folha_pagamento"] = render_to_string(
        "pagamentos/card_folha_pagamento.html", contexto, request=request
    )
    return data


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


def html_funcionario(request, contexto, data):
    data["html_funcionario"] = render_to_string(
        "pagamentos/html_funcionario.html", contexto, request=request
    )
    return data


def html_itens_agenda_pagamento(request, contexto, data):
    data["html_itens_agenda_pagamento"] = render_to_string(
        "pagamentos/html_itens_agenda.html", contexto, request=request
    )
    return data


def html_itens_contra_cheque(request, contexto, data):
    data["html_itens_contra_cheque"] = render_to_string(
        "pagamentos/html_itens_contra_cheque.html", contexto, request=request
    )
    return data


def html_minutas(request, contexto, data):
    data["html_minutas"] = render_to_string(
        "pagamentos/html_minutas.html", contexto, request=request
    )
    return data


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


def html_minutascontracheque(mesreferencia, anoreferencia, idpessoal):
    minutas = select_minutas_contracheque(
        mesreferencia, anoreferencia, idpessoal
    )
    context = {"minutas": minutas, "idPessoal": idpessoal}
    c_return = render_to_string("pagamentos/minutascontracheque.html", context)
    return c_return


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


def html_saldo_avulso(datainicial, datafinal):
    """
    utiliza a 'get_saldo_pagameto_avulso' para carregar as variáveis de saldo dos colaboradores que não são
    considerados mensalistas, conforme período definido pelo usuário. E retorna um 'render_to_string', do template
    'pagamentos/saldavulso.html'
    :param datainicial:
    :param datafinal:
    :return: render_to_string através da variável c_return
    """
    (
        saldo,
        saldototal,
        saldovales,
        totalselect,
    ) = create_contexto_avulsos_a_receber(datainicial, datafinal)
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


def html_vales(request, contexto, data):
    data["html_vales"] = render_to_string(
        "pessoas/card_vales_colaborador.html", contexto, request=request
    )
    return data


def html_vales_pagamento(request, contexto, data):
    data["html_vales_pagamento"] = render_to_string(
        "pagamentos/html_vales.html", contexto, request=request
    )
    return data


def busca_folha(mes, ano, colaboradores, salarios):
    mes_extenso = meses[int(mes) - 1]
    try:
        folha = FolhaPagamento.objects.get(
            MesReferencia=mes_extenso, AnoReferencia=ano
        )
        verifica_contra_cheque_colaboradores(colaboradores, mes, ano, salarios)
    except FolhaPagamento.DoesNotExist:
        create_folha(mes_extenso, ano)
        folha = FolhaPagamento.objects.get(
            MesReferencia=mes_extenso, AnoReferencia=ano
        )
        create_contra_cheques_folha(colaboradores, mes, ano, salarios)
        dias_conducao = create_cartao_ponto_folha(
            colaboradores, mes, ano, salarios
        )
        create_contra_cheque_itens_folha(
            colaboradores, mes, ano, salarios, dias_conducao
        )
    return folha


def verifica_contra_cheque_colaboradores(colaboradores, mes, ano, salarios):
    for colaborador in colaboradores:
        colaborador_lista = []
        colaborador_lista.append(colaborador)
        primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
        if colaborador["DataAdmissao"] <= ultimo_dia_mes.date():
            contra_cheque = busca_contracheque(
                meses[int(mes) - 1], ano, colaborador["idPessoal"]
            )
            contra_cheque = contra_cheque.filter(Descricao="PAGAMENTO")
            dias_conducao = 0
            if not contra_cheque:
                create_contra_cheques_folha(
                    colaborador_lista, mes, ano, salarios
                )
                dias_conducao = create_cartao_ponto_folha(
                    colaborador_lista, mes, ano, salarios
                )
                create_contra_cheque_itens_folha(
                    colaborador_lista, mes, ano, salarios, dias_conducao
                )


def create_folha(mes, ano):
    FolhaPagamento.objects.create(
        MesReferencia=mes,
        AnoReferencia=ano,
        Valor=0.00,
        Colaboradores=0,
        Pago=False,
    )


def get_colaboradores_mensalistas_admitidos():
    colaboradores = Pessoal.objects.filter(
        TipoPgto="MENSALISTA", DataDemissao__isnull=True, StatusPessoal=True
    )
    return colaboradores


def get_valores_salario_transporte_colaborador():
    salarios = Salario.objects.filter(
        idPessoal__TipoPgto="MENSALISTA", idPessoal__DataDemissao__isnull=True
    )
    return salarios


def create_contra_cheques_folha(colaboradores, mes, ano, salarios):
    mes_extenso = meses[int(mes) - 1]
    registros_contra_cheque = []
    for colaborador in colaboradores:
        filtro_salario = next(
            (
                item
                for item in salarios
                if item["idPessoal_id"] == colaborador["idPessoal"]
            ),
            None,
        )
        salario = filtro_salario["Salario"]
        if salario > 0.00:
            registros_contra_cheque.append(
                ContraCheque(
                    MesReferencia=mes_extenso,
                    AnoReferencia=ano,
                    Valor=0.00,
                    Pago=False,
                    Descricao="PAGAMENTO",
                    idPessoal_id=colaborador["idPessoal"],
                )
            )
            registros_contra_cheque.append(
                ContraCheque(
                    MesReferencia=mes_extenso,
                    AnoReferencia=ano,
                    Valor=0.00,
                    Pago=False,
                    Descricao="ADIANTAMENTO",
                    idPessoal_id=colaborador["idPessoal"],
                )
            )
    ContraCheque.objects.bulk_create(registros_contra_cheque)


def create_contra_cheque_itens_folha(
    colaboradores, mes, ano, salarios, dias_conducao
):
    registro_contra_cheque_itens = []
    contra_cheque_pagamento = list(
        get_contra_cheque_mes_ano_pagamento(int(mes), ano).values()
    )
    contra_cheque_adiantamento = list(
        get_contra_cheque_mes_ano_adiantamento(int(mes), ano).values()
    )
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    for colaborador in colaboradores:
        filtro_salario = next(
            (
                item
                for item in salarios
                if item["idPessoal_id"] == colaborador["idPessoal"]
            ),
            None,
        )
        salario = filtro_salario["Salario"]
        valor_conducao = filtro_salario["ValeTransporte"] * dias_conducao
        if salario > 0.00:
            filtro_pagamento = next(
                (
                    item
                    for item in contra_cheque_pagamento
                    if item["idPessoal_id"] == colaborador["idPessoal"]
                ),
                None,
            )
            filtro_adiantamento = next(
                (
                    item
                    for item in contra_cheque_adiantamento
                    if item["idPessoal_id"] == colaborador["idPessoal"]
                ),
                None,
            )
            adiantamento = salario / 100 * 40
            dias = 30 - colaborador["DataAdmissao"].day + 1
            if ultimo_dia_mes.day == 31:
                dias += 1
            if colaborador["DataAdmissao"] <= primeiro_dia_mes.date():
                registro_contra_cheque_itens.append(
                    ContraChequeItens(
                        Descricao="SALARIO",
                        Valor=salario,
                        Registro="C",
                        Referencia="30d",
                        idContraCheque_id=filtro_pagamento["idContraCheque"],
                    )
                )
                registro_contra_cheque_itens.append(
                    ContraChequeItens(
                        Descricao="ADIANTAMENTO",
                        Valor=adiantamento,
                        Registro="C",
                        Referencia="40%",
                        idContraCheque_id=filtro_adiantamento[
                            "idContraCheque"
                        ],
                    )
                )
                registro_contra_cheque_itens.append(
                    ContraChequeItens(
                        Descricao="ADIANTAMENTO",
                        Valor=adiantamento,
                        Registro="D",
                        Referencia="40%",
                        idContraCheque_id=filtro_pagamento["idContraCheque"],
                    )
                )
            else:
                registro_contra_cheque_itens.append(
                    ContraChequeItens(
                        Descricao="SALARIO",
                        Valor=salario / 30 * dias,
                        Registro="C",
                        Referencia=f"{dias}d",
                        idContraCheque_id=filtro_pagamento["idContraCheque"],
                    )
                )
            if valor_conducao > Decimal(0.00):
                registro_contra_cheque_itens.append(
                    ContraChequeItens(
                        Descricao="VALE TRANSPORTE",
                        Valor=valor_conducao,
                        Registro="C",
                        Referencia=f"{dias_conducao}d",
                        idContraCheque_id=filtro_pagamento["idContraCheque"],
                    )
                )
    ContraChequeItens.objects.bulk_create(registro_contra_cheque_itens)


def create_cartao_ponto_folha(colaboradores, mes, ano, salarios):
    feriados = DiasFeriados().__dict__["feriados"]
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    registros_cartao_ponto = []
    for colaborador in colaboradores:
        dia = primeiro_dia_mes
        filtro_salario = next(
            (
                item
                for item in salarios
                if item["idPessoal_id"] == colaborador["idPessoal"]
            ),
            None,
        )
        salario = filtro_salario["Salario"]
        valor_conducao = filtro_salario["ValeTransporte"]
        dias_conducao = 0
        if salario > 0.00:
            while dia < ultimo_dia_mes + relativedelta(days=1):
                hora_entrada = "07:00"
                hora_saida = "17:00"
                remunerado = True
                conducao = False
                if dia.weekday() == 5 or dia.weekday() == 6:
                    ausencia = dias[dia.weekday()]
                else:
                    ausencia = ""
                    if valor_conducao > Decimal(0.00):
                        conducao = True
                        dias_conducao += 1
                if dia.date() in feriados:
                    ausencia = "FERIADO"
                    if valor_conducao > Decimal(0.00):
                        conducao = False
                        dias_conducao -= 1
                if dia.date() < colaborador["DataAdmissao"]:
                    ausencia = "-------"
                    conducao = False
                    remunerado = False
                registros_cartao_ponto.append(
                    CartaoPonto(
                        Dia=dia,
                        Entrada=hora_entrada,
                        Saida=hora_saida,
                        Ausencia=ausencia,
                        Alteracao="ROBOT",
                        Conducao=conducao,
                        Remunerado=remunerado,
                        CarroEmpresa=False,
                        idPessoal_id=colaborador["idPessoal"],
                    )
                )
                dia = dia + relativedelta(days=1)
    CartaoPonto.objects.bulk_create(registros_cartao_ponto)
    return dias_conducao


def contra_cheques_folha_pagamento(folha, colaboradores, salarios):
    mes = meses.index(folha.MesReferencia) + 1
    ano = folha.AnoReferencia
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    contra_cheques_adiantamento = list(
        get_contra_cheque_mes_ano_adiantamento(mes, ano).values(
            "idContraCheque", "idPessoal_id", "idPessoal__Nome"
        )
    )
    contra_cheques_pagamento = list(
        get_contra_cheque_mes_ano_pagamento(mes, ano).values(
            "idContraCheque", "idPessoal_id", "idPessoal__Nome"
        )
    )
    contra_cheques = []
    colaboradores = list(
        filter(
            lambda item: item["DataAdmissao"] <= ultimo_dia_mes.date(),
            colaboradores,
        )
    )
    for colaborador in colaboradores:
        filtro_salario = next(
            (
                item
                for item in salarios
                if item["idPessoal_id"] == colaborador["idPessoal"]
            ),
            None,
        )
        salario = filtro_salario["Salario"]
        if salario > 0.00:
            filtro_adiantamento = list(
                filter(
                    lambda item: item["idPessoal_id"]
                    == colaborador["idPessoal"],
                    contra_cheques_adiantamento,
                )
            )
            filtro_pagamento = list(
                filter(
                    lambda item: item["idPessoal_id"]
                    == colaborador["idPessoal"],
                    contra_cheques_pagamento,
                )
            )
            contra_cheques.append(
                {
                    "nome": nome_curto(colaborador["Nome"]),
                    "idpessoal": colaborador["idPessoal"],
                    "idadiantamento": filtro_adiantamento[0]["idContraCheque"],
                    "idpagamento": filtro_pagamento[0]["idContraCheque"],
                }
            )
    lista_contra_cheques = []
    for contra_cheque in contra_cheques:
        lista_contra_cheques.append(contra_cheque["idadiantamento"])
        lista_contra_cheques.append(contra_cheque["idpagamento"])
    contra_cheque_itens = list(
        ContraChequeItens.objects.filter(
            idContraCheque_id__in=lista_contra_cheques
        ).values()
    )
    for contra_cheque in contra_cheques:
        adiciona_saldo_colaborador_contra_cheque(
            contra_cheque, contra_cheque_itens, "idadiantamento"
        )
        adiciona_saldo_colaborador_contra_cheque(
            contra_cheque, contra_cheque_itens, "idpagamento"
        )
        adiciona_valor_salario_colaborador_contra_cheque(
            contra_cheque, salarios
        )
    contexto = {"contra_cheques": contra_cheques}
    contexto.update(totais_contra_cheques(contra_cheques, contra_cheque_itens))
    return contexto


def adiciona_saldo_colaborador_contra_cheque(
    contra_cheque, contra_cheque_itens, id
):
    filtro = list(
        filter(
            lambda item: item["idContraCheque_id"] == contra_cheque[id],
            contra_cheque_itens,
        )
    )
    debito = sum(item["Valor"] for item in filtro if item["Registro"] == "D")
    credito = sum(item["Valor"] for item in filtro if item["Registro"] == "C")
    saldo = credito - debito
    if id == "idadiantamento":
        contra_cheque["saldo_adiantamento"] = saldo
    else:
        contra_cheque["saldo_pagamento"] = saldo
    return contra_cheque


def adiciona_valor_salario_colaborador_contra_cheque(contra_cheque, salarios):
    salario = list(
        filter(
            lambda item: item["idPessoal_id"] == contra_cheque["idpessoal"],
            salarios,
        )
    )
    contra_cheque["salario"] = salario[0]["Salario"]
    return contra_cheque


def totais_contra_cheques(contra_cheques, contra_cheque_itens):
    total_saldo_adiantamento = Decimal(0.00)
    total_saldo_pagamento = Decimal(0.00)
    total_folha = Decimal(0.00)
    total_saldo_adiantamento = sum(
        item["saldo_adiantamento"] for item in contra_cheques
    )
    total_saldo_pagamento = sum(
        item["saldo_pagamento"] for item in contra_cheques
    )
    total_folha_debito = sum(
        item["Valor"]
        for item in contra_cheque_itens
        if item["Registro"] == "D" and item["Vales_id"] == 0
    )
    total_folha_credito = sum(
        item["Valor"]
        for item in contra_cheque_itens
        if item["Registro"] == "C"
    )
    total_folha = total_folha_credito - total_folha_debito
    contexto = {
        "total_saldo_adiantamento": total_saldo_adiantamento,
        "total_saldo_pagamento": total_saldo_pagamento,
        "total_folha": total_folha,
    }
    return contexto


def verifica_feriados(cartao_ponto, mes, ano):
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    lista_feriados = list(
        Parametros.objects.filter(
            Chave="FERIADO",
            Valor__gte=primeiro_dia_mes,
            Valor__lte=ultimo_dia_mes,
        ).values()
    )
    registros_cartao_ponto = []
    for feriado in lista_feriados:
        dia = datetime.datetime.strptime(feriado["Valor"], "%Y-%m-%d").date()
        filtro = list(filter(lambda item: item["Dia"] == dia, cartao_ponto))
        if filtro[0]["Ausencia"] != "FÉRIAS":
            if filtro[0]["Ausencia"] != "FERIADO" and dia.weekday() != 6:
                filtro[0]["Ausencia"] = "FERIADO"
                filtro[0]["Conducao"] = False
                registros_cartao_ponto.append(
                    CartaoPonto(
                        idCartaoPonto=filtro[0]["idCartaoPonto"],
                        Ausencia="FERIADO",
                        Conducao=False,
                    )
                )
    CartaoPonto.objects.bulk_update(
        registros_cartao_ponto, ["Ausencia", "Conducao"]
    )


def get_agenda_periodo_contra_cheque(
    idpessoal, primeiro_dia_mes, ultimo_dia_mes
):
    agenda = list(
        Agenda.objects.filter(
            idPessoal=idpessoal,
            Dia__range=(primeiro_dia_mes, ultimo_dia_mes),
        ).values()
    )
    return agenda


def get_minutas_periodo_contra_cheque(
    idpessoal, primeiro_dia_mes, ultimo_dia_mes
):
    minutas = list(
        MinutaColaboradores.objects.filter(
            idPessoal=idpessoal,
            idMinuta_id__DataMinuta__range=(primeiro_dia_mes, ultimo_dia_mes),
        )
        .exclude(idMinuta_id__StatusMinuta="ABERTA")
        .values(
            idminuta=F("idMinuta"),
            minuta=F("idMinuta_id__Minuta"),
            data_minuta=F("idMinuta_id__DataMinuta"),
            hora_inicial=F("idMinuta_id__HoraInicial"),
            hora_final=F("idMinuta_id__HoraFinal"),
            fantasia=F("idMinuta_id__idCliente_id__Fantasia"),
        )
    )
    return minutas


def union_minutas_agenda_periodo_contra_cheque(
    idpessoal, primeiro_dia_mes, ultimo_dia_mes
):
    minutas = get_minutas_periodo_contra_cheque(
        idpessoal, primeiro_dia_mes, ultimo_dia_mes
    )
    agenda = get_agenda_periodo_contra_cheque(
        idpessoal, primeiro_dia_mes, ultimo_dia_mes
    )
    for item in agenda:
        minutas.append(
            {
                "idminuta": "",
                "data_minuta": item["Dia"],
                "minuta": "",
                "fantasia": item["Descricao"],
                "hora_inicial": datetime.time(0, 0),
                "hora_final": datetime.time(0, 0),
                "idPessoal": "",
                "Extra": "00:00",
            }
        )
    minutas_agenda = sorted(minutas, key=lambda d: d["data_minuta"])
    return minutas_agenda


def atualiza_cartao_ponto_transporte(cartao_ponto, vale_transporte):
    registros_cartao_ponto = [
        CartaoPonto(
            idCartaoPonto=dia.idCartaoPonto,
            Conducao=vale_transporte > Decimal(0.00) and not dia.CarroEmpresa,
            idPessoal_id=dia.idPessoal_id,
        )
        for dia in cartao_ponto
        if dia.Ausencia == ""
    ]

    CartaoPonto.objects.bulk_update(registros_cartao_ponto, ["Conducao"])
    return cartao_ponto


def atualiza_cartao_ponto_minutas(cartao_ponto, minutas):
    #  start, start_queries = queries_inicio()
    registros_cartao_ponto = []
    for minuta in minutas:
        dia = next(
            (
                item
                for item in cartao_ponto
                if item.Dia == minuta["data_minuta"]
            ),
            None,
        )
        if (
            minuta["hora_inicial"] < dia.Entrada
            and dia["Alteracao"] != "MANUAL"
        ):
            dia.Entrada = minuta["hora_inicial"]
            registros_cartao_ponto.append(
                CartaoPonto(
                    idCartaoPonto=dia.idCartaoPonto,
                    Entrada=minuta["hora_inicial"],
                    Saida=dia.Saida,
                    idPessoal_id=dia.idPessoal_id,
                )
            )
        if minuta["hora_final"] > dia.Saida and dia.Alteracao != "MANUAL":
            dia.Saida = minuta["hora_final"]
            registros_cartao_ponto.append(
                CartaoPonto(
                    idCartaoPonto=dia.idCartaoPonto,
                    Entrada=dia.Entrada,
                    Saida=minuta["hora_final"],
                    idPessoal_id=dia.idPessoal_id,
                )
            )
    CartaoPonto.objects.bulk_update(
        registros_cartao_ponto, ["Entrada", "Saida"]
    )
    #  queries_termino(start, start_queries, "[INFO] Atualiza Cartão Ponto")
    return cartao_ponto


def atualiza_itens_contra_cheque_pagamento(
    colaborador, cartao_ponto, minutas, salario, vale_transporte, mes, ano
):
    #  start, start_queries = queries_inicio()
    contra_cheque = busca_contracheque(
        meses[int(mes) - 1], ano, colaborador.id_pessoal
    )
    contra_cheque = contra_cheque.filter(Descricao="PAGAMENTO")
    horas_extras = horas_extras_colaborador(cartao_ponto, minutas)
    faltas = list(
        filter(
            lambda item: item.Ausencia == "FALTA" and item.Remunerado == False,
            cartao_ponto,
        )
    )
    update_itens = []
    create_itens = []
    _, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)
    dias_pagar_mes = dias_remunerado(cartao_ponto, ultimo_dia)

    atualiza_item_salario(contra_cheque, salario, dias_pagar_mes, update_itens)
    atualiza_item_vale_transporte(
        contra_cheque,
        vale_transporte,
        cartao_ponto,
        update_itens,
        create_itens,
    )
    atualiza_item_horas_extras(
        contra_cheque, salario, horas_extras, update_itens, create_itens
    )
    atualiza_item_adiantamento(colaborador, mes, ano, create_itens)
    atualiza_item_atrazos(
        contra_cheque, salario, cartao_ponto, update_itens, create_itens
    )
    atualiza_item_faltas(
        contra_cheque, salario, faltas, update_itens, create_itens
    )
    atualiza_item_desconto_dsr(
        contra_cheque,
        salario,
        faltas,
        update_itens,
        create_itens,
        mes,
        ano,
        colaborador,
    )
    atualiza_item_salario_ferias(
        contra_cheque, salario, cartao_ponto, update_itens, create_itens
    )
    ContraChequeItens.objects.bulk_update(
        update_itens, ["Valor", "Referencia"]
    )
    ContraChequeItens.objects.bulk_create(create_itens)
    #  queries_termino(
    #  start, start_queries, "[INFO] Atualiza Itens Contra-Cheque"
    #  )


def atualiza_item_salario(
    contra_cheque, salario, dias_pagar_mes, update_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0], "SALARIO", "C"
    )
    salario_mes = (salario / 30 * dias_pagar_mes).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    if contra_cheque_itens:
        update_itens.append(
            ContraChequeItens(
                idContraChequeItens=contra_cheque_itens[0].idContraChequeItens,
                Valor=salario_mes,
                Referencia=f"{dias_pagar_mes}d",
            )
        )


def atualiza_item_adiantamento(colaborador, mes, ano, create_itens):
    contra_cheque = busca_contracheque(
        meses[int(mes) - 1], ano, colaborador.id_pessoal
    )
    contra_cheque_pagamento = contra_cheque.filter(
        Descricao="PAGAMENTO"
    ).first()

    contra_cheque_item_adiantamento = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_pagamento.idContraCheque,
        Descricao="ADIANTAMENTO",
    ).first()

    if contra_cheque_item_adiantamento:
        return

    contra_cheque_adiantamento = contra_cheque.filter(
        Descricao="ADIANTAMENTO"
    ).first()

    if contra_cheque_adiantamento:
        contra_cheque_item = ContraChequeItens.objects.filter(
            idContraCheque_id=contra_cheque_adiantamento.idContraCheque,
            Descricao="ADIANTAMENTO",
        ).first()

        create_itens.append(
            ContraChequeItens(
                Descricao=contra_cheque_item.Descricao,
                Valor=contra_cheque_item.Valor,
                Registro="D",
                Referencia=contra_cheque_item.Referencia,
                idContraCheque_id=contra_cheque_pagamento.idContraCheque,
            )
        )

    return


def atualiza_item_atrazos(
    contra_cheque, salario, cartao_ponto, update_itens, create_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0], "ATRAZOS", "D"
    )
    hora_zerada = datetime.timedelta(hours=0, minutes=0)
    atrazos = hora_zerada
    for dia in cartao_ponto:
        hora_entrada_padrao = datetime.datetime.strptime(
            "07:00:00", "%H:%M:%S"
        ).time()
        hora_entrada_timedelta = datetime.timedelta(
            hours=hora_entrada_padrao.hour, minutes=hora_entrada_padrao.minute
        )
        hora_entrada_dia = datetime.timedelta(
            hours=dia.Entrada.hour, minutes=dia.Entrada.minute
        )
        atrazos += (
            hora_entrada_dia - hora_entrada_timedelta
            if hora_entrada_dia > hora_entrada_timedelta
            else hora_zerada
        )
    valor_desconto_atrazos = salario / 30 / 9 / 60 / 60 * atrazos.seconds
    if atrazos > hora_zerada:
        if contra_cheque_itens:
            if str(atrazos) != contra_cheque_itens[0].Referencia:
                update_itens.append(
                    ContraChequeItens(
                        idContraChequeItens=contra_cheque_itens[
                            0
                        ].idContraChequeItens,
                        Valor=valor_desconto_atrazos,
                        Referencia=atrazos,
                    )
                )
        else:
            create_itens.append(
                ContraChequeItens(
                    Descricao="ATRAZOS",
                    Valor=valor_desconto_atrazos,
                    Registro="D",
                    Referencia=atrazos,
                    idContraCheque_id=contra_cheque[0].idContraCheque,
                )
            )
    else:
        if contra_cheque_itens:
            contra_cheque_itens.delete()


def atualiza_item_faltas(
    contra_cheque, salario, faltas, update_itens, create_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0].idContraCheque, "FALTAS", "D"
    )
    valor_dia = salario / 30
    if faltas:
        if contra_cheque_itens:
            if len(faltas) != int(contra_cheque_itens[0].Referencia):
                update_itens.append(
                    ContraChequeItens(
                        idContraChequeItens=contra_cheque_itens[
                            0
                        ].idContraChequeItens,
                        Valor=len(faltas) * valor_dia,
                        Referencia=len(faltas),
                    )
                )
        else:
            create_itens.append(
                ContraChequeItens(
                    Descricao="FALTAS",
                    Valor=len(faltas) * valor_dia,
                    Registro="D",
                    Referencia=len(faltas),
                    idContraCheque_id=contra_cheque[0].idContraCheque,
                )
            )
    else:
        if contra_cheque_itens:
            contra_cheque_itens.delete()


def atualiza_item_desconto_dsr(
    contra_cheque,
    salario,
    faltas,
    update_itens,
    create_itens,
    mes,
    ano,
    colaborador,
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0].idContraCheque, "DSR SOBRE FALTAS", "D"
    )
    valor_dia = salario / 30
    semanas_faltas = []
    for falta in faltas:
        semanas_faltas.append(datetime.datetime.strftime(falta.Dia, "%V"))
    semanas_faltas = list(map(int, semanas_faltas))
    semanas_faltas = set(semanas_faltas)
    desconto_dsr = len(semanas_faltas)
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    if 1 <= primeiro_dia_mes.weekday() <= 4:
        verifica_falta_ultima_semana_mes_amterior(
            colaborador, primeiro_dia_mes, semanas_faltas
        )
    semanas_feriados = []
    ultimo_dia_mes_seguinte = ultimo_dia_mes + relativedelta(months=+1)
    lista_feriados = list(
        Parametros.objects.filter(
            Chave="FERIADO",
            Valor__gte=primeiro_dia_mes,
            Valor__lte=ultimo_dia_mes_seguinte,
        ).values()
    )
    if lista_feriados:
        for feriado in lista_feriados:
            dia = datetime.datetime.strptime(feriado["Valor"], "%Y-%m-%d")
            if dia.weekday() != 6:
                semanas_feriados.append(datetime.datetime.strftime(dia, "%V"))
        semanas_feriados = list(map(int, semanas_feriados))
        semanas_feriados = set(semanas_feriados)
        for semana in semanas_faltas:
            if semana == 52:
                semana = 0
            if semana + 1 in semanas_feriados:
                desconto_dsr += 1
    if desconto_dsr > 0:
        if contra_cheque_itens:
            if desconto_dsr != int(contra_cheque_itens[0].Referencia):
                update_itens.append(
                    ContraChequeItens(
                        idContraChequeItens=contra_cheque_itens[
                            0
                        ].idContraChequeItens,
                        Valor=desconto_dsr * valor_dia,
                        Referencia=desconto_dsr,
                    )
                )
        else:
            create_itens.append(
                ContraChequeItens(
                    Descricao="DSR SOBRE FALTAS",
                    Valor=desconto_dsr * valor_dia,
                    Registro="D",
                    Referencia=desconto_dsr,
                    idContraCheque_id=contra_cheque[0].idContraCheque,
                )
            )
    else:
        if contra_cheque_itens:
            contra_cheque_itens.delete()


def verifica_falta_ultima_semana_mes_amterior(
    colaborador, primeiro_dia_mes, semanas_faltas
):
    inicio = primeiro_dia_mes - datetime.timedelta(primeiro_dia_mes.weekday())
    fim = primeiro_dia_mes - datetime.timedelta(1)
    faltas_mes_anterior = list(
        CartaoPonto.objects.filter(
            idPessoal=colaborador.id_pessoal,
            Ausencia="FALTA",
            Remunerado=False,
            Dia__range=[inicio, fim],
        ).values()
    )
    if faltas_mes_anterior:
        semana_mes_anterior = datetime.datetime.strftime(
            faltas_mes_anterior[0]["Dia"], "%V"
        )
        if semana_mes_anterior in semanas_faltas:
            semanas_faltas.remove(int(semana_mes_anterior))


def atualiza_item_horas_extras(
    contra_cheque, salario, horas_extras, update_itens, create_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0].idContraCheque, "HORA EXTRA", "C"
    )
    hora_zerada = datetime.datetime.strptime("00:00:00", "%H:%M:%S").time()
    if horas_extras > hora_zerada:
        valor_horas_extras = calcula_horas_extras_colaborador(
            salario, horas_extras
        )
        if contra_cheque_itens:
            update_itens.append(
                ContraChequeItens(
                    idContraChequeItens=contra_cheque_itens[
                        0
                    ].idContraChequeItens,
                    Valor=valor_horas_extras,
                    Referencia=horas_extras,
                )
            )
        else:
            create_itens.append(
                ContraChequeItens(
                    Descricao="HORA EXTRA",
                    Valor=valor_horas_extras,
                    Registro="C",
                    Referencia=horas_extras,
                    idContraCheque_id=contra_cheque[0].idContraCheque,
                )
            )
    else:
        if contra_cheque_itens:
            contra_cheque_itens.delete()


def atualiza_item_vale_transporte(
    contra_cheque, salario, cartao_ponto, update_itens, create_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0].idContraCheque, "VALE TRANSPORTE", "C"
    )
    dias = dias_transporte(cartao_ponto)
    valor_transporte = salario
    if valor_transporte > Decimal(0.00):
        if contra_cheque_itens:
            update_itens.append(
                ContraChequeItens(
                    idContraChequeItens=contra_cheque_itens[
                        0
                    ].idContraChequeItens,
                    Valor=valor_transporte * dias,
                    Referencia=dias,
                )
            )
        else:
            create_itens.append(
                ContraChequeItens(
                    Descricao="VALE TRANSPORTE",
                    Valor=valor_transporte * dias,
                    Registro="C",
                    Referencia=dias,
                    idContraCheque_id=contra_cheque[0].idContraCheque,
                )
            )
    else:
        if contra_cheque_itens:
            contra_cheque_itens.delete()


def atualiza_item_salario_ferias(
    contra_cheque, salario, cartao_ponto, update_itens, create_itens
):
    contra_cheque_itens = busca_contrachequeitens(
        contra_cheque[0].idContraCheque, "SALARIO", "C"
    )
    valor_dia = salario / 30
    ferias = list(
        filter(
            lambda item: item.Ausencia == "FÉRIAS",
            cartao_ponto,
        )
    )
    if len(ferias) > 0:
        dias_pagar = len(cartao_ponto) - len(ferias)
        first_ferias = datetime.datetime.strftime(ferias[0]["Dia"], "%d/%m/%Y")
        last_ferias = datetime.datetime.strftime(ferias[-1]["Dia"], "%d/%m/%Y")
        obs = f"FÉRIAS: {first_ferias} - {last_ferias}"
        update_contra_cheque_obs(contra_cheque[0], obs, "ferias")
        if contra_cheque_itens:
            update_itens.append(
                ContraChequeItens(
                    idContraChequeItens=contra_cheque_itens[
                        0
                    ].idContraChequeItens,
                    Valor=valor_dia * dias_pagar,
                    Referencia=f"{str(dias_pagar).zfill(2)}d",
                )
            )


def horas_extras_colaborador(cartao_ponto, minutas):
    hora_entrada_padrao = datetime.timedelta(hours=7, minutes=0)
    hora_saida_padrao = datetime.timedelta(hours=17, minutes=0)
    horas_extras_mensal = datetime.timedelta(hours=0, minutes=0)
    for itens in cartao_ponto:
        horas_extras_entrada = datetime.timedelta(hours=0, minutes=0)
        horas_extras_saida = datetime.timedelta(hours=0, minutes=0)
        hora_entrada_cartao_ponto = datetime.timedelta(
            hours=itens.Entrada.hour,
            minutes=itens.Entrada.minute,
        )
        hora_saida_cartao_ponto = datetime.timedelta(
            hours=itens.Saida.hour, minutes=itens.Saida.minute
        )
        if hora_entrada_cartao_ponto < hora_entrada_padrao:
            horas_extras_entrada += (
                hora_entrada_padrao - hora_entrada_cartao_ponto
            )
            hora = datetime.datetime.strptime(
                str(hora_entrada_cartao_ponto), "%H:%M:%S"
            ).time()
            minuta = list(
                filter(
                    lambda minutas: minutas["data_minuta"] == itens.Dia
                    and minutas["hora_final"] == hora,
                    minutas,
                )
            )
            if minuta:
                if "hora_extra" in minuta:
                    horas_extras_existente = datetime.timedelta(
                        hours=minuta[0]["hora_extra"].hour,
                        minutes=minuta[0]["hora_extra"].minute,
                    )
                else:
                    horas_extras_existente = datetime.timedelta(
                        hours=0, minutes=0
                    )
                horas_extras_nova = (
                    horas_extras_existente + horas_extras_entrada
                )
                minuta[0]["hora_extra"] = datetime.datetime.strptime(
                    str(horas_extras_nova), "%H:%M:%S"
                ).time
        if hora_saida_cartao_ponto > hora_saida_padrao:
            horas_extras_saida += hora_saida_cartao_ponto - hora_saida_padrao
            hora = datetime.datetime.strptime(
                str(hora_saida_cartao_ponto), "%H:%M:%S"
            ).time()
            minuta = list(
                filter(
                    lambda minutas: minutas["data_minuta"] == itens.Dia
                    and minutas["hora_final"] == hora,
                    minutas,
                )
            )
            if minuta:
                if "hora_extra" in minuta:
                    horas_extras_existente = datetime.timedelta(
                        hours=minuta[0]["hora_extra"].hour,
                        minutes=minuta[0]["hora_extra"].minute,
                    )
                else:
                    horas_extras_existente = datetime.timedelta(
                        hours=0, minutes=0
                    )
                horas_extras_nova = horas_extras_existente + horas_extras_saida
                minuta[0]["hora_extra"] = datetime.datetime.strptime(
                    str(horas_extras_nova), "%H:%M:%S"
                ).time
        horas_extras_mensal += horas_extras_entrada + horas_extras_saida
    horas_extras_mensal = datetime.datetime.strptime(
        str(horas_extras_mensal), "%H:%M:%S"
    ).time()
    return horas_extras_mensal


def calcula_horas_extras_colaborador(salario, horas_extras):
    horas_extras = datetime.timedelta(
        hours=horas_extras.hour, minutes=horas_extras.minute
    )
    valor_horas_extras = (
        float(salario) / 30 / 9 / 60 / 60 * 1.5 * horas_extras.seconds
    )
    return valor_horas_extras


def texste():
    pass


def create_contexto_contra_cheque(idpessoal, mes_ano, descricao):
    contexto = create_contexto_contra_cheque_colaborador(
        idpessoal, mes_ano, descricao
    )
    return contexto


def create_data_contra_cheque_colaborador(request, contexto):
    data = dict()
    html_contra_cheque(request, contexto, data)
    if contexto["contra_cheque"].Pago:
        if not contexto["file"]:
            html_files_contra_cheque(request, contexto, data)
    return JsonResponse(data)


def modal_agenda_colaborador(request, idpessoal, mes_ano):
    data = dict()
    if request.method == "POST":
        descricao = request.POST.get("Descricao").upper()
        data_agenda = request.POST.get("Dia")
        mes_ano = request.POST.get("mes_ano")
        registro_agenda = []
        registro_agenda.append(
            Agenda(
                Descricao=descricao,
                Dia=data_agenda,
                idPessoal_id=idpessoal,
            )
        )
        Agenda.objects.bulk_create(registro_agenda)
        contexto = contexto_agenda_colaborador(idpessoal, mes_ano)
        html_agenda(request, contexto, data)
    else:
        contexto = {
            "form": FormAgenda,
            "idpessoal": idpessoal,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pagamentos/modal_adiciona_agenda.html", contexto, request=request
        )
    return JsonResponse(data)


def contexto_agenda_colaborador(idpessoal, mes_ano):
    mes, ano = converter_mes_ano(mes_ano)
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    agenda = get_agenda_periodo_contra_cheque(
        idpessoal, primeiro_dia_mes, ultimo_dia_mes
    )
    files = FileUpload.objects.filter(DescricaoUpload__startswith="AGENDA")
    for dia in agenda:
        filtro = next(
            (
                item
                for item in files
                if int(item.DescricaoUpload[9:]) == dia["idAgenda"]
            ),
            None,
        )
        if filtro:
            dia["file"] = filtro
    contexto = {"agenda": agenda}
    return contexto


def modal_confirma(request, confirma, idconfirma, idpessoal, mes_ano):
    data = dict()
    if confirma == "confirma_agenda":
        agenda = get_agenda_id(idconfirma)
        contexto = {
            "agenda": agenda,
            "idpessoal": idpessoal,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pagamentos/modal_exclui_agenda.html",
            contexto,
            request=request,
        )
    elif confirma == "confirma_exclui_arquivo_agenda":
        agenda = get_agenda_id(idconfirma)
        contexto = {
            "agenda": agenda,
            "idpessoal": idpessoal,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pagamentos/modal_exclui_arquivo_agenda.html",
            contexto,
            request=request,
        )
    elif confirma == "confirma_edita_agenda":
        agenda = get_agenda_id(idconfirma)
        form = FormAgenda(instance=agenda)
        contexto = {
            "form": form,
            "idpessoal": idpessoal,
            "mes_ano": mes_ano,
            "idagenda": idconfirma,
        }
        data["html_modal"] = render_to_string(
            "pagamentos/modal_adiciona_agenda.html", contexto, request=request
        )
    return JsonResponse(data)


def get_agenda_id(idagenda):
    agenda = Agenda.objects.get(idAgenda=idagenda)
    return agenda


def update_agenda_colaborador(request, idagenda, idpessoal):
    dia = request.POST.get("Dia")
    descricao = request.POST.get("Descricao")
    registro_agenda = []
    registro_agenda.append(
        Agenda(
            idAgenda=idagenda,
            Descricao=descricao,
            Dia=dia,
            idPessoal_id=idpessoal,
        )
    )
    Agenda.objects.bulk_update(registro_agenda, ["Dia", "Descricao"])


def exclui_agenda_colaborador_id(request, idagenda, idpessoal, mes_ano):
    agenda = get_agenda_id(idagenda)
    agenda.delete()


def create_data_agenda_colaborador(request, contexto):
    data = dict()
    data = html_agenda(request, contexto, data)
    return JsonResponse(data)


def salva_arquivo_agenda(request, idagenda):
    message = {"text": None, "type": None}
    if request.method == "POST":
        if request.FILES:
            descricao = f"Agenda_-_{str(idagenda).zfill(6)}"
            ext_file = request.FILES["arquivo"].name.split(".")[-1]
            name_file = f"{descricao}.{ext_file}"
            request.FILES["arquivo"].name = name_file
            obj = FileUpload()
            obj.DescricaoUpload = descricao
            obj.uploadFile = request.FILES["arquivo"]
            try:
                obj.save()
                message["text"] = "Arquivo enviado ao servidor com sucesso"
                message["type"] = "SUCESSO"
            except:
                message["text"] = "Falha ao salvar o arquivo, tente novamente"
                message["type"] = "ERROR"
        else:
            message["text"] = "Arquivo não selecionado"
            message["type"] = "ERROR"
    return message


def exclui_arquivo_agenda_servidor(request, idagenda):
    file_descricao = f"AGENDA_-_{str(idagenda).zfill(6)}"
    file = busca_arquivo_descricao(file_descricao)
    if file:
        try:
            os.remove(file.uploadFile.path)
            file.delete()
        except FileNotFoundError:
            print("ARQUIVO NÃO ENCONTRADO")
