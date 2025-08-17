"""Responsável pelas férias do colaborador"""

from datetime import datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

from dateutil.relativedelta import relativedelta
from django.http import JsonResponse

from core.constants import MESES
from core.tools import (
    get_mensagem,
    get_saldo_contra_cheque,
    obter_mes_por_numero,
)
from pessoas import classes, html_data
from pessoas.facades.ponto import obter_cartao_ponto_mes
from pessoas.models import (
    Aquisitivo,
    CartaoPonto,
    ContraCheque,
    ContraChequeItens,
    Ferias,
    Salario,
)


def faltas_periodo_aquisitivo(id_pessoal: int, aquisitivo) -> list[str]:
    """
    Retorna uma lista com as datas das faltas não remuneradas registradas
    durante o período aquisitivo do colaborador.

    De acordo com a CLT, faltas injustificadas podem impactar diretamente
    no cálculo dos dias de férias a que o colaborador tem direito.

    Args:
        id_pessoal (int): ID do colaborador.
        aquisitivo: Objeto representando o período aquisitivo.

    Returns:
        List[str]: Lista de datas (formatadas como "dd/mm/yyyy") das faltas
                   não remuneradas.
    """
    inicio = aquisitivo.DataInicial
    final = aquisitivo.DataFinal

    dias_faltas = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[inicio, final],
        Ausencia="FALTA",
        Remunerado=False,
    ).values_list("Dia", flat=True)

    return [datetime.strftime(dia, "%d/%m/%Y") for dia in dias_faltas]


def meses_proporcionais_ferias(data_inicial, data_final):
    """
    Calcula a quantidade de meses proporcionais de férias com base no
    período entre a data inicial e final do contrato (ou até a data atual).

    Conforme orientação da CLT, cada mês completo de trabalho gera direito
    a 1/12 de férias. Um mês é considerado completo se houver ao menos 15
    dias trabalhados.

    Args:
        data_inicial (date): Data de início do período aquisitivo.
        data_final (date): Data de fim do contrato ou do período.

    Returns:
        int: Quantidade de meses proporcionais de férias (doze avos).
    """
    hoje = datetime.today().date()
    periodo = relativedelta(
        data_final if data_final < hoje else hoje, data_inicial
    )

    return periodo.months + (1 if periodo.days >= 15 else 0)


def calcular_dias_ferias_proporcionais(faltas, dozeavos):
    """
    Calcula a quantidade de dias de férias proporcionais de acordo com as
    faixas de faltas injustificadas, conforme prevê a CLT (Art. 130).

    Faixas aplicadas:
        - Até 5 faltas: 30 dias (2.5 dias por mês)
        - 6 a 14 faltas: 24 dias (2.0 dias por mês)
        - 15 a 23 faltas: 18 dias (1.5 dias por mês)
        - 24 a 32 faltas: 12 dias (1.0 dia por mês)
        - Acima de 32 faltas: 0 dias

    Args:
        faltas (int): Número de faltas injustificadas.
        dozeavos (int): Meses de férias proporcionais adquiridos.

    Returns:
        float: Quantidade proporcional de dias de férias devidos.
    """
    faixas = [
        (5, 2.5),  # Até 5 faltas
        (14, 2.0),  # De 6 a 14 faltas
        (23, 1.5),  # De 15 a 23 faltas
        (32, 1.0),  # De 24 a 32 faltas
    ]

    multiplicador = next(
        (valor for limite, valor in faixas if faltas <= limite), 0
    )

    return multiplicador * dozeavos


def calcula_valores_ferias(salario, faltas, data_inicial, data_final):
    """
    Calcula os valores financeiros referentes às férias proporcionais,
    incluindo:
    - Valor das férias (dias proporcionais x salário diário)
    - Adicional de 1/3 constitucional
    - Total a ser pago

    Cálculos realizados conforme a CLT (Art. 129 a 130 e 142).

    Args:
        salario (Decimal): Valor do salário base mensal.
        faltas (int): Total de faltas injustificadas no período.
        data_inicial (date): Data inicial do período aquisitivo.
        data_final (date): Data final do período aquisitivo.

    Returns:
        Tuple[Decimal, Decimal, Decimal, Decimal]:
            - dias: Dias proporcionais de férias
            - valor: Valor base das férias
            - um_terco: Adicional de 1/3 constitucional
            - total: Valor total a ser pago (férias + 1/3)
    """
    meses = meses_proporcionais_ferias(data_inicial, data_final)
    dias = Decimal(calcular_dias_ferias_proporcionais(faltas, meses))
    valor = (salario / 30 * dias).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    um_terco = (valor / 3).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    total = valor + um_terco

    return dias, valor, um_terco, total


