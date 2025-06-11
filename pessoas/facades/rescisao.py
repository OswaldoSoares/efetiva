""" Responsável pelo resscisão do colaborador """
from datetime import datetime, timedelta
from typing import Any, Optional
from django.http import JsonResponse
from core.tools import primeiro_e_ultimo_dia_do_mes
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


def atualizar_cartao_ponto_rescisao(id_pessoal, demissao):
    _, ultimo_dia_mes = primeiro_e_ultimo_dia_do_mes(
        demissao.month, demissao.year
    )

    dia_seguinte_demissao = demissao + timedelta(days=1)

    cartao_ponto = CartaoPonto.objects.filter(
        idPessoal=id_pessoal,
        Dia__range=[dia_seguinte_demissao, ultimo_dia_mes],
    )

    if cartao_ponto.exists():
        cartao_ponto.update(
            Ausencia="-------",
            Conducao=0,
            Remunerado=0,
            CarroEmpresa=0,
        )


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
