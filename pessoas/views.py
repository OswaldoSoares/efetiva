from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from pessoas import facade
from pessoas.print import (
    print_pdf_ficha_colaborador,
    print_pdf_rescisao_trabalho,
    print_contra_cheque,
)
from website.facade import (
    dict_tipo_conta,
    dict_tipo_doc,
    dict_tipo_fone,
    str_hoje,
)
from .models import (
    Pessoal,
    DocPessoal,
    FonePessoal,
    ContaPessoal,
    ContraChequeItens,
)
from .forms import (
    CadastraPessoal,
    CadastraDocPessoal,
    CadastraFonePessoal,
    CadastraContaPessoal,
)


def removeduplicadas(lista):
    novalista = list()
    for i in range(len(lista)):
        if lista[i] not in lista[i + 1 :]:
            novalista.append(lista[i])
    return novalista


@has_permission_decorator("modulo_colaboradores")
def indexpessoal(request):
    contexto = facade.create_contexto_categoria()
    contexto.update(facade.create_contexto_colaboradores("MENSALISTA", True))
    return render(request, "pessoas/index.html", contexto)


def selecionar_categoria(request):
    tipo = request.GET.get("tipo")
    status = True if tipo else False
    contexto = facade.create_contexto_colaboradores(tipo, status)
    return facade.selecionar_categoria_html_data(request, contexto)


