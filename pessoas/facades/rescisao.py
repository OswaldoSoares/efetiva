""" Responsável pelo resscisão do colaborador """
from datetime import datetime, timedelta
from typing import Any, Optional
from django.http import JsonResponse
from core import constants
from core.tools import primeiro_e_ultimo_dia_do_mes
from pessoas import classes
from pessoas import html_data
from pessoas.facade import obter_contra_cheque
from pessoas.facade import gerar_data_html
from pessoas.facade import registrar_contra_cheque
from pessoas.models import CartaoPonto, Pessoal


def validar_modal_data_demissao_colaborador(
    request: Any,
) -> Optional[JsonResponse]:
    if request.method != "POST":
        return None

    id_pessoal = request.POST.get("id_pessoal")
    demissao_str = request.POST.get("demissao")

    demissao = datetime.strptime(demissao_str, "%Y-%m-%d").date()
    hoje = datetime.today().date()

    colaborador = classes.Colaborador(id_pessoal)
    # TODO Error pyright
    admissao = colaborador.dados_profissionais.data_admissao  # type: ignore

    if demissao > hoje:
        return JsonResponse(
            {
                "error": "A data de demissão não pode ser posterior ao dia "
                "de hoje."
            },
            status=400,
        )

    if demissao <= admissao:
        return JsonResponse(
            {
                "error": "A data de demissão deve ser posterior à data de "
                "admissão."
                if demissao == admissao
                else "A data de demissão não pode ser anterior à data de "
                "admissão."
            },
            status=400,
        )

    return None


def modal_data_demissao_colaborador(id_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    hoje = datetime.today().date()
    contexto = {
        "colaborador": colaborador,
        "hoje": hoje.strftime("%Y-%m-%d"),
    }
    modal_html = html_data.html_modal_data_demissao_colaborador(
        request, contexto
    )
    return JsonResponse({"modal_html": modal_html})


def atualizar_cartao_ponto_rescisao(id_pessoal, demissao):
    _, ultimo_dia_mes = primeiro_e_ultimo_dia_do_mes(
        demissao.month, demissao.year
    )

    dia_seguinte_demissao = demissao + timedelta(days=1)

    cartao_ponto = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[dia_seguinte_demissao, ultimo_dia_mes],
    )

    if cartao_ponto.exists():
        cartao_ponto.update(
            Ausencia="-------",
            Conducao=0,
            Remunerado=0,
            CarroEmpresa=0,
        )


def excluir_cartao_ponto_mes_seguinte_rescisao(id_pessoal, demissao):
    mes_posterior = demissao.month + 1 if demissao.month < 12 else 1
    ano_posterior = demissao.year if demissao.month < 12 else demissao.year + 1

    primeiro_dia_mes, ultimo_dia_mes = primeiro_e_ultimo_dia_do_mes(
        mes_posterior, ano_posterior
    )
    CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[primeiro_dia_mes, ultimo_dia_mes],
    ).delete()


def excluir_contra_cheque_mes_seguinte_rescisao(id_pessoal, demissao):
    mes = demissao.month
    ano = demissao.year

    mes = 1 if mes == 12 else mes + 1
    ano = ano + 1 if mes == 12 else ano

    data_base = datetime.strptime(f"{ano}-{mes}-1", "%Y-%m-%d")

    contra_cheque = obter_contra_cheque(id_pessoal, data_base, "ADIANTAMENTO")
    if contra_cheque:
        contra_cheque.delete()

    contra_cheque = obter_contra_cheque(id_pessoal, data_base, "PAGAMENTO")
    if contra_cheque:
        contra_cheque.delete()


