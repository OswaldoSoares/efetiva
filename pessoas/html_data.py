from django.template.loader import render_to_string


def html_card_listia_colaboradores(request, data, contexto):
    data["html-card-colaboradores"] = render_to_string(
        "pessoas/card_colaboradores.html",
        contexto,
        request=request,
    )
    return data
