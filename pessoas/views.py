from functools import partial
from django.shortcuts import render
from django.shortcuts import redirect
from django.http import JsonResponse
from rolepermissions.decorators import has_permission_decorator
from core.tools import upload_de_arquivo, excluir_arquivo
from core.tools import modal_excluir_arquivo, get_request_data
from core.tools import injetar_parametro_no_request_post
from .facades import rescisao
from pessoas import facade
from pessoas.print import (
    print_pdf_ficha_colaborador,
    print_pdf_rescisao_trabalho,
    print_contra_cheque,
)
from website.facade import str_hoje


@has_permission_decorator("modulo_colaboradores")
def indexpessoal(request):
    """Consultar Documentação Sistema Efetiva"""
    contexto = facade.create_contexto_categoria()
    contexto.update(facade.create_contexto_colaboradores("MENSALISTA", True))
    return render(request, "pessoas/index.html", contexto)


def selecionar_categoria(request):
    tipo = request.GET.get("tipo")
    status = bool(tipo)
    contexto = facade.create_contexto_colaboradores(tipo, status)
    return facade.selecionar_categoria_html_data(request, contexto)


def consultar_colaborador(request):
    id_pesssoal = request.GET.get("id_pessoal")
    contexto = facade.create_contexto_consulta_colaborador(id_pesssoal)
    return facade.colaborador_html_data(request, contexto)


def handle_modal_colaborador(
    request, modal_func, update_func, context_func, data_func
):
    id_pessoal = request.POST.get("id_pessoal") or request.GET.get(
        "id_pessoal"
    )

    if request.method == "GET":
        return modal_func(id_pessoal, request)
    if request.method == "POST":
        contexto = update_func(request)
        contexto.update(context_func())
        return data_func(request, contexto)

    return JsonResponse({"error": "Método não permitido"}, status=405)


def adicionar_ou_atualizar_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_colaborador,
        facade.save_colaborador,
        partial(facade.create_contexto_colaboradores, "MENSALISTA", True),
        facade.selecionar_categoria_html_data,
    )


def adicionar_ou_atualizar_doc_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_doc_colaborador,
        facade.save_doc_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.documento_html_data,
    )


def upload_arquivo_documento(request):
    print(request.POST)
    id_pessoal = request.POST.get("id_pessoal")
    tipo_documento = request.POST.get("tipo_documento")
    nome_arquivo = f"Documento_-_{tipo_documento}_-_{str(id_pessoal).zfill(4)}"
    print(nome_arquivo)
    mensagem = upload_de_arquivo(request, nome_arquivo, 5)

    contexto = facade.create_contexto_class_colaborador(request)
    contexto.update(mensagem)

    data = facade.arquivo_html_data(request, contexto)

    return data


def excluir_arquivo_documento(request):
    id_file_upload = get_request_data(request, "id_file_upload")
    if request.method == "POST":
        request_injetado = injetar_parametro_no_request_post(request)
        mensagem = excluir_arquivo(id_file_upload)

        contexto = facade.create_contexto_class_colaborador(request_injetado)
        contexto.update(mensagem)

        data = facade.arquivo_html_data(request, contexto)
    else:
        data = modal_excluir_arquivo(id_file_upload, request)

    return data


def adicionar_ou_atualizar_fone_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_fone_colaborador,
        facade.save_fone_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.telefone_html_data,
    )


def excluir_fone_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_confirma_excluir_fone_colaborador,
        facade.delete_fone_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.telefone_html_data,
    )


def adicionar_ou_atualizar_conta_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_conta_colaborador,
        facade.save_conta_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.conta_html_data,
    )


def excluir_conta_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_confirma_excluir_conta_colaborador,
        facade.delete_conta_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.conta_html_data,
    )


def adicionar_vale_colaborador(request):
    error = facade.validar_modal_vale_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        facade.modal_vale_colaborador,
        facade.save_vale_colaborador,
        partial(facade.create_contexto_vales_colaborador, request),
        facade.vale_html_data,
    )


def excluir_vale_colaborador(request):
    return handle_modal_colaborador(
        request,
        facade.modal_confirma_excluir_vale_colaborador,
        facade.delete_vale_colaborador,
        partial(facade.create_contexto_vales_colaborador, request),
        facade.vale_html_data,
    )


def selecionar_contra_cheque_decimo_terceiro(request):
    contexto = facade.create_contexto_contra_cheque_decimo_terceiro(request)
    return facade.contra_cheque_html_data(request, contexto)


