"""
Módulo responsável pelo registro de ponto e contrale do cartão de ponto.
"""
import calendar
import json
from datetime import datetime, date, time, timedelta
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.timezone import (
    get_current_timezone,
    localdate,
    localtime,
    make_aware,
)
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from pessoas import classes
from pessoas.models import (
    CartaoPonto,
    DocPessoal,
    Ferias,
    RegistroPonto,
    SenhaAppPonto,
)
from core.tools import (
    nome_curto,
    obter_feriados_sabados_domingos_mes,
    primeiro_e_ultimo_dia_do_mes,
)


@require_GET
def verificar_identidade(request, cpf):
    cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

    try:
        documento = DocPessoal.objects.get(
            TipoDocumento="CPF", Documento=cpf_formatado
        )

    except DocPessoal.DoesNotExist: # type: ignore[attr-defined]
        return JsonResponse(
            {"error": "CPF não encontrado", "tem_cpf": False},
            status=200
        )

    tem_senha = SenhaAppPonto.objects.filter(
        idPessoal=documento.idPessoal_id
    ).exists()

    return JsonResponse({
        "tem_cpf": True,
        "tem_senha": tem_senha,
        "id_pessoal": documento.idPessoal_id,
        "nome": nome_curto(documento.idPessoal.Nome),
        "cpf": cpf_formatado,
    })



@csrf_exempt
def cadastrar_senha(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)
        cpf = data["cpf"]
        senha = data["senha"]

        cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"

        documento = DocPessoal.objects.get(
            TipoDocumento="CPF", Documento=cpf_formatado
        )

    except DocPessoal.DoesNotExist: # type: ignore[attr-defined]
        return JsonResponse({"error": "Erro ao cadastrar senha"}, status=400)

    senha_obj = SenhaAppPonto(idPessoal_id=documento.idPessoal_id)
    senha_obj.set_senha(senha)

    return JsonResponse({"success": "Senha cadastrada com sucesso"}, status=200)


@csrf_exempt
def autenticar(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)

        senha = data["senha"]
        id_pessoal = data["id_pessoal"]

        senha_app = SenhaAppPonto.objects.filter(
            idPessoal_id=id_pessoal
        ).first()

        if check_password(senha, senha_app.senha):
            entrada, saida = verificar_registro_colaborador_hoje(id_pessoal)

            return JsonResponse({
                "success": "Autenticação realizada",
                "entrada": localtime(entrada.horario).strftime("%H:%M:%S") if entrada else None,
                "saida": localtime(saida.horario).strftime("%H:%M:%S") if saida else None,
            }, status=200)
        else:
            return JsonResponse({"error": "Senha não confere, tentar novamente"}, status=200)

    except SenhaAppPonto.DoesNotExist: # type: ignore[attr-defined]
        return JsonResponse({"error": "Senha não cadastrada"}, status=200)


@csrf_exempt
def registrar_ponto(request):
    try:
        data = json.loads(request.body)

        tipo = data["tipo"]
        id_pessoal = data["id_pessoal"]

        RegistroPonto.objects.create(
            tipo=tipo,
            idPessoal_id=id_pessoal,
        )

        entrada, saida = verificar_registro_colaborador_hoje(id_pessoal)

        return JsonResponse({
            "status": "Ponto registrada com sucesso",
            "entrada": localtime(entrada.horario).strftime("%H:%M:%S") if entrada else None,
            "saida": localtime(saida.horario).strftime("%H:%M:%S") if saida else None,
        }, status=200)

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)


def verificar_registro_colaborador_hoje(id_pessoal):
    tz = get_current_timezone()
    inicio_dia = make_aware(datetime.combine(localdate(), time.min), timezone=tz)
    fim_dia = make_aware(datetime.combine(localdate(), time.max), timezone=tz)

    registros = RegistroPonto.objects.filter(
        idPessoal_id=id_pessoal,
        horario__range=(inicio_dia, fim_dia)
    )

    entrada = registros.filter(tipo="ENTRADA").order_by("horario").first()
    saida = registros.filter(tipo="SAIDA").order_by("horario").last()

    return entrada, saida


def obter_datas_nao_uteis_mes(primeiro_dia):
    mes = primeiro_dia.month
    ano = primeiro_dia.year
    feriados, domingos, sabados = obter_feriados_sabados_domingos_mes(mes, ano)

    datas_sabados = [
        datetime.strptime(data, "%d/%m/%Y").date() for data in sabados
    ]
    datas_domingos = [
        datetime.strptime(data, "%d/%m/%Y").date() for data in domingos
    ]
    datas_feriados = [
        datetime.strptime(data.split(" - ")[0], "%d/%m/%Y").date()
        for data in feriados
    ]

    return datas_sabados, datas_domingos, datas_feriados


def dia_em_ferias(dia, id_pessoal):
    ferias = Ferias.objects.filter(idPessoal_id=id_pessoal)

    for periodo in ferias:
        if periodo.DataInicial <= dia <= periodo.DataFinal:
            return True
    return False


def aplicar_ausencia_dias_nao_util(cartao, dia, tipos_ausencia):
    for tipo, lista in tipos_ausencia.items():
        if dia in lista:
            cartao.Ausencia = tipo
            cartao.Conducao = False
            cartao.Alteracao = "APP-PONTO"
            cartao.save()
            return True
    return False


