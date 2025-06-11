""" Responsável pelo logica do upload de documentos """
import re
from collections import Counter
from typing import List, Dict
from core import constants
from website.models import FileUpload


def remove_prefix_suffix(
    text: str, prefix: str, suffix: str, sep: str = "_-_"
) -> str:
    """
    Remove prefixo e sufixo formatados com um separador específico.

    Exemplo: 'DOCUMENTO_-_Atestado Médico_-_0023' -> 'Atestado Médico'
    """
    if text.startswith(prefix + sep):
        text = text[len(prefix + sep) :]  # noqa: E203
    if text.endswith(sep + suffix):
        text = text[: -len(sep + suffix)]
    return text