def adicionar_vale_no_contra_cheque(request):
    contexto = facade.create_contra_cheque_itens_vale(request)
    contexto.update(facade.create_contexto_contra_cheque(request))
    contexto.update(facade.create_contexto_vales_colaborador(request))
    return facade.contra_cheque_html_data(request, contexto)


def excluir_vale_do_contra_cheque(request):
    contexto = facade.excluir_contra_cheque_item(request)
    contexto.update(facade.create_contexto_contra_cheque(request))
    contexto.update(facade.create_contexto_vales_colaborador(request))
    return facade.contra_cheque_html_data(request, contexto)


def adicionar_data_demissao_colaborador(request):
    error = rescisao.validar_modal_data_demissao_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        rescisao.modal_data_demissao_colaborador,
        rescisao.save_data_demissao_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.data_demissao_html_data,
    )


def mostrar_eventos_rescisorios_colaborador(request):
    contexto = facade.create_contexto_eventos_rescisorios_colaborador(request)
    return facade.data_eventos_html_data(request, contexto)


def calcular_verbas_rescisorias_colaborador(request):
    print(request.POST)
    contexto = facade.verbas_rescisorias(request)
    response = print_pdf_rescisao_trabalho(request, contexto)
    return response


def alterar_falta_colaborador(request):
    contexto = facade.alterar_cartao_ponto_falta(request)
    return facade.cartao_ponto_html_data(request, contexto)


def abonar_falta_colaborador(request):
    contexto = facade.alterar_cartao_ponto_abono_falta(request)
    return facade.cartao_ponto_html_data(request, contexto)


def alterar_conducao_colaborador(request):
    contexto = facade.alterar_cartao_ponto_conducao(request)
    return facade.cartao_ponto_html_data(request, contexto)


def alterar_entrada_colaborador(request):
    id_pessoal = request.POST.get("id_pessoal") or request.GET.get(
        "id_pessoal", 0
    )
    mes = int(request.POST.get("mes") or request.GET.get("mes", 0))
    ano = int(request.POST.get("ano") or request.GET.get("ano", 0))

    return handle_modal_colaborador(
        request,
        facade.modal_entrada_colaborador,
        facade.save_entrada_colaborador,
        partial(facade.create_contexto_cartao_ponto, id_pessoal, mes, ano),
        facade.cartao_ponto_html_data,
    )


def alterar_salario_colaborador(request):
    """Consultar Documentação Sistema Efetiva"""
    error = facade.validar_modal_salario_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        facade.modal_salario_colaborador,
        facade.save_salario_colaborador,
        partial(facade.create_contexto_salario, request),
        facade.salario_html_data,
    )


def alterar_vale_transporte_colaborador(request):
    error = facade.validar_modal_vale_transporte_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        facade.modal_vale_transporte_colaborador,
        facade.save_vale_transporte_colaborador,
        partial(facade.create_contexto_vale_transporte, request),
        facade.vale_transporte_html_data,
    )


def pagar_contra_cheque(request):
    """Consultar Documentação Sistema Efetiva"""
    return handle_modal_colaborador(
        request,
        facade.modal_pagar_contra_cheque,
        facade.save_pagamento_contra_cheque,
        partial(facade.create_contexto_contra_cheque, request),
        facade.contra_cheque_html_data,
    )


def estornar_pagamento_contra_cheque(request):
    """Consultar Documentação Sistema Efetiva"""
    return handle_modal_colaborador(
        request,
        facade.modal_estornar_pagamento_contra_cheque,
        facade.save_estorno_pagamento_contra_cheque,
        partial(facade.create_contexto_contra_cheque, request),
        facade.contra_cheque_html_data,
    )


def bloqueia_pessoa(request, idpessoa):
    facade.altera_status(idpessoa)
    return redirect("indexpessoal")


def edita_salario(request):
    c_pessoal = request.POST.get("idPessoal")
    c_salario = request.POST.get("Salario")
    c_horas_mensais = float(request.POST.get("HorasMensais"))
    c_valetransporte = request.POST.get("ValeTransporte")
    facade.save_salario(
        c_pessoal, c_salario, c_horas_mensais, c_valetransporte
    )
    return redirect("consultapessoa", c_pessoal)


