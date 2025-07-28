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


def html_card_salario_colaborador(request, contexto, data):
    data["html-card-salario-colaborador"] = render_to_string(
        "pessoas/card_salario_colaborador.html", contexto, request=request
    )
    return data


def html_card_vale_transporte_colaborador(request, contexto, data):
    data["html-card-vale-transporte-colaborador"] = render_to_string(
        "pessoas/card_vale_transporte_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_card_vales_colaborador(request, contexto, data):
    data["html-card-vales-colaborador"] = render_to_string(
        "pessoas/card_vales_colaborador.html", contexto, request=request
    )
    return data


def html_card_arquivos_colaborador(request, contexto, data):
    data["html-card-arquivos-colaborador"] = render_to_string(
        "pessoas/card_arquivos_colaborador.html", contexto, request=request
    )
    return data


def html_card_cartao_ponto_colaborador(request, contexto, data):
    data["html-card-cartao-ponto-colaborador"] = render_to_string(
        "pessoas/card_cartao_ponto_colaborador.html", contexto, request=request
    )
    return data


def html_card_eventos_rescisorios_colaborador(request, contexto, data):
    data["html-card-eventos-rescisorios-colaborador"] = render_to_string(
        "pessoas/card_eventos_rescisorios_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_card_rescisao_colaborador(request, contexto, data):
    data["html-card-rescisao-colaborador"] = render_to_string(
        "pessoas/card_rescisao_colaborador.html",
        contexto,
        request=request,
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


def html_modal_registro_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_registra_colaborador.html", contexto, request=request
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


def html_modal_salario_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_salario_colaborador.html",
        contexto,
        request=request,
    )
    return modal_html


def html_modal_vale_transporte_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_vale_transporte_colaborador.html",
        contexto,
        request=request,
    )
    return modal_html


def html_modal_pagar_contra_cheque(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_pagamento_contra_cheque.html",
        contexto,
        request=request,
    )
    return modal_html


def html_modal_estornar_pagamento_contra_cheque(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_estornar_pagamento_contra_cheque.html",
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


def html_modal_data_demissao_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_demissao_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_data_readmissao_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_readmissao_colaborador.html", contexto, request=request
    )
    return modal_html


def html_modal_entrada_colaborador(request, contexto):
    modal_html = render_to_string(
        "pessoas/modal_entrada_colaborador.html", contexto, request=request
    )
    return modal_html
