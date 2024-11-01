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


def html_card_docs_colaborador(request, contexto, data):
    data["html-card-docs-colaborador"] = render_to_string(
        "pessoas/card_docs_colaborador.html", contexto, request=request
    )
    return data


def html_card_fones_colaborador(request, contexto, data):
    data["html-card-fones-colaborador"] = render_to_string(
        "pessoas/card_fones_colaborador.html", contexto, request=request
    )
    return data


def html_card_contas_colaborador(request, contexto, data):
    data["html-card-contas-colaborador"] = render_to_string(
        "pessoas/card_contas_colaborador.html", contexto, request=request
    )
    return data


def html_card_vales_colaborador(request, contexto, data):
    data["html-card-vales-colaborador"] = render_to_string(
        "pessoas/card_vales_colaborador.html", contexto, request=request
    )
    return data


def html_card_decimo_terceiro_colaborador(request, contexto, data):
    data["html-card-decimo-terceiro-colaborador"] = render_to_string(
        "pessoas/card_decimo_terceiro_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_card_contra_cheque_colaborador(request, contexto, data):
    data["html-card-contra-cheque-colaborador"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_modal_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_doc_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_doc_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_fone_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_fone_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_confirma_excluir_fone_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_confirma_excluir_fone_colaborador.html",
        contexto,
        request=request,
    )
    return modal_html


def html_modal_conta_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_conta_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_confirma_excluir_conta_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_confirma_excluir_conta_colaborador.html",
        contexto,
        request=request,
    )
    return modal_html


def html_modal_vale_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_vale_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_confirma_excluir_vale_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_confirma_excluir_vale_colaborador.html",
        contexto,
        request=request,
    )
    return modal_html
