from django.template.loader import render_to_string


def html_card_veiculos(request, contexto, data):
    data["html-card-veiculos"] = render_to_string(
        "veiculos/card_veiculos.html", contexto, request=request
    )
    return data


def html_card_veiculo(request, contexto, data):
    data["html-card-veiculo"] = render_to_string(
        "veiculos/card_veiculo.html", contexto, request=request
    )
    return data


def html_card_categorias(request, contexto, data):
    data["html-card-categorias-veiculo"] = render_to_string(
        "veiculos/card_categorias.html", contexto, request=request
    )
    return data


def html_modal_veiculo(request, contexto):
    return render_to_string(
        "veiculos/modal_veiculo.html", contexto, request=request
    )


def html_modal_categoria(request, contexto):
    return render_to_string(
        "veiculos/modal_categoria.html", contexto, request=request
    )
