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


