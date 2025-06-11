""" Responsável pelo resscisão do colaborador """
from datetime import datetime
from typing import Any, Optional
from django.http import JsonResponse
from pessoas import classes
from pessoas import html_data
from pessoas.facade import registrar_contra_cheque
from pessoas.models import CartaoPonto, Pessoal


def validar_modal_data_demissao_colaborador(
    request: Any,
) -> Optional[JsonResponse]:
    if request.method != "POST":
        return None

    id_pessoal = request.POST.get("id_pessoal")
    demissao_str = request.POST.get("demissao")

    demissao = datetime.strptime(demissao_str, "%Y-%m-%d").date()
    hoje = datetime.today().date()

    colaborador = classes.Colaborador(id_pessoal)
    # TODO Error pyright
    admissao = colaborador.dados_profissionais.data_admissao  # type: ignore

    if demissao > hoje:
        return JsonResponse(
            {
                "error": "A data de demissão não pode ser posterior ao dia "
                "de hoje."
            },
            status=400,
        )

    if demissao <= admissao:
        return JsonResponse(
            {
                "error": "A data de demissão deve ser posterior à data de "
                "admissão."
                if demissao == admissao
                else "A data de demissão não pode ser anterior à data de "
                "admissão."
            },
            status=400,
        )

    return None


def modal_data_demissao_colaborador(id_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    hoje = datetime.today().date()
    contexto = {
        "colaborador": colaborador,
        "hoje": hoje.strftime("%Y-%m-%d"),
    }
    modal_html = html_data.html_modal_data_demissao_colaborador(
        request, contexto
    )
    return JsonResponse({"modal_html": modal_html})
