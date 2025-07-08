"""
Módulo responsável pelo registro de ponto e contraoe do cartão de ponto.
"""
import base64
import json
from django.http import JsonResponse
from django.utils.timezone import get_current_timezone, make_aware
from django.utils.timezone import localdate, localtime
from django.views.decorators.csrf import csrf_exempt