def consultar_colaborador(request):
    id_pesssoal = request.GET.get("id_pessoal")
    contexto = facade.create_contexto_consulta_colaborador(id_pesssoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def handle_modal_colaborador(request, modal_func, update_func):
    id_pessoal = request.POST.get("id_pessoal") or request.GET.get(
        "id_pessoal"
    )

    if request.method == "GET":
        return modal_func(id_pessoal, request)
    if request.method == "POST":
        contexto = update_func(request)
        print(f"[INFO] : {contexto}")
        contexto.update(
            facade.create_contexto_colaboradores("MENSALISTA", True)
        )
        return facade.selecionar_categoria_html_data(request, contexto)

    return JsonResponse({"error": "Método não permitido"}, status=405)


def adicionar_ou_atualizar_colaborador(request):
    return handle_modal_colaborador(
        request, facade.modal_colaborador, facade.save_colaborador
    )


def criadocpessoa(request):
    if request.method == "POST":
        idpessoal = request.POST.get("idPessoal")
        form = CadastraDocPessoal(request.POST or None)
    else:
        idpessoal = request.GET.get("idpessoal")
        form = CadastraDocPessoal(initial={"idPessoal": idpessoal})
    return salva_form(request, form, "pessoas/criadocpessoa.html", idpessoal)


def excluidocpessoa(request, idpesdoc):
    docpessoa = get_object_or_404(DocPessoal, idDocPessoal=idpesdoc)
    data = dict()
    if request.method == "POST":
        docpessoa.delete()
        return redirect("consultapessoa", docpessoa.idPessoal_id)
    else:
        context = {"docpessoa": docpessoa}
        data["html_form"] = render_to_string(
            "pessoas/excluidocpessoa.html", context, request=request
        )
    return JsonResponse(data)


def criafonepessoa(request):
    if request.method == "POST":
        idpessoal = request.POST.get("idPessoal")
        form = CadastraFonePessoal(request.POST or None)
    else:
        idpessoal = request.GET.get("idpessoal")
        form = CadastraFonePessoal(initial={"idPessoal": idpessoal})
    return salva_form(request, form, "pessoas/criafonepessoa.html", idpessoal)


def excluifonepessoa(request, idpesfon):
    fonepessoa = get_object_or_404(FonePessoal, idFonePessoal=idpesfon)
    data = dict()
    if request.method == "POST":
        fonepessoa.delete()
        return redirect("consultapessoa", fonepessoa.idPessoal_id)
    else:
        context = {"fonepessoa": fonepessoa}
        data["html_form"] = render_to_string(
            "pessoas/excluifonepessoa.html", context, request=request
        )
    return JsonResponse(data)


def criacontapessoa(request):
    if request.method == "POST":
        idpessoal = request.POST.get("idPessoal")
        form = CadastraContaPessoal(request.POST or None)
    else:
        idpessoal = request.GET.get("idpessoal")
        form = CadastraContaPessoal(initial={"idPessoal": idpessoal})
    return salva_form(request, form, "pessoas/criacontapessoa.html", idpessoal)


def excluicontapessoa(request, idpescon):
    contapessoa = get_object_or_404(ContaPessoal, idContaPessoal=idpescon)
    data = dict()
    if request.method == "POST":
        contapessoa.delete()
        return redirect("consultapessoa", contapessoa.idPessoal_id)
    else:
        context = {"contapessoa": contapessoa}
        data["html_form"] = render_to_string(
            "pessoas/excluicontapessoa.html", context, request=request
        )
    return JsonResponse(data)


def salva_form(request, form, template_name, idpes):
    data = dict()
    if request.method == "POST":
        if form.is_valid():
            form.save()
            data["form_is_valid"] = True
            if template_name == "pessoas/criapessoa.html":
                return redirect("indexpessoal")
            else:
                return redirect("consultapessoa", idpes)
        else:
            data["form_is_valid"] = False
    context = {"form": form}
    data["html_form"] = render_to_string(
        template_name, context, request=request
    )
    return JsonResponse(data)


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


def cria_vale(request):
    c_data = request.POST.get("Data")
    c_descricao = request.POST.get("Descricao")
    c_valor = request.POST.get("Valor")
    c_pessoal = request.POST.get("idPessoal")
    facade.create_vale(c_data, c_descricao, c_valor, c_pessoal)
    return render(request, "pessoas/consultapessoa.html")


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


def adiciona_documento_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    hoje = str_hoje()
    tipo_doc = dict_tipo_doc()
    contexto = {"idpessoal": idpessoal, "hoje": hoje, "tipo_doc": tipo_doc}
    data = facade.create_data_form_adiciona_documento_colaborador(
        request, contexto
    )
    return data


def altera_documento_colaborador(request):
    iddocpessoal = request.GET.get("iddocpessoal")
    idpessoal = request.GET.get("idpessoal")
    documento_form = facade.read_documento_database(iddocpessoal)
    tipo_doc = dict_tipo_doc()
    contexto = {
        "documento_form": documento_form,
        "idpessoal": idpessoal,
        "tipo_doc": tipo_doc,
    }
    data = facade.create_data_form_adiciona_documento_colaborador(
        request, contexto
    )
    return data


def salva_documento_colaborador(request):
    error, msg = facade.valida_documento_colaborador(request)
    documento_form = facade.read_documento_post(request)
    iddocpessoal = request.POST.get("iddocpessoal")
    if not error:
        if iddocpessoal:
            facade.altera_documento(documento_form, iddocpessoal)
        else:
            facade.salva_documento(documento_form)
        idpessoal = request.POST.get("idpessoal")
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        documento_form = dict()
    else:
        idpessoal = request.POST.get("idpessoal")
        hoje = str_hoje()
        tipo_doc = dict_tipo_doc()
        contexto = {
            "documento_form": documento_form,
            "idpessoal": idpessoal,
            "hoje": hoje,
            "tipo_doc": tipo_doc,
            "error": error,
        }
        contexto.update(msg)
        data = facade.create_data_form_adiciona_documento_colaborador(
            request, contexto
        )
    return data


def exclui_documento_colaborador(request):
    iddocpessoal = request.GET.get("iddocpessoal")
    contexto = facade.create_contexto_exclui_documento_colaborador(
        iddocpessoal
    )
    data = facade.create_data_form_exclui_documento_colaborador(
        request, contexto
    )
    return data


def apaga_documento_colaborador(request):
    iddocpessoal = request.POST.get("idobj")
    idpessoal = request.POST.get("idpessoal")
    facade.apaga_documento(iddocpessoal)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def adiciona_telefone_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    tipo_fone = dict_tipo_fone()
    contexto = {"idpessoal": idpessoal, "tipo_fone": tipo_fone}
    data = facade.create_data_form_adiciona_fone_colaborador(request, contexto)
    return data


def altera_telefone_colaborador(request):
    idfonepessoal = request.GET.get("idfonepessoal")
    idpessoal = request.GET.get("idpessoal")
    fone_form = facade.read_fone_database(idfonepessoal)
    tipo_fone = dict_tipo_fone()
    contexto = {
        "fone_form": fone_form,
        "idpessoal": idpessoal,
        "tipo_fone": tipo_fone,
    }
    data = facade.create_data_form_adiciona_fone_colaborador(request, contexto)
    return data


def salva_telefone_colaborador(request):
    error, msg = facade.valida_fone_colaborador(request)
    fone_form = facade.read_fone_post(request)
    idfonepessoal = request.POST.get("idfonepessoal")
    if not error:
        if idfonepessoal:
            facade.altera_fone(fone_form, idfonepessoal)
        else:
            facade.salva_fone(fone_form)
        idpessoal = request.POST.get("idpessoal")
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        fone_form = dict()
    else:
        idpessoal = request.POST.get("idpessoal")
        tipo_fone = dict_tipo_fone()
        contexto = {
            "fone_form": fone_form,
            "idpessoal": idpessoal,
            "tipo_fone": tipo_fone,
            "error": error,
        }
        contexto.update(msg)
        data = facade.create_data_form_adiciona_fone_colaborador(
            request, contexto
        )
    return data


def exclui_telefone_colaborador(request):
    idfonepessoal = request.GET.get("idfonepessoal")
    contexto = facade.create_contexto_exclui_fone_colaborador(idfonepessoal)
    data = facade.create_data_form_exclui_fone_colaborador(request, contexto)
    return data


def apaga_telefone_colaborador(request):
    idfonepessoal = request.POST.get("idobj")
    idpessoal = request.POST.get("idpessoal")
    facade.apaga_fone(idfonepessoal)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


def adiciona_conta_colaborador(request):
    idpessoal = request.GET.get("idpessoal")
    tipo_conta = dict_tipo_conta()
    contexto = {"idpessoal": idpessoal, "tipo_conta": tipo_conta}
    data = facade.create_data_form_adiciona_conta_colaborador(
        request, contexto
    )
    return data


def altera_conta_colaborador(request):
    if request.method == "POST":
        idpessoal = int(request.POST.get("idpessoal"))
    else:
        idpessoal = int(request.GET.get("idpessoal"))
    data = facade.modal_conta_bancaria(request, idpessoal)
    return data


def salva_conta_colaborador(request):
    error, msg = facade.valida_conta_colaborador(request)
    conta_form = facade.read_conta_post(request)
    idcontapessoal = request.POST.get("idcontapessoal")
    if not error:
        if idcontapessoal:
            facade.altera_conta(conta_form, idcontapessoal)
        else:
            facade.salva_conta(conta_form)
        idpessoal = request.POST.get("idpessoal")
        contexto = facade.create_contexto_consulta_colaborador(idpessoal)
        data = facade.create_data_consulta_colaborador(request, contexto)
        conta_form = dict()
    else:
        idpessoal = request.POST.get("idpessoal")
        tipo_conta = dict_tipo_conta()
        contexto = {
            "conta_form": conta_form,
            "idpessoal": idpessoal,
            "tipo_conta": tipo_conta,
            "error": error,
        }
        contexto.update(msg)
        data = facade.create_data_form_adiciona_conta_colaborador(
            request, contexto
        )
    return data


def exclui_conta_colaborador(request):
    idcontapessoal = request.GET.get("idcontapessoal")
    contexto = facade.create_contexto_exclui_conta_colaborador(idcontapessoal)
    data = facade.create_data_form_exclui_conta_colaborador(request, contexto)
    return data


def apaga_conta_colaborador(request):
    idcontapessoal = request.POST.get("idobj")
    idpessoal = request.POST.get("idpessoal")
    facade.apaga_conta(idcontapessoal)
    contexto = facade.create_contexto_consulta_colaborador(idpessoal)
    data = facade.create_data_consulta_colaborador(request, contexto)
    return data


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
    contexto = facade.create_contexto_contra_cheque(
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


def adiciona_vale_contra_cheque(request):
    idvale = request.GET.get("idvale")
    idcontracheque = request.GET.get("idcontracheque")
    idpessoal = request.GET.get("idpessoal")
    colaborador = facade.get_colaborador(idpessoal)
    facade.create_contra_cheque_itens_vale(idcontracheque, idvale)
    contexto = facade.contexto_contra_cheque_id(idcontracheque)
    contexto.update(facade.contexto_vales_colaborador(colaborador))
    contexto.update({"idpessoal": idpessoal})
    data = facade.data_adiciona_vale_contra_cheque(request, contexto)
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


def pagamento_contra_cheque(request):
    if request.method == "POST":
        idcontracheque = request.POST.get("idcontracheque")
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        print(f"[INFO] {idcontracheque} - {idpessoal} - {mes_ano}")
        facade.paga_contra_cheque(request, idcontracheque)
        descricao = facade.get_descricao_contra_cheque_id(idcontracheque)
        contexto = facade.create_contexto_contra_cheque_colaborador(
            idpessoal, mes_ano, descricao
        )
        data = facade.create_data_contra_cheque_colaborador(request, contexto)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data


def estorna_contra_cheque(request):
    if request.method == "POST":
        idcontracheque = request.POST.get("idcontracheque")
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        facade.estorna_contra_cheque(request, idcontracheque)
        descricao = facade.get_descricao_contra_cheque_id(idcontracheque)
        contexto = facade.create_contexto_contra_cheque_colaborador(
            idpessoal, mes_ano, descricao
        )
        data = facade.create_data_contra_cheque_colaborador(request, contexto)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data


def arquiva_contra_cheque(request):
    idcontracheque = request.POST.get("idcontracheque")
    idpessoal = request.POST.get("idpessoal")
    mes_ano = request.POST.get("mes_ano")
    message = facade.salva_arquivo_contra_cheque(request, idcontracheque)
    descricao = facade.get_descricao_contra_cheque_id(idcontracheque)
    contexto = facade.create_contexto_contra_cheque_colaborador(
        idpessoal, mes_ano, descricao
    )
    contexto.update({"message": message})
    data = facade.create_data_contra_cheque_colaborador(request, contexto)
    return data


def exclui_arquivo_contra_cheque(request):
    if request.method == "POST":
        print(request.POST)
        idcontracheque = request.POST.get("idcontracheque")
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        facade.exclui_arquivo_contra_cheque_servidor(request, idcontracheque)
        descricao = facade.get_descricao_contra_cheque_id(idcontracheque)
        contexto = facade.create_contexto_contra_cheque_colaborador(
            idpessoal, mes_ano, descricao
        )
        data = facade.create_data_contra_cheque_colaborador(request, contexto)
    else:
        print(request.GET)
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data