def save_data_demissao_colaborador(request):
    id_pessoal = request.POST.get("id_pessoal")
    demissao_str = request.POST.get("demissao")

    if not id_pessoal or not demissao_str:
        return {"mensagem": "Parâmetros inválidos"}

    try:
        demissao = datetime.strptime(demissao_str, "%Y-%m-%d")
    except ValueError:
        return {"mensagem": "Formato de data inválido"}

    registrar_contra_cheque(id_pessoal, demissao, "RESCISÃO")

    atualizar_cartao_ponto_rescisao(id_pessoal, demissao)
    excluir_cartao_ponto_mes_seguinte_rescisao(id_pessoal, demissao)
    excluir_contra_cheque_mes_seguinte_rescisao(id_pessoal, demissao)

    Pessoal.objects.filter(idPessoal=id_pessoal).update(DataDemissao=demissao)

    return {"mensagem": "Data de demissão inserida com sucesso"}


def data_demissao_html_data(request, contexto):
    """Consultar Documentação Sistema Efetiva"""
    data = {}
    html_functions = [
        html_data.html_card_foto_colaborador,
    ]

    return gerar_data_html(html_functions, request, contexto, data)


def create_contexto_eventos_rescisorios_colaborador(request):
    """Consultar Documentação Sistema Efetiva"""
    id_pessoal = request.GET.get("id_pessoal")
    eventos = constants.EVENTOS_RESCISORIOS
    motivos = constants.MOTIVOS_DEMISSAO
    aviso_previo = constants.AVISO_PREVIO

    return {
        "id_pessoal": id_pessoal,
        "eventos": eventos,
        "motivos": motivos,
        "aviso_previo": aviso_previo,
        "mensagem": "SELECIONAR EVENTOS",
    }


def data_eventos_html_data(request, contexto):
    data = {}
    html_functions = [
        html_data.html_card_eventos_rescisorios_colaborador,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def calcular_rescisao_saldo_salario(colaborador):
    id_pessoal = colaborador.id_pessoal
    demissao = colaborador.dados_profissionais.data_demissao

    processar_contra_cheque_mes_rescisao(id_pessoal, demissao)
    contra_cheque = obter_contra_cheque(id_pessoal, demissao, "PAGAMENTO")
    atualiza_contra_cheque_item_salario(id_pessoal, demissao, contra_cheque)
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque_id=contra_cheque.idContraCheque
    ).order_by("Registro")

    return {"contra_cheque_itens": contra_cheque_itens}


def verbas_rescisorias(request):
    id_pessoal = request.POST.get("id_pessoal")

    motivos_dict = dict(constants.MOTIVOS_DEMISSAO)
    motivo_selecionado = request.POST.get("motivo")
    motivo = motivos_dict.get(motivo_selecionado)

    saldo_salario = request.POST.get("saldo_salario")
    ferias_vencidas = request.POST.get("ferias_vencidas")
    ferias_proporcionais = request.POST.get("ferias_proporcionais")
    decimo_terceiro_proporcional = request.POST.get(
        "decimo_terceiro_proporcional"
    )

    colaborador = classes.Colaborador(id_pessoal)

    contexto = {"colaborador": colaborador, "motivo": motivo}

    contexto.update(
        calcular_rescisao_saldo_salario(colaborador)
        if saldo_salario.lower() == "true"
        else {"saldo_salario": None}
    )

    contexto.update(
        calcular_ferias_vencidas(colaborador)
        if ferias_vencidas.lower() == "true"
        else {"ferias_vencidas_valor": None}
    )

    contexto.update(
        calcular_ferias_proporcionais(colaborador)
        if ferias_proporcionais.lower() == "true"
        else {"ferias_valor": None}
    )

    contexto.update(
        calcular_decimo_terceiro_proporcional(colaborador)
        if decimo_terceiro_proporcional.lower() == "true"
        else {"decimo_terceiro_valor": None}
    )

    contexto.update(calcular_pagamento_ferias_proporcionais(colaborador))

    contexto.update({"mensagem": "Rescião Calculada"})

    hoje = datetime.today()
    locale.setlocale(locale.LC_TIME, "pt_BR.utf8")
    data_extenso = hoje.strftime("São Paulo, %d de %B de %Y.")
    contexto.update({"data_extenso": data_extenso})

    return contexto
