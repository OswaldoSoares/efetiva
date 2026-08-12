from django.template.loader import render_to_string


def html_card_colaboradores(request, contexto, data):
    data["html-card-colaboradores"] = render_to_string(
        "pagamentos/card_colaboradores.html", contexto, request=request
    )
    return data


def html_cartao_ponto(request, contexto, data):
    data["html_cartao_ponto"] = render_to_string(
        "pessoas/card_cartao_ponto_colaborador.html", contexto, request=request
    )
    return data


def html_funcionario(request, contexto, data):
    data["html_funcionario"] = render_to_string(
        "pagamentos/html_funcionario.html", contexto, request=request
    )
    return data


def html_contra_cheque(request, contexto, data):
    data["html_contra_cheque"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_minutas(request, contexto, data):
    data["html_minutas"] = render_to_string(
        "pagamentos/html_minutas.html", contexto, request=request
    )
    return data


def html_vales_pagamento(request, contexto, data):
    data["html_vales_pagamento"] = render_to_string(
        "pagamentos/html_vales.html", contexto, request=request
    )
    return data


def html_agenda(request, contexto, data):
    data["html_agenda"] = render_to_string(
        "pagamentos/html_agenda.html", contexto, request=request
    )
    return data


def html_files_contra_cheque(request, contexto, data):
    data["html_files_contra_cheque"] = render_to_string(
        "pessoas/html_files_contra_cheque.html", contexto, request=request
    )
    return data


def html_files_pagamento(request, contexto, data):
    data["html_files_pagamento"] = render_to_string(
        "pagamentos/html_files.html", contexto, request=request
    )
    return data


def html_vales(request, contexto, data):
    data["html_vales"] = render_to_string(
        "pessoas/card_vales_colaborador.html", contexto, request=request
    )
    return data


def html_itens_agenda_pagamento(request, contexto, data):
    data["html_itens_agenda_pagamento"] = render_to_string(
        "pagamentos/html_itens_agenda.html", contexto, request=request
    )
    return data


def html_itens_contra_cheque(request, contexto, data):
    data["html_itens_contra_cheque"] = render_to_string(
        "pagamentos/html_itens_contra_cheque.html", contexto, request=request
    )
    return data