def edita_demissao(request):
    c_pessoal = request.POST.get("idPessoal")
    c_data_demissao = request.POST.get("DataDemissao")
    facade.edita_data_demissao(c_pessoal, c_data_demissao)
    return redirect("consultapessoa", c_pessoal)


def cria_contracheque(request):
    c_mesreferencia = request.POST.get("MesReferencia")
    c_anoreferencia = request.POST.get("AnoReferencia")
    c_valor = 0.00
    c_pessoal = request.POST.get("idPessoal")
    facade.create_contracheque(
        c_mesreferencia, c_anoreferencia, c_valor, c_pessoal
    )
    return redirect("consultapessoa", c_pessoal)


def seleciona_contracheque(request):
    c_idpessoal = request.GET.get("idpessoal")
    c_mes = request.GET.get("mes")
    c_ano = request.GET.get("ano")
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpessoal)
    return data


def cria_contrachequeitens(request):
    c_idcontracheque = request.POST.get("idContraCheque")
    c_descricao = request.POST.get("Descricao")
    c_valor = request.POST.get("Valor")
    c_registro = request.POST.get("Registro")
    c_mes = request.POST.get("MesReferencia")
    c_ano = request.POST.get("AnoReferencia")
    c_idpessoal = request.POST.get("idPessoal")
    facade.create_contracheque_itens(
        c_descricao, c_valor, c_registro, c_idcontracheque
    )
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpessoal)
    return data


def salva_foto(request):
    idpes = request.POST.get("idpessoal")
    arquivo = request.FILES.get("arquivo")
    facade.salva_foto_colaborador(idpes, arquivo)
    contexto = facade.create_contexto_consulta_colaborador(idpes)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def atualiza_decimo_terceiro(request):
    facade.gera_decimo_terceiro()
    colaboradores = facade.create_contexto_colaboradores_ativo(True)
    contexto = {"colaboradores": colaboradores}
    data = facade.create_data_lista_colaboradores_ativo(request, contexto)
    return data


def print_decimo_terceiro(request):
    idpes = request.GET.get("idpes")
    idparcela = request.GET.get("idparcela")
    contexto = facade.create_contexto_print_decimo_terceiro(idpes, idparcela)
    response = print_pdf_decimno_terceiro(contexto)
    return response


def altera_salario_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    salario_form = facade.read_salario_database(idpessoal)
    contexto = {"salario_form": salario_form, "idpessoal": idpessoal}
    data = facade.create_data_form_salario_colaborador(request, contexto)
    return data


def salva_salario_colaborador(request):
    error, msg = facade.valida_salario_colaborador(request)
    salario_form = facade.read_salario_post(request)
    idsalario = request.POST.get("idsalario")
    idpessoal = request.POST.get("idpessoal")
    if not error:
        facade.altera_salario(salario_form, idsalario)
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        salario_form = dict()
    else:
        contexto = {"salario_form": salario_form, "idpessoal": idpessoal}
        contexto.update(msg)
        data = facade.create_data_form_salario_colaborador(request, contexto)
    return data


def form_paga_decimo_terceiro(request):
    idparcela = request.GET.get("idparcela")
    idpessoal = request.GET.get("idpessoal")
    hoje = str_hoje()
    contexto = {"idparcela": idparcela, "idpessoal": idpessoal, "hoje": hoje}
    data = facade.create_data_form_paga_decimo_terceiro(request, contexto)
    return data


def paga_decimo_terceiro(request):
    idparcela = int(request.POST.get("idparcela"))
    data_pgto = request.POST.get("data_pgto")
    idpessoal = request.POST.get("idpessoal")
    if request.method == "POST":
        facade.paga_parcela(idparcela, data_pgto)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def print_ficha_colaborador(request):
    idpes = request.GET.get("idpes")
    contexto = facade.create_contexto_consulta_colaborador(idpes)
    response = print_pdf_ficha_colaborador(contexto)
    return response


def demissao_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    hoje = str_hoje()
    contexto = {
        "idpessoal": idpessoal,
        "hoje": hoje,
    }
    data = facade.create_data_form_altera_demissao(request, contexto)
    return data


