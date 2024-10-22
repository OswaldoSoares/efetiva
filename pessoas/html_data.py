from django.template.loader import render_to_string


def html_card_lista_colaboradores(request, contexto, data):
    data["html-card-colaboradores"] = render_to_string(
        "pessoas/card_colaboradores.html", contexto, request=request
    )
    return data


def html_card_foto_colaborador(request, contexto, data):
    data["html-card-foto-colaborador"] = render_to_string(
        "pessoas/card_foto_colaborador.html", contexto, request=request
    )
    return data


def html_modal_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_colaborador.html", contexto, request=request
    )
    return modal_html
