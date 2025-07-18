"""
Módulo responsável pelo registro de ponto e contraoe do cartão de ponto.
"""
import json
from datetime import datetime, time
from django.contrib.auth.hashers import check_password
from django.http import JsonResponse
from django.utils.timezone import get_current_timezone, localdate, localtime, make_aware
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
from pessoas.models import DocPessoal, RegistroPonto, SenhaAppPonto
from core.tools import nome_curto


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
    print(request.body.decode())
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
    print(request.body.decode())
    try:
        data = json.loads(request.body)

        cpf = data["cpf"]
        tipo = data["tipo"]
        id_pessoal = data["id_pessoal"]

        print(id_pessoal)

        RegistroPonto.objects.create(
            tipo=tipo,
            idPessoal_id=id_pessoal,
        )

        entrada, saida = verificar_registro_colaborador_hoje(id_pessoal)

        return JsonResponse({
            "status": "Ponto registrada com sucesso",
            "entrada": localtime(entrada.horario).strftime("%H:%M:%S") if entrada else None,
            "saida": localtime(saida.horario).strftime("%H:%M:%S") if saida else None,
        })

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

    print(f"ENTRADA: {entrada} - SAÍDA {saida}")

    return entrada, saida
