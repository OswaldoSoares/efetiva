from django.template.loader import render_to_string


def html_modal_abastecimento(request, contexto):
    return render_to_string(
        "despesas/modal_abastecimento.html", contexto, request=request
    )


def html_card_abastecimento(request, contexto, data):
    data["html-card-abastecimento"] = render_to_string(
        "despesas/components/abastecimento.html", contexto, request=request
    )
    return data
