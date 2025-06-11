""" Responsável pelo resscisão do colaborador """
from datetime import datetime
from django.http import JsonResponse
from pessoas import classes
from pessoas import html_data


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
