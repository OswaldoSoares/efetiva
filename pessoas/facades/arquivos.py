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


def documentos_arquivados_do_colaborador(id_pessoal: int) -> List[FileUpload]:
    """
    Retorna os arquivos arquivados do colaborador com base no ID formatado.
    """
    inicio_nome_arquivo = "DOCUMENTO"
    id_quatro_caracter = str(id_pessoal).zfill(4)

    return FileUpload.objects.filter(
        DescricaoUpload__startswith=inicio_nome_arquivo,
        DescricaoUpload__endswith=id_quatro_caracter,
    )


def filtrar_tipos_documentos_arquivar(
    documentos_arquivados: List[FileUpload], id_pessoal: int
) -> List[str]:
    """
    Filtra os tipos de documentos que ainda não foram arquivados para o
    colaborador.
    """
    inicio_nome_arquivo = "DOCUMENTO"
    id_quatro_caracter = str(id_pessoal).zfill(4)
    tipos_docs = constants.TIPOS_DOCS.copy()
    tipos_docs_arquivar = constants.TIPOS_DOCUMENTO_PARA_ARQUIVAR.copy()

    for file in documentos_arquivados:
        tipo = remove_prefix_suffix(
            str(file.DescricaoUpload), inicio_nome_arquivo, id_quatro_caracter
        )
        file.descricao = tipo.replace("_", " ")  # type: ignore[attr-defined]

        if tipo in tipos_docs:
            tipos_docs_arquivar.remove(tipo)

    return tipos_docs_arquivar
