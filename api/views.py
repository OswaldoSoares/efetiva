import json
import os
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from webauthn import generate_registration_options,
from webauthn import verify_registartion_response,
from pessoas.models import DocPessoal, CredencialWebAuthn


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from core.tools import nome_curto


def colaborador_por_cpf(request, cpf):
    try:
        documento = DocPessoal.objects.get(TipoDocumento="CPF", Documento=cpf)

        return JsonResponse(
            {
                "id_pessoal": documento.idPessoal_id,
                "nome": documento.idPessoal.Nome,
                "nome_curto": nome_curto(documento.idPessoal.Nome),
                "cpf": cpf,
            }
        )
    except DocPessoal.DoesNotExist:
        return JsonResponse({"error": "CPF Não encontrado"}, status=404)


class RegistroBiometriaAPIView(APIView):
    def post(self, request):
        data = request.data
        username = data.get("username")
        credential_id = data.get("credential_id")
        public_key = data.get("public_key")
        sign_count = data.get("sign_count")

        try:
            cpf_documento = DocPessoal.objects.get(
                TipoDocumento="CPF", Documento=username
            )
            id_pessoal = cpf_documento.idPessoal_id

            # Evita duplicação
            if CredencialWebAuthn.objects.filter(
                credential_id=credential_id
            ).exists():
                return Response(
                    {"error": "Credencial já registrada."}, status=400
                )

            CredencialWebAuthn.objects.create(
                idPessoal_id=id_pessoal,
                credential_id=credential_id,
                public_key=public_key,
                sign_count=sign_count,
            )
            return Response({"status": "registrado com sucesso"})

        except cpf_documento.DoesNotExist:
            return Response({"error": "CPF não encontrado"}, status=404)

        except Exception as e:
            return Response({"error": str(e)}, status=500)