def salva_demissao_colaborador(request):
    print("demitido")
    error, msg = facade.valida_demissao_colaborador(request)
    demissao_form = facade.read_demissao_post(request)
    data_demissao = request.POST.get("demissao")
    if not error:
        idpessoal = request.POST.get("idpessoal")
        facade.salva_demissao(idpessoal, data_demissao)
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        demissao_form = dict()
    else:
        idpessoal = request.POST.get("idpessoal")
        contexto = {
            "demissao_form": demissao_form,
            "idpessoal": idpessoal,
            "error": error,
        }
        contexto.update(msg)
        data = facade.create_data_form_altera_demissao(request, contexto)
    return data


def periodo_ferias(request):
    idpessoal = request.GET.get("idpessoal")
    idaquisitivo = request.GET.get("idaquisitivo")
    hoje = str_hoje()
    contexto = {
        "idpessoal": idpessoal,
        "idaquisitivo": idaquisitivo,
        "hoje": hoje,
    }
    data = facade.create_data_form_periodo_ferias(request, contexto)
    return data


def salva_periodo_ferias(request):
    error, msg = facade.valida_periodo_ferias(request)
    ferias_form = facade.read_periodo_ferias_post(request)
    if not error:
        data = dict()
        idpessoal = request.POST.get("idpessoal")
        inicio = request.POST.get("inicio")
        terminio = request.POST.get("termino")
        idaquisitivo = request.POST.get("idaquisitivo")
        facade.salva_periodo_ferias_colaborador(
            idpessoal, inicio, terminio, idaquisitivo
        )
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        ferias_form = dict()
    else:
        idpessoal = request.POST.get("idpessoal")
        contexto = {
            "ferias_form": ferias_form,
            "idpessoal": idpessoal,
            "error": error,
        }
        contexto.update(msg)
        data = facade.create_data_form_periodo_ferias(request, contexto)
    return data


def confirma_exclusao_periodo_ferias(request):
    idferias = request.GET.get("idferias")
    contexto = facade.create_contexto_exclui_ferias(idferias)
    data = facade.create_data_form_exclui_periodo_ferias(request, contexto)
    return data


def exclui_periodo_ferias(request):
    idpessoal = request.POST.get("idpessoal")
    idferias = request.POST.get("idobj")
    facade.exclui_periodo_ferias_base_dados(idferias)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def print_ferias(request):
    idpes = request.GET.get("idpes")
    idaquisitivo = request.GET.get("idaquisitivo")
    idparcela = request.GET.get("idparcela")
    contexto = facade.create_contexto_print_ferias(
        idpes, idaquisitivo, idparcela
    )
    response = print_pdf_ferias(contexto)
    return response


def altera_status_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    ativo = bool(request.GET.get("lista"))
    facade.altera_status(idpessoal)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    if ativo:
        colaboradores = facade.create_contexto_colaboradores_ativo(True)
    else:
        colaboradores = facade.create_contexto_colaboradores_ativo(False)
    colaboradores = {"colaboradores": colaboradores}
    contexto.update(colaboradores)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def altera_lista(request):
    ativo = bool(request.GET.get("lista"))
    if ativo:
        colaboradores = facade.create_contexto_colaboradores_ativo(True)
    else:
        colaboradores = facade.create_contexto_colaboradores_ativo(False)
    contexto = {"colaboradores": colaboradores}
    data = facade.create_data_lista_colaboradores_ativo(request, contexto)
    return data


def verba_rescisoria(request):
    idpessoal = request.GET.get("idpessoal")
    contexto = facade.create_contexto_verbas_rescisoria(idpessoal)
    data = facade.create_data_verbas_rescisoria(request, contexto)
    return data


def print_rescisao_trabalho(request):
    idpessoal = request.GET.get("idpessoal")
    causa = request.GET.get("causa")
    contexto = facade.create_contexto_verbas_rescisoria(idpessoal)
    contexto.update({"causa": causa})
    response = print_pdf_rescisao_trabalho(request, contexto)
    return response


def seleciona_aquisitivo(request):
    idpessoal = request.GET.get("idpessoal")
    idaquisitivo = request.GET.get("idaquisitivo")
    descricao = request.GET.get("descricao")
    contexto = facade.create_contexto_contra_cheque_apaga(
        idpessoal,
        idaquisitivo,
        descricao,
    )
    contexto.update({"idpessoal": idpessoal})
    data = facade.create_data_contra_cheque(request, contexto)
    return data


def seleciona_parcela(request):
    idpessoal = request.GET.get("idpessoal")
    idparcela = request.GET.get("idparcela")
    descricao = request.GET.get("descricao")
    contexto = facade.create_contexto_contra_cheque(
        idpessoal,
        idparcela,
        descricao,
    )
    contexto.update({"idpessoal": idpessoal})
    data = facade.create_data_contra_cheque(request, contexto)
    return data