def anota_dados_ferias(id_pessoal, aquisitivos):
    """
    Processa cada período aquisitivo de um colaborador e anota os dados de
    férias calculados, incluindo:
        - Faltas
        - Dias de férias proporcionais
        - Valor das férias
        - Adicional de 1/3 constitucional
        - Valor total

    Args:
        id_pessoal (int): ID do colaborador.
        aquisitivos (QuerySet): Lista de objetos de períodos aquisitivos.

    Returns:
        QuerySet: Lista de objetos aquisitivos com os atributos anotados.
    """
    salario = (
        Salario.objects.filter(idPessoal=id_pessoal)
        .values_list("Salario", flat=True)
        .first()
    )

    for aquisitivo in aquisitivos:
        faltas = len(faltas_periodo_aquisitivo(id_pessoal, aquisitivo))
        dias, valor, um_terco, total = calcula_valores_ferias(
            salario, faltas, aquisitivo.DataInicial, aquisitivo.DataFinal
        )

        aquisitivo.faltas = faltas
        aquisitivo.dias = dias
        aquisitivo.valor = valor
        aquisitivo.um_terco = um_terco
        aquisitivo.total = total

    return aquisitivos


def create_contexto_ferias_colaborador(id_pessoal) -> dict:
    """
    Retorna um dicionário com os dados de férias do colaborador, contendo:
    - Lista de períodos aquisitivos, com valores calculados
    - Lista de registros de gozo de férias

    Esse contexto é útil para exibição em templates ou consumo por APIs.

    Args:
        id_pessoal (int): ID do colaborador.

    Returns:
        Dict: {
            "aquisitivos": Lista de períodos aquisitivos com dados anotados,
            "gozo_ferias": Lista de períodos de gozo de férias
        }
    """
    aquisitivos = Aquisitivo.objects.filter(idPessoal=id_pessoal).reverse()
    aquisitivos = anota_dados_ferias(id_pessoal, aquisitivos)
    gozo_ferias = Ferias.objects.filter(idPessoal=id_pessoal).reverse()

    return {"aquisitivos": aquisitivos, "gozo_ferias": gozo_ferias}


def obter_dias_para_gozo_ferias(id_pessoal):
    dict_ferias = create_contexto_ferias_colaborador(id_pessoal)
    for aquisitivo in reversed(list(dict_ferias["aquisitivos"])):
        gozo_ferias = dict_ferias["gozo_ferias"].filter(
            idAquisitivo_id=aquisitivo.idAquisitivo
        )
        dias = 0
        for gozo in gozo_ferias:
            dias += (gozo.DataFinal - gozo.DataInicial).days + 1

        if aquisitivo.dias > dias:
            dias_restantes = round(aquisitivo.dias - dias)
            return dias_restantes, aquisitivo

    return 0, False


def modal_gozo_ferias_colaborador(id_pessoal, request):
    colaborador = classes.Colaborador(id_pessoal)
    dias_restantes, aquisitivo = obter_dias_para_gozo_ferias(id_pessoal)
    hoje = datetime.today().date()
    data_final = hoje + timedelta(dias_restantes - 1)
    contexto = {
        "colaborador": colaborador,
        "aquisitivo": aquisitivo,
        "dias_restantes": dias_restantes,
        "hoje": hoje.strftime("%Y-%m-%d"),
        "data_final": data_final.strftime("%Y-%m-%d"),
    }
    modal_html = html_data.html_modal_gozo_ferias_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})


def validar_dias_ferias(id_pessoal, dias_ferias):
    dias_restantes, _ = obter_dias_para_gozo_ferias(id_pessoal)

    return not int(dias_ferias) > dias_restantes


def validar_data_ferias(id_pessoal, data):
    data = datetime.strptime(data, "%Y-%m-%d").date()
    mes = data.month
    mes_extenso = MESES[int(mes)]
    ano = data.year

    contra_cheque = ContraCheque.objects.filter(
        idPessoal_id=id_pessoal,
        MesReferencia=mes_extenso,
        AnoReferencia=ano,
        Descricao="PAGAMENTO",
    ).first()

    return not contra_cheque and contra_cheque.Pago


def validar_admitido_ferias(colaborador, data):
    data = datetime.strptime(data, "%Y-%m-%d").date()
    admissao = colaborador.dados_profissionais.data_admissao

    return not data < admissao


