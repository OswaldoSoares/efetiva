""" Responsável pelo resscisão do colaborador """
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal
from typing import Any, List, Optional
from dateutil.relativedelta import relativedelta
from django.db.models import QuerySet, Sum
from django.http import JsonResponse
from core import constants
from core.tools import obter_mes_por_numero, primeiro_e_ultimo_dia_do_mes
from pessoas import classes
from pessoas import html_data
from pessoas.facade import (
    atualiza_contra_cheque_item_salario,
    atualizar_contra_cheque_pagamento,
    atualizar_ou_adicionar_contra_cheque_item,
    gerar_data_html,
    get_or_create_contra_cheque,
    meses_proporcionais_decimo_terceiro,
    obter_contra_cheque,
    obter_evento_ou_erro,
    registrar_contra_cheque,
)
from pessoas.facades.ferias import (
    calcular_dias_ferias_proporcionais,
    faltas_periodo_aquisitivo,
    meses_proporcionais_ferias,
)
from pessoas.models import (
    Aquisitivo,
    CartaoPonto,
    ContraCheque,
    ContraChequeItens,
    Ferias,
    Pessoal,
)


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


def adicionar_itens_no_contra_cheque_rescisao(
    contra_cheque_rescisao: ContraCheque,
    contra_cheque_itens_pagamento: QuerySet[ContraChequeItens],
) -> None:
    """
    Função que adicionar itens no contra cheque rescisao.

    Args:
        contra_cheque_rescisao (ContraCheque): Descrição do parâmetro
    contra_cheque_rescisao
        contra_cheque_itens_pagamento (QuerySet[ContraChequeItens]):
    Descrição do parâmetro contra_cheque_itens_pagamento

    Returns:
        None: Descrição do retorno
    """
    rubrica_saldo_salario = constants.CODIGO_SALARIO
    descricao_salario = constants.DESCRICAO_SALARIO
    evento_lookup = {evento.codigo: evento for evento in constants.EVENTOS_CONTRA_CHEQUE}

    ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_rescisao
    ).delete()

    with transaction.atomic():  # type: ignore
        for item in contra_cheque_itens_pagamento:
            codigo = (
                rubrica_saldo_salario
                if item.Descricao == descricao_salario
                else item.Codigo
            )
            print(descricao_salario, rubrica_saldo_salario, codigo)
            evento = obter_evento_ou_erro(evento_lookup, codigo)

            atualizar_ou_adicionar_contra_cheque_item(
                evento.descricao,
                item.Valor,
                item.Registro,
                item.Referencia,
                codigo,
                contra_cheque_rescisao.idContraCheque,
            )


def processar_contra_cheque_mes_rescisao(
    id_pessoal: int, demissao: date
) -> List[Any]:
    mes = demissao.month
    ano = demissao.year
    mes_por_extenso = obter_mes_por_numero(mes)

    tipo_rescisao = constants.TIPO_CONTRA_CHEQUE_RESCISAO
    tipo_pagamento = constants.TIPO_CONTRA_CHEQUE_PAGAMENTO
    campo_codigo = constants.CAMPO_CODIGO_CONTRA_CHEQUE_ITEM

    contra_cheque_rescisao, _ = get_or_create_contra_cheque(
        mes_por_extenso, ano, tipo_rescisao, id_pessoal
    )
    print(type(contra_cheque_rescisao))

    contra_cheque_pagamento, _ = get_or_create_contra_cheque(
        mes_por_extenso, ano, tipo_pagamento, id_pessoal
    )

    atualizar_contra_cheque_pagamento(
        id_pessoal, mes, ano, contra_cheque_pagamento
    )

    contra_cheque_itens_pagamento = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_pagamento
    ).order_by(campo_codigo)
    print(type(contra_cheque_itens_pagamento))

    adicionar_itens_no_contra_cheque_rescisao(
        contra_cheque_rescisao, contra_cheque_itens_pagamento
    )

    contra_cheque_itens_rescisao = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque_rescisao
    ).order_by(campo_codigo)

    return contra_cheque_itens_rescisao


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


