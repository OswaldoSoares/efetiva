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


@csrf_exempt
def registrar_credencial(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)

        id_pessoal = data["id_pessoal"]
        credential_id = data["credentialId"]
        attestation_object_b64 = data["attestationObject"]

        if FidoCredential.objects.filter(idPessoal_id=id_pessoal).exists():
            return JsonResponse({"error": "Credencial registrada em outro dispositivo"}, status=403)

        attestation_byte = websafe_decode(attestation_object_b64)
        att_obj = AttestationObject(attestation_byte)

        cose_key = att_obj.auth_data.credential_data.public_key
        cose_dict = dict(cose_key)

        x_bytes = cose_dict[-2]
        y_bytes = cose_dict[-3]

        x = int.from_bytes(x_bytes, byteorder="big")
        y = int.from_bytes(y_bytes, byteorder="big")

        public_numbers = ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1())
        public_key = public_numbers.public_key(default_backend())

        public_key_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ).decode()

        FidoCredential.objects.create(
            credential_id=credential_id,
            public_key_pem=public_key_pem,
            idPessoal_id=id_pessoal,
        )

        return JsonResponse({"status": "Credencial registrada com sucesso"})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return JsonResponse({"error": f"Erro ao registrar credencial: {str(e)}"}, status=500)


@csrf_exempt
def fido2_login(request):
    if request.method != "POST":
        return JsonResponse({"error": "Método não permitido"}, status=405)

    try:
        data = json.loads(request.body)

        credential_id = data["credentialId"]
        authenticator_data = base64.urlsafe_b64decode(data["authenticatorData"] + '==')
        client_data_json = base64.urlsafe_b64decode(data["clientDataJSON"] + '==')
        signature = base64.urlsafe_b64decode(data["signature"] + '==')
        challenge = base64.urlsafe_b64decode(data["challenge"] + '==')
        id_pessoal = data["idPessoal"]
        cpf = data["cpf"]


        colarador = Pessoal.objects.get(idPessoal=id_pessoal)

        cred = FidoCredential.objects.filter(credential_id=credential_id).first()
        if not cred:
            return JsonResponse({"error": "Credencial não encontrada"}, status=400)

        public_key = serialization.load_pem_public_key(cred.public_key_pem.encode())

        client_data = json.loads(client_data_json.decode())
        if base64.urlsafe_b64decode(client_data["challenge"] + '==') != challenge:
            return JsonResponse({"error": "Challenge inválido"}, status=400)


        digest = hashes.Hash(hashes.SHA256())
        digest.update(client_data_json)
        client_data_hash = digest.finalize()

        signed_data = authenticator_data + client_data_hash
        public_key.verify(signature, signed_data, ec.ECDSA(hashes.SHA256()))

        tz = get_current_timezone()
        inicio_dia = make_aware(datetime.combine(localdate(), time.min), timezone=tz)
        fim_dia = make_aware(datetime.combine(localdate(), time.max), timezone=tz)

        registros = RegistroPonto.objects.filter(
            idPessoal_id=id_pessoal,
            horario__range=(inicio_dia, fim_dia)
        )

        entrada = registros.filter(tipo="entrada").order_by("horario").first()
        saida = registros.filter(tipo="saida").order_by("horario").last()

        return JsonResponse({
            "id_pessoal": id_pessoal,
            "cpf": cpf,
            "nome": nome_curto(colarador.Nome),
            "entrada": localtime(entrada.horario).strftime("%H:%M:%S") if entrada else None,
            "saida": saida.horario.strftime("%H:%M:%S") if saida else None,
        })

    except Exception as e:
        return JsonResponse({"erro": str(e)}, status=400)