def exclui_contra_cheque_item(request):
    idcontrachequeitens = request.GET.get("idcontrachequeitens")
    idcontracheque = request.GET.get("idcontracheque")
    idpessoal = request.GET.get("idpessoal")
    colaborador = facade.get_colaborador(idpessoal)
    facade.delete_contra_cheque_itens(idcontrachequeitens)
    contexto = facade.contexto_contra_cheque_id(idcontracheque)
    contexto.update(facade.contexto_vales_colaborador(colaborador))
    contexto.update({"idpessoal": idpessoal})
    data = facade.data_adiciona_vale_contra_cheque(request, contexto)
    return data


def imprime_contra_cheque(request):
    idcontracheque = request.GET.get("idcontracheque")
    idpessoal = request.GET.get("idpessoal")
    tipo = request.GET.get("tipo")
    contexto = facade.contexto_contra_cheque_id(idcontracheque)
    colaborador = facade.get_colaborador(idpessoal)
    contexto.update({"colaborador": colaborador})
    salario_base = facade.get_salario_base_contra_cheque_itens(
        contexto["contra_cheque_itens"], tipo
    )
    contexto.update({"salario_base": salario_base})
    contexto_minutas = facade.create_contexto_minutas_contra_cheque(
        idpessoal, contexto["contra_cheque"]
    )
    contexto.update(contexto_minutas)
    contexto_cartao_ponto = facade.create_contexto_cartao_ponto_contra_cheque(
        idpessoal, contexto["contra_cheque"]
    )
    contexto.update(contexto_cartao_ponto)
    response = print_contra_cheque(contexto)
    return response


def imprimir_contra_cheque(request):
    id_pessoal = request.GET.get("id_pessoal")
    contexto = facade.create_contexto_contra_cheque(request)
    contexto.update(facade.create_contexto_class_colaborador(request))
    contexto.update(
        facade.create_contexto_minutas_contra_cheque(
            id_pessoal, contexto["contra_cheque"]
        )
    )
    contexto.update(
        facade.create_contexto_cartao_ponto_contra_cheque(
            id_pessoal, contexto["contra_cheque"]
        )
    )
    response = print_contra_cheque(contexto)
    return response


def adiciona_vale_colaborador(request):
    if request.method == "POST":
        idpessoal = int(request.POST.get("idpessoal"))
    else:
        idpessoal = int(request.GET.get("idpessoal"))
    data = facade.modal_vale_colaborador(request, idpessoal)
    return data


def exclui_vale_colaborador(request):
    if request.method == "POST":
        idvale = request.POST.get("idvale")
        idpessoal = request.POST.get("idpessoal")
        data = facade.exclui_vale_colaborador_id(request, idvale, idpessoal)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data


def upload_contra_cheque(request):
    """Consultar Documentação Sistema Efetiva"""
    id_contra_cheque = request.POST.get("id_contra_cheque")
    nome_arquivo = f"Contra-Cheque_-_{str(id_contra_cheque).zfill(6)}"
    mensagem = upload_de_arquivo(request, nome_arquivo, 5)

    contexto = facade.create_contexto_contra_cheque(request)
    contexto.update(mensagem)

    data = facade.contra_cheque_html_data(request, contexto)

    return data


def excluir_arquivo_contra_cheque(request):
    """Consultar Documentação Sistema Efetiva"""
    id_file_upload = get_request_data(request, "id_file_upload")
    if request.method == "POST":
        request_injetado = injetar_parametro_no_request_post(request)
        mensagem = excluir_arquivo(id_file_upload)

        contexto = facade.create_contexto_contra_cheque(request_injetado)
        contexto.update(mensagem)

        data = facade.contra_cheque_html_data(request, contexto)
    else:
        data = modal_excluir_arquivo(id_file_upload, request)

    return data


def readmitir_colaborador(request):
    """Consultar Documentação Sistema Efetiva"""
    error = facade.validar_modal_data_readmissao_colaborador(request)
    if error:
        return error

    return handle_modal_colaborador(
        request,
        facade.modal_data_readmissao_colaborador,
        facade.save_readmissao_colaborador,
        partial(facade.create_contexto_class_colaborador, request),
        facade.data_demissao_html_data,
    )