def calcular_ferias_vencidas(colaborador):
    aquisitivos = Aquisitivo.objects.filter(
        idPessoal=colaborador.id_pessoal
    ).order_by("-DataInicial")

    salario = colaborador.salarios.salarios.Salario
    salario_dia = salario / 30

    ferias_vencidas = []

    for aquisitivo in aquisitivos:
        if (aquisitivo.DataFinal - aquisitivo.DataInicial).days + 1 < 365:
            continue

        faltas = faltas_periodo_aquisitivo(colaborador.id_pessoal, aquisitivo)

        dias_proporcionais = Decimal(
            calcular_dias_ferias_proporcionais(len(faltas), 12)
        )

        dias_gozo = sum(
            (feria.DataFinal - feria.DataInicial).days + 1
            for feria in Ferias.objects.filter(
                idAquisitivo_id=aquisitivo.idAquisitivo
            )
        )

        dias_a_pagar = max(dias_proporcionais - dias_gozo, 0)
        valor_pagar = (dias_a_pagar * salario_dia).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        um_terco_pagar = (valor_pagar / 3).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )

        data_ionicial_str = datetime.strftime(
            aquisitivo.DataInicial, "%d/%m/%Y"
        )
        data_final_str = datetime.strftime(aquisitivo.DataFinal, "%d/%m/%Y")
        periodo = f"{data_ionicial_str} a {data_final_str}"

        if dias_a_pagar > 0:
            ferias_vencidas.append(
                {
                    "periodo": periodo,
                    "dias_faltas": faltas,
                    "numero_faltas": len(faltas),
                    "dias_proporcionais": dias_proporcionais,
                    "dias_gozo": dias_gozo,
                    "dias_pagar": dias_a_pagar,
                    "valor_pagar": valor_pagar,
                    "um_terco_pagar": um_terco_pagar,
                }
            )

    return {"ferias_vencidas": ferias_vencidas}


def calcular_ferias_proporcionais(colaborador):
    """Consultar Documentação Sistema Efetiva"""
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=colaborador.id_pessoal)
        .order_by("-DataInicial")
        .first()
    )

    if not aquisitivo:
        aquisitivo = Aquisitivo.objects.create(
            DataInicial=colaborador.dados_profissionais.data_admissao,
            DataFinal=colaborador.dados_profissionais.data_demissao,
            idPessoal_id=colaborador.id_pessoal,
        )
    else:
        aquisitivo.DataFinal = colaborador.dados_profissionais.data_demissao
        aquisitivo.save()

    faltas = faltas_periodo_aquisitivo(
        colaborador.id_pessoal, aquisitivo
    )

    dozeavos = meses_proporcionais_ferias(
        aquisitivo.DataInicial, aquisitivo.DataFinal
    )

    dias = Decimal(
        calcular_dias_ferias_proporcionais(len(faltas), dozeavos)
    )

    salario_base = colaborador.salarios.salarios.Salario
    valor = (salario_base / 30 * dias).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    um_terco = (valor / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    return {
        "ferias_valor": valor,
        "ferias_meses": dozeavos,
        "ferias_um_terco": um_terco,
    }


def calcular_decimo_terceiro_proporcional(colaborador):
    """Consultar Documentação Sistema Efetiva"""
    data_admissao = colaborador.dados_profissionais.data_admissao
    data_demissao = colaborador.dados_profissionais.data_demissao
    hoje = datetime.today().date()
    inicio_ano = date(hoje.year, 1, 1)
    fim_ano = date(hoje.year, 12, 31)

    if hoje.year > data_demissao.year:
        inicio_ano = date(hoje.year - 1, 1, 1)
        fim_ano = date(hoje.year - 1, 12, 31)

    parcelas_pagas = ContraCheque.objects.filter(
        idPessoal=colaborador.id_pessoal,
        Descricao="DECIMO TERCEIRO",
        AnoReferencia=data_demissao.year,
        Pago=True,
    )

    total_valor = (
        parcelas_pagas.aggregate(soma_valor=Sum("Valor"))["soma_valor"] or 0
    )

    data_inicial = data_admissao if data_admissao > inicio_ano else inicio_ano
    data_final = data_demissao if data_demissao < fim_ano else fim_ano

    dozeavos = meses_proporcionais_decimo_terceiro(data_inicial, data_final)

    salario_base = colaborador.salarios.salarios.Salario
    valor = (salario_base / 12 * dozeavos).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )

    return {
        "decimo_terceiro_valor": valor,
        "decimo_terceiro_meses": dozeavos,
        "decimo_terceiro_parcelas_pagas": parcelas_pagas,
        "decimo_terceiro_total_pago": total_valor,
    }


def calcular_pagamento_ferias_proporcionais(colaborador):
    """Consultar Documentação Sistema Efetiva"""
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=colaborador.id_pessoal)
        .order_by("-DataInicial")
        .first()
    )

    data_inicial = aquisitivo.DataInicial
    data_final_original = data_inicial + relativedelta(years=1, days=-1)
    mes_por_extenso = constants.MESES[data_final_original.month]
    ano = data_final_original.year

    contra_cheque_ferias = ContraCheque.objects.filter(
        idPessoal=colaborador.id_pessoal,
        MesReferencia=mes_por_extenso,
        AnoReferencia=ano,
        Descricao="FERIAS",
    ).first()

    if contra_cheque_ferias and contra_cheque_ferias.Pago:
        total_ferias_paga = ContraChequeItens.objects.filter(
            idContraCheque=contra_cheque_ferias.idContraCheque, Registro="C"
        ).aggregate(total=Sum("Valor")).get("total") or Decimal(0)

        return {"desconto_ferias": total_ferias_paga}

    return {"ferias_nao_paga": "ferias_nao_paga"}


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