def validar_gozo_ferias_colaborador(request):
    if request.method != "POST":
        return False

    id_pessoal = request.POST.get("id_pessoal")
    data_inicio = request.POST.get("data_inicio")
    dias_ferias = request.POST.get("dias")
    data_fim = request.POST.get("data_fim")

    colaborador = classes.Colaborador(id_pessoal)

    if not validar_dias_ferias(id_pessoal, dias_ferias):
        return get_mensagem("pefe0002", dias=dias_ferias)

    if not validar_data_ferias(id_pessoal, data_inicio):
        return get_mensagem("pefe0003")

    if not validar_data_ferias(id_pessoal, data_fim):
        return get_mensagem("pefe0004")

    if not validar_admitido_ferias(colaborador, data_inicio):
        return get_mensagem("pefe0005")


def atualizar_cartao_ponto_ferias(id_pessoal, data_inicio, data_fim):
    cartao_ponto = CartaoPonto.objects.filter(
        idPessoal=id_pessoal, Dia__range=[data_inicio, data_fim]
    )

    try:
        cartao_ponto.update(
            Ausencia="FÉRIAS",
            Conducao=False,
            Remunerado=False,
            Alteracao="ROBOT",
        )

        return True

    except Exception:
        return get_mensagem("pefe0001")


def save_gozo_ferias_colaborador(request):
    id_pessoal = int(request.POST.get("id_pessoal"))
    data_inicio_str = request.POST.get("data_inicio")
    data_inicio = datetime.strptime(data_inicio_str, "%Y-%m-%d")
    data_fim_str = request.POST.get("data_fim")
    data_fim = datetime.strptime(data_fim_str, "%Y-%m-%d")

    _, aquisitivo = obter_dias_para_gozo_ferias(id_pessoal)

    obter_cartao_ponto_mes(id_pessoal, data_inicio.month, data_inicio.year)
    if data_inicio.month != data_fim.month:
        obter_cartao_ponto_mes(id_pessoal, data_fim.month, data_fim.year)

    try:
        Ferias.objects.create(
            DataInicial=data_inicio,
            DataFinal=data_fim,
            idAquisitivo_id=aquisitivo.idAquisitivo,
            idPessoal_id=id_pessoal,
        )

        atualizar_cartao_ponto_ferias(id_pessoal, data_inicio, data_fim)
    except Exception:
        return get_mensagem("pefe0006")

    return get_mensagem("pefe0001")


def obter_contra_cheque_itens_ferias(contra_cheque, feria):
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque.idContraCheque
    )

    if not contra_cheque_itens.exists():
        colaborador = classes.Colaborador(feria.idPessoal_id)
        salario = colaborador.salarios.salarios.Salario
        dias_ferias = feria.DataFinal.day - feria.DataInicial.day + 1
        valor_ferias = (salario / 30 * dias_ferias).quantize(
            Decimal("0.01"), rounding=ROUND_HALF_UP
        )
        terco_ferias = (valor_ferias / 3).quantize(
            Decimal("0.00"), rounding=ROUND_HALF_UP
        )

        for i in range(2):
            descricao = "FÉRIAS" if i == 0 else "1/3 FÉRIAS"
            valor = valor_ferias if i == 0 else terco_ferias
            referencia = dias_ferias if i == 0 else "1/3"
            codigo = "1020" if i == 0 else "1019"

            ContraChequeItens.objects.create(
                Descricao=descricao,
                Valor=valor,
                Registro="C",
                Referencia=referencia,
                idContraCheque_id=contra_cheque.idContraCheque,
                Codigo=codigo,
                Vales_id=0,
            )

            contra_cheque_itens = ContraChequeItens.objects.filter(
                idContraCheque=contra_cheque.idContraCheque
            )

    return contra_cheque_itens


def obter_contra_cheque_ferias(request):
    id_ferias = request.GET.get("id_ferias")

    feria = Ferias.objects.filter(idFerias=id_ferias).first()
    mes_inicio = feria.DataInicial.month
    ano_inicio = feria.DataInicial.year
    mes_extenso = obter_mes_por_numero(mes_inicio)

    qs = ContraCheque.objects.filter(
        idContraCheque=feria.idContraCheque_id
    )

    if not qs.exists():
        contra_cheque = ContraCheque.objects.create(
            MesReferencia=mes_extenso,
            AnoReferencia=ano_inicio,
            idPessoal_id=feria.idPessoal_id,
            Descricao="FERIAS"
        )

        if feria.idContraCheque_id is None:
            feria.idContraCheque_id=contra_cheque.idContraCheque
            feria.save()

    else:
        contra_cheque = qs.first()

    contra_cheque_itens = obter_contra_cheque_itens_ferias(
        contra_cheque, feria
    )

    return {
        "id_pessoal": feria.idPessoal_id,
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
        **get_saldo_contra_cheque(contra_cheque_itens),
        **get_mensagem(
            "pefe0007",
            inicio=datetime.strftime(feria.DataInicial, "%d/%m/%Y"),
            fim=datetime.strftime(feria.DataFinal, "%d/%m/%Y"),
        ),
    }
