from django.template.loader import render_to_string


def html_card_colaboradores(request, contexto, data):
    data["html-card-colaboradores"] = render_to_string(
        "pagamentos/card_colaboradores.html", contexto, request=request
    )
    return data
