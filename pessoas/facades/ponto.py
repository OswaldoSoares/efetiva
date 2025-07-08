"""
Módulo responsável pelo registro de ponto e contraoe do cartão de ponto.
"""
import base64
import json
from django.http import JsonResponse
from django.utils.timezone import get_current_timezone, make_aware
from django.utils.timezone import localdate, localtime
from django.views.decorators.csrf import csrf_exempt
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.backends import default_backend
from fido2.webauthn import AttestationObject
from fido2.utils import websafe_decode
from pessoas.models import DocPessoal, FidoCredential, RegistroPonto, Pessoal
from core.tools import nome_curto


def verificar_credencial_por_cpf(request, cpf):
    cpf_formatado = f"{cpf[:3]}.{cpf[3:6]}.{cpf[6:9]}-{cpf[9:]}"
    try:
        documento = DocPessoal.objects.get(
            TipoDocumento="CPF", Documento=cpf_formatado
        )
    except DocPessoal.DoesNotExist:
        return JsonResponse({"cpf_encontrado": False})

    cred = FidoCredential.objects.filter(idPessoal_id=documento.idPessoal_id)
    tem_credencial = cred.exists()
    liberado_pelo_rh = cred.first().liberado_pelo_rh if cred.exists() else False

    return JsonResponse({
        "cpf_encontrado": True,
        "tem_credencial": tem_credencial,
        "liberado_pelo_rh": liberado_pelo_rh,
        "id_pessoal": documento.idPessoal_id,
        "nome": documento.idPessoal.Nome,
        "nome_curto": nome_curto(documento.idPessoal.Nome),
        "cpf": cpf_formatado,
    })

