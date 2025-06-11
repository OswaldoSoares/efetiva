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


def maior_indice_documentos_arquivados_tipo(
    documentos_arquivados: List[FileUpload], id_pessoal: int
) -> Dict[str, int]:
    """
    Retorna o maior índice numérico (ex: 003) para cada tipo de documento.
    """
    inicio_nome_arquivo = "DOCUMENTO"
    id_quatro_caracter = str(id_pessoal).zfill(4)
    max_indices = {}

    for file in documentos_arquivados:
        tipo_com_indice = remove_prefix_suffix(
            str(file.DescricaoUpload), inicio_nome_arquivo, id_quatro_caracter
        )

        match = re.match(r"^(.*?)(?:_(\d{3}))?$", tipo_com_indice)
        if match:
            tipo_base = match.group(1).replace("_", " ")
            print(tipo_base)
            indice = int(match.group(2)) if match.group(2) else 0
            max_indices[tipo_base] = max(indice, max_indices.get(tipo_base, 0))

    return max_indices


def dict_de_tipos_documentos_arquivar(
    documentos_arquivados: List[FileUpload], id_pessoal: int
) -> Dict[str, str]:
    """
    Gera um dicionário com os tipos de documentos que ainda precisam ser
    arquivados.
    O valor será o nome formatado com sufixo numérico (ex: 'Receita_003').
    """
    tipos_docs = constants.TIPOS_DOCS
    tipos_docs_arquivar = filtrar_tipos_documentos_arquivar(
        documentos_arquivados, id_pessoal
    )

    maior_indice_por_tipo = maior_indice_documentos_arquivados_tipo(
        documentos_arquivados, id_pessoal
    )

    tipos_arquivar: Dict[str, str] = {}

    for tipo in tipos_docs_arquivar:
        proximo_indice = maior_indice_por_tipo.get(tipo, 0) + 1
        indice_formatada = f"{proximo_indice:03}"
        tipo_formatado = tipo.replace(" ", "_")

        if tipo in tipos_docs:
            tipos_arquivar[tipo] = tipo_formatado
        else:
            tipos_arquivar[tipo] = f"{tipo_formatado}_{indice_formatada}"

    return tipos_arquivar
