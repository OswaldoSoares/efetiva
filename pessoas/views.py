from django.shortcuts import render
from django.shortcuts import redirect, get_object_or_404
from django.http import JsonResponse
from django.template.loader import render_to_string
from rolepermissions.decorators import has_permission_decorator
from pessoas import facade
from pessoas.print import print_pdf_decimno_terceiro
from website.facade import dict_tipo_conta, dict_tipo_doc, dict_tipo_fone, str_hoje
from .models import Pessoal, DocPessoal, FonePessoal, ContaPessoal, ContraChequeItens
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
    colaboradores = facade.create_contexto_colaboradores_ativo()
    contexto = {"colaboradores": colaboradores}
    # categoriaslist = Pessoal.objects.values("Categoria").order_by("Categoria")
    # categorias = removeduplicadas(categoriaslist)
    return render(request, "pessoas/index.html", contexto)


def cria_pessoa(request):
    c_form = CadastraPessoal
    c_idobj = None
    c_url = "/pessoas/criapessoa/"
    c_view = "cria_pessoa"
    idpessoal = None
    data = facade.form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal)
    return data


def edita_pessoa(request, idpessoa):
    c_form = CadastraPessoal
    c_idobj = idpessoa
    c_url = "/pessoas/editapessoa/{}/".format(c_idobj)
    c_view = "edita_pessoa"
    idpessoal = "edita_pessoa"
    data = facade.form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal)
    return data


def excluipessoa(request, idpessoa):
    c_idobj = idpessoa
    c_url = "/pessoas/excluipessoa/{}/".format(c_idobj)
    c_view = "exclui_pessoa"
    idpessoal = idpessoa
    data = facade.form_exclui_pessoal(request, c_idobj, c_url, c_view, idpessoal)
    return data


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


def consulta_pessoa(request, idpessoa):
    contexto = facade.create_pessoal_context(idpessoa)
    return render(request, "pessoas/consultapessoa.html", contexto)


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
    data["html_form"] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def bloqueia_pessoa(request, idpessoa):
    facade.altera_status(idpessoa)
    return redirect("indexpessoal")


def edita_salario(request):
    c_pessoal = request.POST.get("idPessoal")
    c_salario = request.POST.get("Salario")
    c_horas_mensais = float(request.POST.get("HorasMensais"))
    c_valetransporte = request.POST.get("ValeTransporte")
    facade.save_salario(c_pessoal, c_salario, c_horas_mensais, c_valetransporte)
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
    facade.create_contracheque(c_mesreferencia, c_anoreferencia, c_valor, c_pessoal)
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
    facade.create_contracheque_itens(c_descricao, c_valor, c_registro, c_idcontracheque)
    data = facade.seleciona_contracheque(request, c_mes, c_ano, c_idpessoal)
    return data


def consulta_pessoa(request):
    idpes = request.GET.get("id_pessoal")
    contexto = facade.create_contexto_consulta_colaborador(idpes)
    data = facade.create_data_consulta_colaborador(request, contexto)
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
    colaboradores = facade.create_contexto_colaboradores_ativo()
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
    data = facade.create_data_form_adiciona_documento_colaborador(request, contexto)
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
    data = facade.create_data_form_adiciona_documento_colaborador(request, contexto)
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
        data = facade.create_data_form_adiciona_documento_colaborador(request, contexto)
    return data


def exclui_documento_colaborador(request):
    iddocpessoal = request.GET.get("iddocpessoal")
    contexto = facade.create_contexto_exclui_documento_colaborador(iddocpessoal)
    data = facade.create_data_form_exclui_documento_colaborador(request, contexto)
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
        data = facade.create_data_form_adiciona_fone_colaborador(request, contexto)
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
    data = facade.create_data_form_adiciona_conta_colaborador(request, contexto)
    return data


def altera_conta_colaborador(request):
    idcontapessoal = request.GET.get("idcontapessoal")
    idpessoal = request.GET.get("idpessoal")
    conta_form = facade.read_conta_database(idcontapessoal)
    tipo_conta = dict_tipo_conta()
    contexto = {
        "conta_form": conta_form,
        "idpessoal": idpessoal,
        "tipo_conta": tipo_conta,
    }
    data = facade.create_data_form_adiciona_conta_colaborador(request, contexto)
    return data


def salva_conta_colaborador(request):
    print(request.POST)
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
        data = facade.create_data_form_adiciona_conta_colaborador(request, contexto)
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