def filter_by_local_date(queryset, field_name: str, dia: date):
    """
    Filtra um queryset por um DateTimeField, considerando o dia no
    fuso horário local (TIME_ZONE).

    :param queryset: QuerySet original.
    :param field_name: Nome do campo DateTimeField (como string).
    :param dia: Instância de datetime.date representando o dia local.
    :return: QuerySet filtrado com registros daquele dia no horário local.
    """
    tz = get_current_timezone()

    inicio = make_aware(datetime.combine(dia, datetime.min.time()), timezone=tz)
    fim = make_aware(datetime.combine(dia, datetime.max.time()), timezone=tz)

    filtro = {
        f"{field_name}__range": (inicio, fim)
    }

    return queryset.filter(**filtro)


def obter_horarios(registros_dia):
    entrada = next(
        (
            localtime(r.horario).time() for r in registros_dia
            if r.tipo == "ENTRADA"
        ), None
    )
    saida = next(
        (
            localtime(r.horario).time() for r in reversed(registros_dia)
            if r.tipo == "SAIDA"
        ), None
    )

    return entrada, saida


def processar_dia_util(cartao, dia, nao_uteis, data_implementacao, hoje, vale_transporte):
    if dia < data_implementacao or dia >= hoje or dia in nao_uteis:
        return

    registros_dia = filter_by_local_date(RegistroPonto.objects.filter(
        idPessoal=cartao.idPessoal
    ).order_by("horario"), "horario", dia)

    entrada, saida = obter_horarios(registros_dia)

    cartao.Entrada = entrada if entrada else cartao.Entrada
    cartao.Saida = saida if saida else cartao.Saida

    falta = not entrada and not saida
    cartao.Ausencia = "FALTA" if falta else ""
    cartao.Remunerado = not falta
    cartao.Conducao = vale_transporte and not falta
    cartao.Alteracao = "APP-PONTO"
    cartao.save()


def atualizar_cartao_ponto_pelo_registro_ponto(cartao_ponto):
    primeiro_dia = cartao_ponto.first().Dia
    hoje = datetime.today().date()
    data_implementacao = datetime(2025, 7, 21).date()

    id_pessoal = cartao_ponto.first().idPessoal_id
    colaborador = classes.Colaborador(id_pessoal)
    admissao = colaborador.dados_profissionais.data_admissao
    demissao = colaborador.dados_profissionais.data_demissao
    vale_transporte = colaborador.salarios.salarios.ValeTransporte

    sabados, domingos, feriados = obter_datas_nao_uteis_mes(
        primeiro_dia
    )

    tipos_ausencia = {
        "FERIADO": feriados,
        "SABADO": sabados,
        "DOMINGO": domingos,
    }

    nao_uteis = set(sabados + domingos + feriados)

    for cartao in cartao_ponto:
        dia = cartao.Dia
        vinculo_ativo = admissao <= dia and(not demissao or dia <= demissao)

        if not vinculo_ativo:
            continue

        if dia_em_ferias(dia, id_pessoal):
            continue

        if cartao.Alteracao in {"APP-PONTO", "MANUAL"}:
            continue

        if aplicar_ausencia_dias_nao_util(cartao, dia, tipos_ausencia):
            continue

        processar_dia_util(cartao, dia, nao_uteis, data_implementacao, hoje, vale_transporte)

    return cartao_ponto


def adicionar_cartao_ponto(id_pessoal, mes, ano):
    colaborador = classes.Colaborador(id_pessoal)
    if colaborador.dados_profissionais.tipo_pgto != "MENSALISTA":
        return

    primeiro_dia = date(ano, mes, 1)
    _, total_dias = calendar.monthrange(ano, mes)

    registros = []

    for index in range(total_dias):
        dia = primeiro_dia + timedelta(days=index)

        registros.append(CartaoPonto(
            Dia=dia,
            Entrada="07:00",
            Saida="17:00",
            Ausencia="",
            idPessoal_id=id_pessoal,
            Alteracao="ROBOT",
            Conducao=False,
            Remunerado=True,
            CarroEmpresa=False,
        ))

    CartaoPonto.objects.bulk_create(registros)


def obter_cartao_ponto_mes(id_pessoal, mes, ano):
    primeiro_dia, ultimo_dia = primeiro_e_ultimo_dia_do_mes(mes, ano)

    cartao_ponto = CartaoPonto.objects.filter(
        idPessoal= id_pessoal,
        Dia__range=[primeiro_dia, ultimo_dia]
    )

    if not cartao_ponto.exists():
        adicionar_cartao_ponto(id_pessoal, mes, ano)

        cartao_ponto = CartaoPonto.objects.filter(
            idPessoal= id_pessoal,
            Dia__range=[primeiro_dia, ultimo_dia]
        )

    return atualizar_cartao_ponto_pelo_registro_ponto(cartao_ponto)


def create_contexto_cartao_ponto(id_pessoal, mes, ano):
    cartao_ponto = obter_cartao_ponto_mes(id_pessoal, mes, ano)

    return {"cartao_ponto": cartao_ponto}
