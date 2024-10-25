import calendar
import datetime
import os
import ast
from django.db import connection

from datetime import datetime
from dateutil.relativedelta import relativedelta
from django.db.models import (
    Sum,
    F,
    ExpressionWrapper,
    IntegerField,
    DateField,
    When,
    Case,
    Value,
)
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal
from PIL import Image, ImageDraw
from despesas import facade as facade_multa
from pagamentos import facade as facade_pagamentos
from pagamentos.models import Recibo


from pessoas.forms import FormVale
from core.constants import (
    CATEGORIAS,
    TIPOPGTO,
    TIPOS_DOCS,
    TIPOS_FONES,
    TIPOS_CONTAS,
)
from pessoas.models import (
    Aquisitivo,
    DecimoTerceiro,
    Ferias,
    ParcelasDecimoTerceiro,
    Pessoal,
    Salario,
    DocPessoal,
    FonePessoal,
    ContaPessoal,
    Vales,
    ContraCheque,
    ContraChequeItens,
    CartaoPonto,
)
from website.models import FileUpload
from website.facade import (
    converter_mes_ano,
    nome_curto,
    extremos_mes,
    nome_curto_underscore,
    busca_arquivo_descricao,
)
from .itens_card import categorias_colaborador
from transefetiva.settings.settings import MEDIA_ROOT
from pessoas import classes
from pessoas import html_data

meses = [
    "JANEIRO",
    "FEVEREIRO",
    "MARÇO",
    "ABRIL",
    "MAIO",
    "JUNHO",
    "JULHO",
    "AGOSTO",
    "SETEMBRO",
    "OUTUBRO",
    "NOVEMBRO",
    "DEZEMBRO",
]
dias = [
    "SEGUNDA-FEIRA",
    "TERÇA-FEIRA",
    "QUARTA-FEIRA",
    "QUINTA-FEIRA",
    "SEXTA-FEIRA",
    "SÁBADO",
    "DOMINGO",
]


def create_contexto_categoria():
    return {"categorias": categorias_colaborador}


def create_contexto_colaboradores(categoria, status_colaborador):
    colaboradores = (
        Pessoal.objects.filter(
            TipoPgto="MENSALISTA", StatusPessoal=status_colaborador
        )
        if categoria == "MENSALISTA"
        else Pessoal.objects.filter(StatusPessoal=status_colaborador).exclude(
            TipoPgto="MENSALISTA"
        )
    )
    lista_colaboradores = [
        {
            "idpessoal": item.idPessoal,
            "nome": item.Nome,
            "nome_curto": nome_curto(item.Nome),
        }
        for item in colaboradores
    ]
    return {"colaboradores": lista_colaboradores}


def gerar_data_html(html_functions, request, contexto, data):
    data["mensagem"] = contexto["mensagem"]
    for html_func in html_functions:
        data = html_func(request, contexto, data)

    return JsonResponse(data)


def selecionar_categoria_html_data(request, contexto):
    data = {}
    contexto["mensagem"] = "Categoria selecionada"
    html_functions = [
        html_data.html_card_lista_colaboradores,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def modal_colaborador(id_pessoal, request):
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    hoje = datetime.today().date()
    anos_18 = hoje - relativedelta(years=18)
    contexto = {
        "colaborador": colaborador,
        "hoje": hoje.strftime("%Y-%m-%d"),
        "anos_18": anos_18.strftime("%Y-%m-%d"),
    }
    contexto.update({"categorias": CATEGORIAS})
    contexto.update({"tipos_pgto": TIPOPGTO})
    modal_html = html_data.html_modal_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})


def save_colaborador(request):
    id_pessoal = request.POST.get("id_pessoal")
    registro = {
        "Nome": request.POST.get("nome").upper(),
        "Endereco": request.POST.get("endereco").upper(),
        "Bairro": request.POST.get("bairro").upper(),
        "CEP": request.POST.get("cep"),
        "Cidade": request.POST.get("cidade").upper(),
        "Estado": request.POST.get("estado").upper(),
        "DataNascimento": datetime.strptime(
            request.POST.get("nascimento"), "%Y-%m-%d"
        ),
        "Categoria": request.POST.get("categoria"),
        "TipoPgto": request.POST.get("tipo_pgto"),
        "Mae": request.POST.get("mae").upper(),
        "Pai": request.POST.get("pai").upper(),
        "StatusPessoal": 1,
        "DataAdmissao": datetime.strptime(
            request.POST.get("admissao"), "%Y-%m-%d"
        ),
    }

    if id_pessoal:
        Pessoal.objects.filter(idPessoal=id_pessoal).update(**registro)
        return {"mensagem": "Colaborador atualizado com sucesso"}

    Pessoal.objects.create(**registro)
    return {"mensagem": "Colaborador cadastrado com sucesso"}


def modal_doc_colaborador(id_doc_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    id_documento = (
        request.POST.get("id_documento")
        if request.method == "POST"
        else request.GET.get("id_documento")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    documento = DocPessoal.objects.filter(idDocPessoal=id_documento).first()
    hoje = datetime.today().date()
    contexto = {
        "colaborador": colaborador,
        "documento": documento,
        "hoje": hoje.strftime("%Y-%m-%d"),
    }
    contexto.update({"tipos_docs": TIPOS_DOCS})
    modal_html = html_data.html_modal_doc_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})


def save_doc_colaborador(request):
    id_documento = request.POST.get("id_documento")
    tipo_documento = request.POST.get("categoria")
    documento = request.POST.get("documento").upper()
    data = datetime.strptime(request.POST.get("data"), "%Y-%m-%d")
    id_pessoal = request.POST.get("id_pessoal")

    registro = {
        "TipoDocumento": tipo_documento,
        "Documento": documento,
        "Data": data,
        "idPessoal_id": id_pessoal,
    }

    if id_documento:
        DocPessoal.objects.filter(idDocPessoal=id_documento).update(**registro)
        return {"mensagem": "Documento atualizado com sucesso"}

    documento = DocPessoal.objects.filter(
        idPessoal_id=id_pessoal, TipoDocumento=tipo_documento
    )
    if documento:
        return {
            "mensagem": f"Colaborador já possui {tipo_documento} cadastrado"
        }

    DocPessoal.objects.create(**registro)
    return {"mensagem": "Documento cadastrado com sucesso"}


def create_contexto_class_colaborador(request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    colaborador = classes.Colaborador(id_pessoal)
    return {
        "colaborador": colaborador,
    }


def documento_html_data(request, contexto):
    data = {}
    html_functions = [
        html_data.html_card_docs_colaborador,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def modal_fone_colaborador(id_doc_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    id_telefone = (
        request.POST.get("id_telefone")
        if request.method == "POST"
        else request.GET.get("id_telefone")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    telefone = FonePessoal.objects.filter(idFonePessoal=id_telefone).first()
    contexto = {
        "colaborador": colaborador,
        "telefone": telefone,
    }
    contexto.update({"tipos_fones": TIPOS_FONES})
    modal_html = html_data.html_modal_fone_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})


def save_fone_colaborador(request):
    id_telefone = request.POST.get("id_telefone")
    tipo_telefone = request.POST.get("categoria")
    telefone = request.POST.get("telefone")
    contato = request.POST.get("contato").upper()
    id_pessoal = request.POST.get("id_pessoal")

    registro = {
        "TipoFone": tipo_telefone,
        "Fone": telefone,
        "Contato": contato,
        "idPessoal_id": id_pessoal,
    }

    if id_telefone:
        FonePessoal.objects.filter(idFonePessoal=id_telefone).update(
            **registro
        )
        return {"mensagem": "Telefone atualizado com sucesso"}

    FonePessoal.objects.create(**registro)
    return {"mensagem": "Telefone cadastrado com sucesso"}


def telefone_html_data(request, contexto):
    data = {}
    html_functions = [
        html_data.html_card_fones_colaborador,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def modal_confirma_excluir_fone_colaborador(id_doc_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    id_telefone = (
        request.POST.get("id_telefone")
        if request.method == "POST"
        else request.GET.get("id_telefone")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    telefone = FonePessoal.objects.filter(idFonePessoal=id_telefone).first()
    contexto = {
        "colaborador": colaborador,
        "telefone": telefone,
    }
    modal_html = html_data.html_modal_confirma_excluir_fone_colaborador(
        request, contexto
    )
    return JsonResponse({"modal_html": modal_html})


def delete_fone_colaborador(request):
    if request.method == "POST":
        id_telefone = request.POST.get("id_telefone")
        telefone = FonePessoal.objects.filter(idFonePessoal=id_telefone)
        telefone.delete()
        return {"mensagem": "Telefone do colaborador excluido com sucesso"}

    return {"mensagem": "Não foi possível excluir telefone do colaborador"}


def modal_conta_colaborador(id_doc_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    id_conta = (
        request.POST.get("id_conta")
        if request.method == "POST"
        else request.GET.get("id_conta")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    conta = ContaPessoal.objects.filter(idContaPessoal=id_conta).first()
    contexto = {
        "colaborador": colaborador,
        "conta": conta,
    }
    contexto.update({"tipos_contas": TIPOS_CONTAS})
    modal_html = html_data.html_modal_conta_colaborador(request, contexto)
    return JsonResponse({"modal_html": modal_html})


def save_conta_colaborador(request):
    print(request.POST)
    id_conta = request.POST.get("id_conta")

    registro = {
        "Banco": request.POST.get("banco").upper(),
        "Agencia": request.POST.get("agencia").upper(),
        "Conta": request.POST.get("conta").upper(),
        "TipoConta": request.POST.get("categoria"),
        "Titular": request.POST.get("titular").upper(),
        "Documento": request.POST.get("documento"),
        "PIX": request.POST.get("pix"),
        "idPessoal_id": request.POST.get("id_pessoal"),
    }

    if id_conta:
        ContaPessoal.objects.filter(idContaPessoal=id_conta).update(**registro)
        return {"mensagem": "Conta atualizado com sucesso"}

    ContaPessoal.objects.create(**registro)
    return {"mensagem": "Conta cadastrado com sucesso"}


def conta_html_data(request, contexto):
    data = {}
    html_functions = [
        html_data.html_card_contas_colaborador,
    ]
    return gerar_data_html(html_functions, request, contexto, data)


def modal_confirma_excluir_conta_colaborador(id_doc_pessoal, request):
    id_pessoal = (
        request.POST.get("id_pessoal")
        if request.method == "POST"
        else request.GET.get("id_pessoal")
    )
    id_conta = (
        request.POST.get("id_conta")
        if request.method == "POST"
        else request.GET.get("id_conta")
    )
    colaborador = classes.Colaborador(id_pessoal) if id_pessoal else False
    conta = ContaPessoal.objects.filter(idContaPessoal=id_conta).first()
    contexto = {
        "colaborador": colaborador,
        "conta": conta,
    }
    modal_html = html_data.html_modal_confirma_excluir_conta_colaborador(
        request, contexto
    )
    return JsonResponse({"modal_html": modal_html})


def delete_conta_colaborador(request):
    print(request.POST)
    if request.method == "POST":
        id_conta = request.POST.get("id_conta")
        conta = ContaPessoal.objects.filter(idContaPessoal=id_conta)
        conta.delete()
        return {"mensagem": "Conta do colaborador excluida com sucesso"}

    return {"mensagem": "Não foi possível excluir conta do colaborador"}


def create_contexto_consulta_colaborador(id_pessoal):
    colaborador = classes.Colaborador(id_pessoal)
    colaborador_ant = get_colaborador(id_pessoal)
    aquisitivo = get_aquisitivo(colaborador_ant)
    multas = facade_multa.multas_pagar("MOTORISTA", id_pessoal)
    vales = get_vales_colaborador(colaborador_ant)
    saldo_vales = get_saldo_vales_colaborador(vales)
    verifica_decimo_terceiro((colaborador_ant))
    decimo_terceiro = get_decimo_terceiro_colaborador(colaborador_ant)
    decimo_terceiro = decimo_terceiro.order_by("-Ano")
    verifica_parcelas_decimo_terceiro(colaborador_ant)
    parcelas_decimo_terceiro = get_parcelas_decimo_terceiro(colaborador_ant)
    hoje = datetime.today().date()
    return {
        "colaborador": colaborador,
        "vales": vales,
        "saldo_vales": saldo_vales,
        "multas": multas,
        "decimo_terceiro": decimo_terceiro,
        "parcelas_decimo_terceiro": parcelas_decimo_terceiro,
        "hoje": hoje,
        "aquisitivo": aquisitivo,
    }


def list_pessoal_all():
    return list(Pessoal.objects.all())


def get_pessoal_all():
    return Pessoal.objects.all()


def get_pessoal_mensalista_ativo():
    return Pessoal.objects.filter(TipoPgto="MENSALISTA", StatusPessoal=True)


def get_pessoal_nao_mensalista_ativo():
    return Pessoal.objects.filter(StatusPessoal=True).exclude(
        TipoPgto="MENSALISTA"
    )


def get_pessoal(idpessoa: int):
    colaborador = Pessoal.objects.filter(idPessoal=idpessoa)
    return colaborador


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


def get_contracheque(idpessoal: int):
    contracheque = ContraCheque.objects.filter(idPessoal=idpessoal)
    return contracheque


def get_contrachequeid(idcontracheque: int):
    contracheque = ContraCheque.objects.filter(idContraCheque=idcontracheque)
    return contracheque


def get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    contracheque = ContraCheque.objects.filter(
        MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal
    )
    return contracheque


def get_contracheque_itens(idcontracheque: int):
    contracheque_itens = ContraChequeItens.objects.filter(
        idContraCheque_id=idcontracheque
    ).order_by("Registro")
    return contracheque_itens


def save_salario(idpessoal, salario, horasmensais, valetransporte):
    try:
        qs_salario = Salario.objects.get(idPessoal_id=idpessoal)
        obj = Salario(qs_salario)
        obj.idSalario = qs_salario.idSalario
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.ValeTransporte = valetransporte
        obj.idPessoal_id = idpessoal
    except Salario.DoesNotExist:
        obj = Salario()
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.ValeTransporte = valetransporte
        obj.idPessoal_id = idpessoal
    obj.save()


def edita_data_demissao(idpessoal, data_demissao):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    obj = colaborador
    obj.DataDemissao = data_demissao
    obj.save(update_fields=["DataDemissao"])


def create_vale(data, descricao, valor, idpessoal):
    obj = Vales()
    obj.Data = data
    obj.Descricao = descricao
    obj.Valor = valor
    obj.idPessoal_id = idpessoal
    obj.save()


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    colaborador = get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            salario = get_salario(idpessoal)
            if not busca_contracheque(
                meses[int(mesreferencia) - 1], anoreferencia, idpessoal
            ):
                obj = ContraCheque()
                obj.MesReferencia = meses[int(mesreferencia) - 1]
                obj.AnoReferencia = anoreferencia
                obj.Valor = valor
                obj.idPessoal_id = idpessoal
                obj.save()
                create_contracheque_itens(
                    "Salario", salario[0].Salario, "C", obj.idContraCheque
                )


def create_contracheque_itens(descricao, valor, registro, idcontracheque):
    if float(valor) > 0:
        if not busca_contrachequeitens(idcontracheque, descricao, registro):
            obj = ContraChequeItens()
            obj.Descricao = descricao
            obj.Valor = valor
            obj.Registro = registro
            obj.idContraCheque_id = idcontracheque
            obj.save()


def altera_contracheque_itens(contrachequeitens, valorhoraextra):
    if float(valorhoraextra) > 0:
        obj = contrachequeitens
        obj.Valor = valorhoraextra
        obj.save(update_fields=["Valor"])


def busca_contracheque(mesreferencia, anoreferencia, idpessoal):
    qs_contracheque = ContraCheque.objects.filter(
        MesReferencia=mesreferencia,
        AnoReferencia=anoreferencia,
        idPessoal=idpessoal,
    )
    if qs_contracheque:
        return True


def busca_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Descricao=descricao, Registro=registro
    )
    return contrachequeitens


def saldo_contracheque(idcontracheque):
    credito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=idcontracheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if not credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if not debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    return totais


def print_contracheque_context(idcontracheque):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = get_contracheque_itens(idcontracheque)
    colaborador = get_pessoal(contracheque[0].idPessoal_id)
    credito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="C"
    ).aggregate(Total=Sum("Valor"))
    debito = ContraChequeItens.objects.filter(
        idContraCheque=contracheque[0].idContraCheque, Registro="D"
    ).aggregate(Total=Sum("Valor"))
    if credito["Total"]:
        credito["Total"] = Decimal("0.00")
    if debito["Total"]:
        debito["Total"] = Decimal("0.00")
    totais = {
        "Credito": credito["Total"],
        "Debito": debito["Total"],
        "Liquido": credito["Total"] - debito["Total"],
    }
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "colaborador": colaborador,
        "totais": totais,
    }
    return contexto


def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            admissao = datetime.datetime(
                admissao.year, admissao.month, admissao.day
            )
            if not busca_cartaoponto_referencia(
                mesreferencia, anoreferencia, idpessoal
            ):
                referencia = calendar.monthrange(
                    int(anoreferencia), int(mesreferencia)
                )
                for x in range(1, referencia[1] + 1):
                    dia = "{}-{}-{}".format(anoreferencia, mesreferencia, x)
                    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
                    obj = CartaoPonto()
                    obj.Dia = dia
                    obj.Entrada = "07:00"
                    obj.Saida = "17:00"
                    if dia.weekday() == 5 or dia.weekday() == 6:
                        obj.Ausencia = dias[dia.weekday()]
                    else:
                        obj.Ausencia = ""
                    if dia < admissao:
                        obj.Ausencia = "-------"
                    obj.idPessoal_id = idpessoal
                    obj.save()


def busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = meses.index(mesreferencia) + 1
    else:
        mes = int(mesreferencia)
    dia = "{}-{}-{}".format(anoreferencia, mes, 1)
    dia = datetime.datetime.strptime(dia, "%Y-%m-%d")
    referencia = calendar.monthrange(int(anoreferencia), mes)
    diafinal = "{}-{}-{}".format(anoreferencia, mes, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, "%Y-%m-%d")
    cartaoponto = CartaoPonto.objects.filter(
        Dia__range=[dia, diafinal], idPessoal=idpessoal
    )
    if cartaoponto:
        return cartaoponto


def form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal):
    data = dict()
    c_instance = None
    if c_view == "edita_pessoa" or c_view == "exclui_pessoa":
        if c_idobj:
            c_instance = Pessoal.objects.get(idPessoal=c_idobj)
    if request.method == "POST":
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            save_id = form.save()
            if c_view == "cria_pessoa" or c_view == "edita_pessoa":
                data["save_id"] = save_id.idPessoal
                if c_view == "cria_pessoa":
                    save_salario(save_id.idPessoal, 0.00, 1, 0.00)
            else:
                data["save_id"] = save_id.idPessoal_id
        else:
            pass
    else:
        form = c_form(instance=c_instance)
    context = {
        "form": form,
        "c_idobj": c_idobj,
        "c_url": c_url,
        "c_view": c_view,
        "idpessoal": idpessoal,
    }
    data["html_modal"] = render_to_string(
        "pessoas/formpessoa.html", context, request=request
    )
    data["c_view"] = c_view
    c_return = JsonResponse(data)
    return c_return


def form_exclui_pessoal(request, c_idobj, c_url, c_view, idpessoal):
    data = dict()
    c_queryset = None
    if c_view == "exclui_pessoa":
        c_queryset = Pessoal.objects.get(idPessoal=c_idobj)
    # elif c_view == 'exclui_email_cliente':
    #     c_queryset = EMailContatoCliente.objects.get(idEmailContatoCliente=c_idobj)
    # elif c_view == 'exclui_fone_cliente':
    #     c_queryset = FoneContatoCliente.objects.get(idFoneContatoCliente=c_idobj)
    # elif c_view == 'exclui_cobranca_cliente':
    #     c_queryset = Cobranca.objects.get(idCobranca=c_idobj)
    # elif c_view == 'exclui_tabela_capacidade':
    #     c_queryset = TabelaCapacidade.objects.get(idTabelaCapacidade=c_idobj)
    # elif c_view == 'exclui_tabela_perimetro':
    #     c_queryset = TabelaPerimetro.objects.get(idTabelaPerimetro=c_idobj)
    if request.method == "POST":
        c_queryset.delete()
    context = {
        "c_url": c_url,
        "c_view": c_view,
        "c_queryset": c_queryset,
        "idpessoal": idpessoal,
    }
    data["html_form"] = render_to_string(
        "pessoas/formpessoa.html", context, request=request
    )
    data["c_view"] = c_view
    data["save_id"] = idpessoal
    c_return = JsonResponse(data)
    return c_return


# TODO: Refatoração
def create_contexto_colaboradores_ativo(status_colaborador):
    colaboradores = Pessoal.objects.filter(StatusPessoal=status_colaborador)
    lista = []
    hoje = datetime.datetime.today()
    for i in colaboradores:
        decimo_terceiro = DecimoTerceiro.objects.filter(
            idPessoal=i.idPessoal, Ano=hoje.year
        )
        lista.append(
            {
                "idpessoal": i.idPessoal,
                "nome": i.Nome,
                "nome_curto": nome_curto(i.Nome),
                "tipo_pgto": i.TipoPgto,
                "status_pessoal": i.StatusPessoal,
                "decimo_terceiro": decimo_terceiro,
            }
        )
    return lista


def create_recibos_colaborador(idpessoal):
    recibos = Recibo.objects.filter(idPessoal_id=idpessoal).order_by(
        "-DataRecibo", "-Recibo"
    )
    return {"recibos": recibos}


def html_recibos_colaborador(request, contexto, data):
    idpessoal = contexto["colaborador"]["idpes"]
    recibos = create_recibos_colaborador(idpessoal)
    contexto.update(recibos)
    data["html_recibos_colaborador"] = render_to_string(
        "pagamentos/reciboavulso.html", contexto, request=request
    )
    return data


def create_data_consulta_colaborador(request, contexto):
    tipo_pgto = contexto["colaborador"]["tipo_pgto"]
    data = dict()
    html_lista_colaboradores_ativo(request, contexto, data)
    html_card_foto_colaborador(request, contexto, data)
    html_card_info_colaborador(request, contexto, data)
    html_dados_colaborador(request, contexto, data)
    if tipo_pgto == "MENSALISTA":
        html_ferias_colaborador(request, contexto, data)
        html_decimo_terceiro(request, contexto, data)
    else:
        html_recibos_colaborador(request, contexto, data)
    html_vales_colaborador(request, contexto, data)
    html_multas_colaborador(request, contexto, data)
    data["colaborador"] = contexto["colaborador"]["idpes"]
    data["categoria"] = contexto["colaborador"]["categoria"]
    return JsonResponse(data)


def html_ferias_colaborador(request, contexto, data):
    data["html_ferias_colaborador"] = render_to_string(
        "pessoas/html_ferias_colaborador.html", contexto, request=request
    )
    return data


def html_vales_colaborador(request, contexto, data):
    data["html_vales_colaborador"] = render_to_string(
        "pessoas/card_vales_colaborador.html", contexto, request=request
    )
    return data


def html_multas_colaborador(request, contexto, data):
    data["html_multas_colaborador"] = render_to_string(
        "pessoas/html_multas_colaborador.html", contexto, request=request
    )
    return data


def html_dados_colaborador(request, contexto, data):
    data["html_dados_colaborador"] = render_to_string(
        "pessoas/html_dados_colaborador.html", contexto, request=request
    )
    data["tipo_pgto"] = contexto["colaborador"]["tipo_pgto"]
    return data


def html_decimo_terceiro(request, contexto, data):
    data["html_decimo_terceiro"] = render_to_string(
        "pessoas/html_decimo_terceiro.html", contexto, request=request
    )
    return data


def salva_foto_colaborador(idpessoal, arquivo):
    obj = Pessoal.objects.get(idPessoal=idpessoal)
    if obj.Foto:
        file = f"{MEDIA_ROOT}/{obj.Foto}"
        if os.path.isfile(file):
            os.remove(file)
    obj.Foto = arquivo
    obj.save(update_fields=["Foto"])
    return obj


def gera_decimo_terceiro():
    colaboradores = Pessoal.objects.filter(
        TipoPgto="MENSALISTA", StatusPessoal=True, DataDemissao__isnull=True
    )
    hoje = datetime.datetime.today()
    for x in colaboradores:
        colaborador_decimo = DecimoTerceiro.objects.filter(
            idPessoal=x.idPessoal, Ano=hoje.year
        )
        if not colaborador_decimo:
            salario = Salario.objects.get(idPessoal=x.idPessoal)
            admissao = x.DataAdmissao
            if admissao.year < hoje.year:
                avos = 12
            else:
                avos = 12 - admissao.month
                if admissao.day < 17:
                    avos += 1
            valor = salario.Salario / 12 * avos
            obj = DecimoTerceiro()
            obj.Ano = hoje.year
            obj.ValorBase = salario.Salario
            obj.Dozeavos = avos
            obj.Valor = valor
            obj.idPessoal_id = x.idPessoal
            obj.save()
            new_obj = obj.idDecimoTerceiro
            gera_decimo_terceiro_parcelas(new_obj, valor)


def gera_decimo_terceiro_parcelas(idDecimoTerceiro, valor):
    for i in range(1, 3):
        obj = ParcelasDecimoTerceiro()
        obj.Valor = round(valor / 2, 2)
        obj.Parcela = i
        obj.idDecimoTerceiro_id = idDecimoTerceiro
        obj.save()


def atualiza_decimno_terceito_parcelas(idDecimoTerceiro):
    pass


def create_contexto_print_decimo_terceiro(idpes, idparcela):
    colaborador = Colaborador(idpes).__dict__
    contexto = {"colaborador": colaborador, "idparcela": idparcela}
    return contexto


def create_contexto_verbas_rescisoria(idpessoal):
    colaborador = Colaborador(idpessoal).__dict__
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=idpessoal)
        .order_by("-DataInicial")
        .first()
    )
    variavel = dict()
    variavel["admissao"] = colaborador["data_admissao"]
    variavel["demissao"] = colaborador["data_demissao"]
    dias_admitido_colaborador = facade_pagamentos.dias_admitido(
        variavel["admissao"], variavel["demissao"]
    )
    if dias_admitido_colaborador > 16:
        meses_ferias = rescisao_ferias_meses(
            aquisitivo.DataInicial, aquisitivo.DataFinal
        )
        # TODO Na rescisão precisa verificar os pagamento de 13º já efetuados
        meses_decimo_terceiro = rescisao_descimo_terceiro_meses(
            colaborador["data_admissao"], colaborador["data_demissao"]
        )
    else:
        meses_ferias = 0
        meses_decimo_terceiro = 0
    rescisao_salario = colaborador["salario"][0]["salario"]
    rescisao_ferias = rescisao_salario / 12 * meses_ferias
    rescisao_terco_ferias = rescisao_ferias / 3
    rescisao_descimo_terceiro = rescisao_salario / 12 * meses_decimo_terceiro
    _mes_ano = datetime.datetime.strftime(
        colaborador["data_demissao"], "%B/%Y"
    )
    #  folha = facade_pagamentos.create_contexto_funcionario(_mes_ano, idpessoal)
    folha = create_contexto_contra_cheque_colaborador(
        idpessoal, _mes_ano, "PAGAMENTO"
    )
    rescisao = [
        {
            "salario": round(rescisao_salario, 2),
            "ferias": round(rescisao_ferias, 2),
            "meses_ferias": meses_ferias,
            "terco_ferias": round(rescisao_terco_ferias, 2),
            "decimo_terceiro": round(rescisao_descimo_terceiro, 2),
            "meses_decimo_terceiro": meses_decimo_terceiro,
            "folha_contra_cheque_itens": folha["contra_cheque_itens"],
        }
    ]
    print(folha["contra_cheque_itens"])
    return {"rescisao": rescisao, "colaborador": colaborador}


def create_data_verbas_rescisoria(request, contexto):
    data = dict()
    html_verbas_rescisoria(request, contexto, data)
    return JsonResponse(data)


def html_verbas_rescisoria(request, contexto, data):
    data["html_verbas_rescisoria"] = render_to_string(
        "pessoas/html_verbas_rescisoria.html", contexto, request=request
    )
    return data


def rescisao_ferias_meses(data_inicial, data_final):
    dia_inicial = data_inicial.day
    if dia_inicial < 16:
        mes_inicial = data_inicial.month
    else:
        mes_inicial = data_inicial.month + 1
    dia_final = data_final.day
    if dia_final > 14:
        mes_final = data_final.month
    else:
        mes_final = data_final.month - 1
    meses = mes_final - mes_inicial + 1
    return meses


def rescisao_descimo_terceiro_meses(data_inicial, data_final):
    dia_inicial = data_inicial.day
    ano_inicial = data_inicial.year
    ano_final = data_final.year
    if dia_inicial < 16:
        mes_inicial = data_inicial.month
    else:
        mes_inicial = data_inicial.month + 1
    dia_final = data_final.day
    if dia_final > 14:
        mes_final = data_final.month
    else:
        mes_final = data_final.month - 1
    if ano_inicial != ano_final:
        mes_inicial = 1
    meses = mes_final - mes_inicial + 1
    return meses


def html_form_confirma_exclusao(request, contexto, data):
    data["html_form_confirma_exclusao"] = render_to_string(
        "pessoas/html_form_confirma_exclusao.html", contexto, request=request
    )
    return data


# TODO renomear função já existe fazendo a mesma função.
def create_data_form_exclui_periodo_ferias(request, contexto):
    data = dict()
    html_form_confirma_exclusao(request, contexto, data)
    return JsonResponse(data)


def create_contexto_exclui_ferias(idferias):
    ferias = Ferias.objects.get(idFerias=idferias)
    inicio = datetime.datetime.strftime(ferias.DataInicial, "%d/%m/%Y")
    final = datetime.datetime.strftime(ferias.DataFinal, "%d/%m/%Y")
    idpessoal = ferias.idPessoal_id
    mensagem = (
        f"Confirma a exclusão do periodo de férias de: {inicio} - {final}?"
    )
    js_class = "js-exclui-periodo-ferias"
    return {
        "mensagem": mensagem,
        "idobj": idferias,
        "idpessoal": idpessoal,
        "js_class": js_class,
    }


def exclui_periodo_ferias_base_dados(idferias):
    ferias = Ferias.objects.get(idFerias=idferias)
    ferias.delete()


def create_data_form_paga_decimo_terceiro(request, contexto):
    data = dict()
    html_form_paga_decimo_terceiro(request, contexto, data)
    return JsonResponse(data)


def html_form_paga_decimo_terceiro(request, contexto, data):
    data["html_form_paga_decimo_terceiro"] = render_to_string(
        "pessoas/html_form_paga_decimo_terceiro.html",
        contexto,
        request=request,
    )
    return data


def paga_parcela(idparcela, data_pgto):
    obj = ParcelasDecimoTerceiro.objects.get(
        idParcelasDecimoTerceiro=idparcela
    )
    obj.DataPgto = data_pgto
    obj.Pago = True
    obj.save(update_fields=["DataPgto", "Pago"])


# Deixa a imagem circular e salva como png, utilizada na impressão da ficha cadastral
def prepare_mask(size, antialias=2):
    mask = Image.new("L", (size[0] * antialias, size[1] * antialias), 0)
    ImageDraw.Draw(mask).ellipse((0, 0) + mask.size, fill=255)
    return mask.resize(size, Image.ANTIALIAS)


def crop(im, s):
    w, h = im.size
    k = w / s[0] - h / s[1]
    if k > 0:
        im = im.crop(((w - h) / 2, 0, (w + h) / 2, h))
    elif k < 0:
        im = im.crop((0, (h - w) / 2, w, (h + w) / 2))
    return im.resize(s, Image.ANTIALIAS)


def do_crop(img):
    size = (200, 200)
    try:
        im = Image.open(img)
        im = crop(im, size)
        im.putalpha(prepare_mask(size, 4))
        output = str(img).replace("jpg", "png").replace("jpeg", "png")
        im.save(output)
        return output
    except:
        return False


def create_data_form_salario_colaborador(request, contexto):
    data = dict()
    html_form_salario_colaborador(request, contexto, data)
    return JsonResponse(data)


def html_form_salario_colaborador(request, contexto, data):
    data["html_form_salario_colaborador"] = render_to_string(
        "pessoas/html_form_salario_colaborador.html", contexto, request=request
    )
    return data


def valida_salario_colaborador(request):
    msg = dict()
    error = False
    salario = float(request.POST.get("valor_salario"))
    if salario < 1.00:
        msg["erro_salario"] = "O salário deve ser maior que R$ 0,99."
        error = True
    return error, msg


def read_salario_post(request):
    conta_post = dict()
    conta_post["salario"] = request.POST.get("valor_salario")
    conta_post["transporte"] = request.POST.get("valor_transporte")
    conta_post["idpessoal"] = request.POST.get("idpessoal")
    conta_post["idsalario"] = request.POST.get("idsalario")
    return conta_post


def read_salario_database(idpessoal):
    salario = Salario.objects.get(idPessoal=idpessoal)
    conta_database = dict()
    conta_database["salario"] = str(salario.Salario)
    conta_database["transporte"] = str(salario.ValeTransporte)
    conta_database["idpessoal"] = salario.idPessoal
    conta_database["idsalario"] = salario.idSalario
    return conta_database


def altera_salario(salario, idsalario):
    obj = Salario.objects.get(idSalario=idsalario)
    obj.Salario = salario["salario"]
    obj.ValeTransporte = salario["transporte"]
    # obj.idSalario = obj.Salario
    # obj.idPessoal = obj.idPessoal
    obj.save(update_fields=["Salario", "ValeTransporte"])


def salva_ferias_aquisitivo_inicial(colaborador):
    obj = Ferias()
    obj.DataInicial = colaborador.data_admissao


def create_data_form_periodo_ferias(request, contexto):
    data = dict()
    html_form_periodo_ferias(request, contexto, data)
    return JsonResponse(data)


def html_form_periodo_ferias(request, contexto, data):
    data["html_form_periodo_ferias"] = render_to_string(
        "pessoas/html_form_periodo_ferias.html", contexto, request=request
    )
    return data


# TODO Fazer uma validação conforme data de admissao e pagamentos de salarios
def valida_periodo_ferias(request):
    msg = dict()
    error = False
    hoje = datetime.datetime.today()
    data_inicio = datetime.datetime.strptime(
        request.POST.get("inicio"), "%Y-%m-%d"
    )
    data_termino = datetime.datetime.strptime(
        request.POST.get("termino"), "%Y-%m-%d"
    )
    dias = (data_termino - data_inicio).days + 1
    if dias < 5:
        msg["erro_termino"] = "O Período não pode ser menor que 5 dias."
        error = True
    if dias > 30:
        msg["erro_termino"] = "O Período não pode ser maior que 30 dias."
        error = True
    return error, msg


def read_periodo_ferias_post(request):
    periodo_ferias_post = dict()
    periodo_ferias_post["inicio"] = request.POST.get("inicio")
    periodo_ferias_post["termino"] = request.POST.get("termino")
    periodo_ferias_post["idpessoal"] = request.POST.get("idpessoal")
    return periodo_ferias_post


def salva_periodo_ferias_colaborador(idpessoal, inicio, termino, idaquisitivo):
    print(len(connection.queries))
    inicio = datetime.datetime.strptime(inicio, "%Y-%m-%d")
    termino = datetime.datetime.strptime(termino, "%Y-%m-%d")
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    admissao = colaborador.DataAdmissao
    demissao = colaborador.DataDemissao
    valores_colaborador = Salario.objects.get(idPessoal=idpessoal)
    var = dict()
    var["conducao"] = valores_colaborador.ValeTransporte
    mes_inicio = inicio.month
    mes_termino = termino.month
    if mes_inicio == 12:
        mes_termino += 12
    mes_ano = datetime.datetime.strftime(inicio, "%B/%Y")
    mes, ano = converter_mes_ano(mes_ano)
    pdm, udm = extremos_mes(mes, ano)
    cp = CartaoPonto.objects.filter(Dia__range=[pdm, udm], idPessoal=idpessoal)
    if not cp:
        facade_pagamentos.create_cartao_ponto(
            idpessoal, pdm, udm, admissao, demissao, var
        )
    if mes_termino > mes_inicio:
        nova_data = inicio + relativedelta(months=+1)
        mes_ano = datetime.datetime.strftime(nova_data, "%B/%Y")
        mes, ano = converter_mes_ano(mes_ano)
        pdm, udm = extremos_mes(mes, ano)
        cp = CartaoPonto.objects.filter(
            Dia__range=[pdm, udm], idPessoal=idpessoal
        )
        if not cp:
            facade_pagamentos.create_cartao_ponto(
                idpessoal, pdm, udm, admissao, demissao, var
            )
        if mes_termino == mes_inicio + 2:
            nova_data = nova_data + relativedelta(months=+1)
            mes_ano = datetime.datetime.strftime(nova_data, "%B/%Y")
            mes, ano = converter_mes_ano(mes_ano)
            pdm, udm = extremos_mes(mes, ano)
            cp = CartaoPonto.objects.filter(
                Dia__range=[pdm, udm], idPessoal=idpessoal
            )
            if not cp:
                facade_pagamentos.create_cartao_ponto(
                    idpessoal, pdm, udm, admissao, demissao, var
                )
    print(len(connection.queries))
    CartaoPonto.objects.filter(
        Dia__range=[inicio, termino], idPessoal=idpessoal
    ).update(Ausencia="FÉRIAS", Conducao=0, Remunerado=0, CarroEmpresa=0)
    print(len(connection.queries))
    obj = Ferias()
    print(len(connection.queries))
    obj.DataInicial = inicio
    obj.DataFinal = termino
    obj.idPessoal_id = idpessoal
    obj.idAquisitivo_id = idaquisitivo
    obj.save()
    print(len(connection.queries))


def create_contexto_print_ferias(idpes, idaquisitivo, idparcela):
    colaborador = Colaborador(idpes).__dict__
    colaborador_model = get_colaborador(idpes)
    aquisitivo = Aquisitivo.objects.filter(idAquisitivo=idaquisitivo)[0]
    contra_cheque = ContraCheque.objects.filter(idPessoal=colaborador_model)
    contra_cheque_annotate = contra_cheque_ano_mes_integer(contra_cheque)
    contra_cheque_selecionado = get_contra_cheque_aquisitivo(
        aquisitivo, contra_cheque_annotate
    )
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque_selecionado)
    salario = get_salario_contra_cheque(contra_cheque_itens)
    #  aquisitivo = Aquisitivo.objects.get(idAquisitivo=idaquisitivo)
    contexto = {
        "colaborador": colaborador,
        "aquisitivo": aquisitivo,
        "idparcela": idparcela,
        "salario_aquisitivo": salario,
    }
    return contexto


def create_data_form_altera_demissao(request, contexto):
    data = dict()
    html_form_altera_demissao(request, contexto, data)
    return JsonResponse(data)


def html_form_altera_demissao(request, contexto, data):
    data["html_modal"] = render_to_string(
        "pessoas/modal_data_demissao.html",
        contexto,
        request=request,
    )
    print(data)
    return data


# TODO Fazer uma validação conforme data de admissao e pagamentos de salarios
def valida_demissao_colaborador(request):
    msg = dict()
    error = False
    hoje = datetime.datetime.today()
    data_demissao = datetime.datetime.strptime(
        request.POST.get("demissao"), "%Y-%m-%d"
    )
    if data_demissao > hoje:
        msg["erro_demissao"] = "Você não pode utilizar uma data futura."
        error = True
    return error, msg


def read_demissao_post(request):
    demissao_post = dict()
    demissao_post["demissao"] = datetime.datetime.strptime(
        request.POST.get("demissao"), "%Y-%m-%d"
    )
    demissao_post["idpessoal"] = request.POST.get("idpessoal")
    return demissao_post


def read_demissao_database(idpessoal):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    demissao_database = dict()
    demissao_database["demissao"] = colaborador.DataDemissao
    demissao_database["idpessoal"] = colaborador.idPessoal
    return demissao_database


def salva_demissao(idpessoal, demissao):
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    aquisitivo = (
        Aquisitivo.objects.filter(idPessoal=idpessoal)
        .order_by("-DataInicial")
        .first()
    )
    obj = Pessoal(colaborador)
    obj.idPessoal = idpessoal
    obj.DataDemissao = demissao
    obj.save(update_fields=["DataDemissao"])
    obj = Aquisitivo(aquisitivo)
    obj.idAquisitivo = aquisitivo.idAquisitivo
    obj.DataFinal = demissao
    obj.save(update_fields=["DataFinal"])


def altera_status(idpessoal):
    """
        Altera o status do colaborador usando XOR Toggle
    Args:
        idpessoal: Chave primária

    """
    colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    colaborador.StatusPessoal ^= True
    colaborador.save()


def aquisitivo_save(data_inicial, data_final, colaborador):
    """
        Salva no db o período aquisitito do colaborador
    Args:
        data_inicial: Data inicial do período
        data_final: Data final do período
        colaborador: Colaborador

    """
    Aquisitivo.objects.create(
        DataInicial=data_inicial,
        DataFinal=data_final,
        idPessoal=colaborador,
    )


def get_colaborador(idpessoal):
    """
        Recebe do db o colaborador com a primary key informada
        como argumento
    Args:
        idpessoal: Primary Key

    Returns:
        colaborador: type -> pessoas.models.Pessoal

    """
    try:
        colaborador = Pessoal.objects.get(idPessoal=idpessoal)
    except Pessoal.DoesNotExist:  # pylint: disable=no-member
        colaborador = False
    return colaborador


def get_aquisitivo(colaborador):
    """
        Recebe do db os aquisitivos do colaborador informado como
        argumento
    Args:
        colaborador: pessoas.models.Pessoal

    Returns:
        aquisitivo: type -> django.db.models.query.Queryset

    """
    try:
        aquisitivo = Aquisitivo.objects.filter(idPessoal=colaborador).order_by(
            "DataInicial"
        )
    except Aquisitivo.DoesNotExist:  # pylint: disable=no-member
        aquisitivo = False
    return aquisitivo


def aquisitivo_admissao(colaborador):
    """
        Verifica se o colaborador tem aquisitivo no db, caso não tenha
        cria aquisitivo com a data de admissão como data inicial e como
        data final o dia em que completa 1 ano.
    Args:
        colaborador: pessoas.models.Pessoal

    """
    if colaborador.TipoPgto == "MENSALISTA":
        if not get_aquisitivo(colaborador):
            data_inicial = colaborador.DataAdmissao
            data_final = data_inicial + relativedelta(years=+1, days=-1)
            aquisitivo_save(data_inicial, data_final, colaborador)


def aquisitivo_aniversario(colaborador):
    """
        Verifica se já possui ao menos 1 aquisitivo no db, caso tenha
        e passado o ultimo aquisitivo como datas inicial e final e
        cria aquisitivos anuais até a data final for maior que a data
        de hoje.
    Args:
        colaborador:

    """
    aquisitivo = get_aquisitivo(colaborador)
    if aquisitivo:
        ultimo_aquisitivo = aquisitivo.last()
        data_inicial = ultimo_aquisitivo.DataInicial
        data_final = ultimo_aquisitivo.DataFinal
        while data_final < datetime.datetime.now().date():
            data_inicial = data_inicial + relativedelta(years=+1)
            data_final = data_final + relativedelta(years=+1)
            aquisitivo_save(data_inicial, data_final, colaborador)


def get_contra_cheque_descricao(colaborador, descricao):
    contra_cheque_descricao = ContraCheque.objects.filter(
        idPessoal=colaborador, Descricao=descricao
    )
    return contra_cheque_descricao


def contra_cheque_ano_mes_integer(query):
    """
        Adiciona um campo na query contra cheque passada como
        parametro, que contem o ano e o mes em forma integer
        utilizada para ordenar decrescente a query
    Args:
        query: django.db.models.query.Queryset

    Returns:
        query: type -> django.db.models.query.Queryset, ordernada
        por ano_mes decrescente

    """
    query = query.annotate(
        mes=ExpressionWrapper(
            Case(
                When(MesReferencia="JANEIRO", then=Value(1)),
                When(MesReferencia="FEVEREIRO", then=Value(2)),
                When(MesReferencia="MARÇO", then=Value(3)),
                When(MesReferencia="ABRIL", then=Value(4)),
                When(MesReferencia="MAIO", then=Value(5)),
                When(MesReferencia="JUNHO", then=Value(6)),
                When(MesReferencia="JULHO", then=Value(7)),
                When(MesReferencia="AGOSTO", then=Value(8)),
                When(MesReferencia="SETEMBRO", then=Value(9)),
                When(MesReferencia="OUTUBRO", then=Value(10)),
                When(MesReferencia="NOVEMBRO", then=Value(11)),
                When(MesReferencia="DEZEMBRO", then=Value(12)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            output_field=IntegerField(),
        ),
        ano_mes_integer=ExpressionWrapper(
            F("AnoReferencia") * 100 + F("mes"),
            output_field=DateField(),
        ),
    )
    query = query.order_by("-ano_mes_integer")
    return query


def get_contra_cheque_aquisitivo(
    aquisitivo_selecionado, contra_cheque_annotate
):
    """
        Seleciona o contra cheque referente a data final
        do aquisitivo selecionado, passado como parametro.
        Cria a variavel ano_mes para comparar com o campo
        annotate ano_mes_integer criado nos contra cheques
        do colaborador e passado como parametro.
    Args:
        aquisitivo_selecionado: pessoas.models.Aquisitivo
        contra_cheque_annotate: django.db.models.query.Queryset

    Returns:
        contra cheque: type -> pessoas.models.ContraCheque

    """
    if aquisitivo_selecionado:
        ano = aquisitivo_selecionado.DataFinal.year
        mes = aquisitivo_selecionado.DataFinal.month
        # removido pegando a mes e ano corretos 26/07/2024
        #  ano = 2022
        #  mes = 12
        ano_mes = ano * 100 + mes
        contra_cheque_selecionado = None
        for itens in contra_cheque_annotate:
            if ano_mes == itens.ano_mes_integer:
                contra_cheque_selecionado = itens
                break
        return contra_cheque_selecionado


def get_contra_cheque_itens(contra_cheque):
    """
        Recebe do db os itens referente ao contra
        cheque informado como argumento.
    Args:
        contra_cheque: pessoas.models.ContraCheque

    Returns:
        contra_cheque_itens: type -> django.db.models.query.Queryset

    """
    if contra_cheque:
        contra_cheque_itens = ContraChequeItens.objects.filter(
            idContraCheque=contra_cheque
        )
    return contra_cheque_itens


def get_salario_contra_cheque(contra_cheque_itens):
    """
        Verifica nos itens do contra cheque o que tem
        como descricao "SALARIO" e retorna o valor
    Args:
        contra_cheque_itens: django.db.models.query.Queryset

    Returns:
        salario: -> decimal.Decimal

    """
    for itens in contra_cheque_itens:
        if itens.Descricao == "SALARIO":
            salario = round(itens.Valor / int(itens.Referencia[:-1]) * 30)
            return salario
            break
    return False


def html_card_foto_colaborador(request, contexto, data):
    data["html_card_foto_colaborador"] = render_to_string(
        "pessoas/card_foto_colaborador.html", contexto, request=request
    )
    return data


def html_card_info_colaborador(request, contexto, data):
    data["html_card_info_colaborador"] = render_to_string(
        "pessoas/card_info_colaborador.html", contexto, request=request
    )
    return data


def html_card_contra_cheque_colaborador(request, contexto, data):
    data["html_card_contra_cheque_colaborador"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    data["mes_ano"] = contexto["mes_ano"]
    return data


def create_contexto_contra_cheque(idpessoal, idselecionado, descricao):
    colaborador = classes.Colaborador(idpessoal).__dict__
    colaborador_futuro = get_colaborador(idpessoal)
    contas = get_contas_bancaria_colaborador(colaborador_futuro)
    if descricao == "FERIAS":
        contra_cheque = create_contexto_contra_cheque_ferias(
            idpessoal, idselecionado, descricao
        )
    elif descricao[:15] == "DECIMO TERCEIRO":
        contra_cheque = create_contexto_contra_cheque_13(
            idpessoal, idselecionado, descricao
        )
    elif descricao == "ADIANTAMENTO":
        # TODO Corrigir
        contra_cheque = idselecionado
    elif descricao == "PAGAMENTO":
        # TODO Corrigir
        contra_cheque = idselecionado
    if contas:
        update_contas_bancaria_obs(contra_cheque, contas, "contas")
    mes_ano = f"{contra_cheque.MesReferencia}/{contra_cheque.AnoReferencia}"
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
    contra_cheque_itens = contra_cheque_itens.order_by("idContraChequeItens")
    credito, debito, saldo_contra_cheque = get_saldo_contra_cheque(
        contra_cheque_itens
    )
    decimo_terceiro = get_decimo_terceiro_colaborador(colaborador_futuro)
    decimo_terceiro = decimo_terceiro.order_by("-Ano")
    parcelas_decimo_terceiro = get_parcelas_decimo_terceiro(colaborador_futuro)
    contexto = {
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
        "mes_ano": mes_ano,
        "credito": credito,
        "debito": debito,
        "saldo_contra_cheque": saldo_contra_cheque,
        "decimo_terceiro": decimo_terceiro,
        "parcelas_decimo_terceiro": parcelas_decimo_terceiro,
        "colaborador": colaborador,
        "tipo": descricao,
        "idpessoal": idpessoal,
    }
    idcontracheque = contra_cheque.idContraCheque
    file = get_file_contra_cheque(idcontracheque)
    contexto.update({"file": file})
    return contexto


def create_contexto_contra_cheque_ferias(idpessoal, idselecionado, descricao):
    idaquisitivo = idselecionado
    contra_cheque = busca_contra_cheque_aquisitivo(
        idpessoal, idaquisitivo, descricao
    )
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
    if not contra_cheque_itens:
        create_contra_cheque_itens(descricao, 0.00, "C", "30d", contra_cheque)
        if not busca_um_terco_ferias(contra_cheque_itens):
            create_contra_cheque_itens(
                "1/3 FERIAS", 0.00, "C", "30d", contra_cheque
            )
    atualiza_salario_ferias_dias_referencia(idpessoal, idaquisitivo)
    return contra_cheque


def create_contexto_contra_cheque_13(idpessoal, idselecionado, descricao):
    idparcela = idselecionado
    print(f"[INFO - 1] {idselecionado}")
    contra_cheque = busca_contra_cheque_parcela(
        idpessoal, idparcela, descricao[:15]
    )
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
    if not contra_cheque_itens:
        create_contra_cheque_itens(descricao, 0.00, "C", "12da", contra_cheque)
    atualiza_dozeavos_decimo_terceiro(idpessoal, idparcela, descricao)
    return contra_cheque


def update_contas_bancaria_obs(contra_cheque, contas, chave):
    dict_contas = dict()
    for index, conta in enumerate(contas):
        dict_contas[index + 1] = {}
        if conta["PIX"]:
            dict_contas[index + 1]["PIX"] = conta["PIX"]
        if conta["Banco"]:
            dict_contas[index + 1]["BANCO"] = conta["Banco"]
        if conta["Agencia"]:
            dict_contas[index + 1]["AGENCIA"] = conta["Agencia"]
        if conta["Conta"]:
            dict_contas[index + 1]["CONTA"] = conta["Conta"]
        if conta["TipoConta"]:
            dict_contas[index + 1]["TIPO"] = conta["TipoConta"]
        if conta["Titular"]:
            dict_contas[index + 1]["TITULAR"] = conta["Titular"]
        if conta["Documento"]:
            dict_contas[index + 1]["CPF"] = conta["Documento"]
    try:
        dict_obs = ast.literal_eval(contra_cheque.Obs)
        if not dict_obs.get("contas"):
            dict_obs["contas"] = ""
    except:
        dict_obs = dict({"contas": ""})
    if dict_obs["contas"] != dict_contas:
        dict_obs["contas"] = dict_contas
        obj = contra_cheque
        obj.Obs = dict_obs
        obj.save()


def atualiza_salario_ferias_dias_referencia(idpessoal, idaquisitivo):
    """

    Args:
        idpessoal:
        idaquisitivo:

    Returns:


    """
    colaborador = get_colaborador(idpessoal)
    aquisitivo = get_aquisitivo_id(idaquisitivo)
    contra_cheque = get_contra_cheque_descricao(colaborador, "PAGAMENTO")
    contra_cheque = contra_cheque_ano_mes_integer(contra_cheque)
    contra_cheque = get_contra_cheque_aquisitivo(aquisitivo, contra_cheque)
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
    salario_contra_cheque = get_salario_contra_cheque(contra_cheque_itens)
    faltas = aquisitivo_faltas(colaborador, aquisitivo)
    salario_ferias = aquisitivo_salario_ferias(salario_contra_cheque, faltas)
    mes = aquisitivo.DataFinal.month
    ano = aquisitivo.DataFinal.year
    contra_cheque_ferias = get_contra_cheque_mes_ano_descricao(
        colaborador, mes, ano, "FERIAS"
    )
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque_ferias)
    contra_cheque_item = contra_cheque_itens.filter(Descricao="FERIAS")
    update_contra_cheque_item_valor(contra_cheque_item, salario_ferias)
    referencia = tabela_faltas_aquisitivo(faltas)
    update_contra_cheque_item_referencia(contra_cheque_item, referencia)
    contra_cheque_item = contra_cheque_itens.filter(Descricao="1/3 FERIAS")
    update_contra_cheque_item_valor(contra_cheque_item, salario_ferias / 3)
    update_contra_cheque_item_referencia(contra_cheque_item, referencia)
    return (
        colaborador,
        aquisitivo,
        contra_cheque,
        contra_cheque_itens,
        salario_contra_cheque,
        salario_ferias,
        faltas,
        referencia,
        contra_cheque_ferias,
    )


def atualiza_dozeavos_decimo_terceiro(idpessoal, idparcela, descricao):
    colaborador = get_colaborador(idpessoal)
    hoje = datetime.datetime.today()
    salario = Salario.objects.get(idPessoal=idpessoal)
    admissao = colaborador.DataAdmissao
    if admissao.year < hoje.year:
        avos = 12
    else:
        avos = 12 - admissao.month
        if admissao.day < 17:
            avos += 1
    valor = salario.Salario / 12 * avos
    parcela = get_parcelas_decimo_terceiro_id(idparcela)
    decimo_terceiro = get_decimo_terceiro_id(parcela.idDecimoTerceiro_id)
    decimo_terceiro.ValorBase = salario.Salario
    decimo_terceiro.Valor = valor
    decimo_terceiro.Dozeavos = avos
    decimo_terceiro.save()
    parcelas = ParcelasDecimoTerceiro.objects.filter(
        idDecimoTerceiro=decimo_terceiro
    )
    parcelas.update(Valor=valor / 2)
    if parcela.Parcela == 1:
        mes = 11
    else:
        mes = 12
    ano = parcela.idDecimoTerceiro.Ano
    contra_cheque_decimo_terceiro = get_contra_cheque_mes_ano_descricao(
        colaborador, mes, ano, "DECIMO TERCEIRO"
    )
    contra_cheque_itens = get_contra_cheque_itens(
        contra_cheque_decimo_terceiro
    )
    contra_cheque_item = contra_cheque_itens.filter(Descricao=descricao)
    update_contra_cheque_item_valor(contra_cheque_item, valor / 2)
    update_contra_cheque_item_referencia(contra_cheque_item, f"{avos}a")


def get_decimo_terceiro_id(id_decimo_terceiro):
    decimo_terceiro = DecimoTerceiro.objects.get(
        idDecimoTerceiro=id_decimo_terceiro
    )
    return decimo_terceiro


def get_salarios_aquisitivo(colaborador, aquisitivos):
    contra_cheque = get_contra_cheque_descricao(colaborador, "PAGAMENTO")
    contra_cheque = contra_cheque_ano_mes_integer(contra_cheque)
    salarios = []
    for itens in aquisitivos:
        aquisitivo_selecionado = get_aquisitivo_id(itens.idAquisitivo)
        contra_cheque_aquisitivo = get_contra_cheque_aquisitivo(
            aquisitivo_selecionado, contra_cheque
        )
        if contra_cheque_aquisitivo:
            contra_cheque_itens = get_contra_cheque_itens(
                contra_cheque_aquisitivo
            )
            salario_contra_cheque = get_salario_contra_cheque(
                contra_cheque_itens
            )
            salarios.append(
                {"Data": itens.DataFinal, "salario": salario_contra_cheque}
            )
    return salarios


def tabela_faltas_aquisitivo(faltas):
    dias = "30d"
    if len(faltas) > 5:
        dias = "24d"
    if len(faltas) > 14:
        dias = "18d"
    if len(faltas) > 23:
        dias = "12d"
    if len(faltas) > 32:
        dias = "0d"
    return dias


def create_data_contra_cheque(request, contexto):
    data = {}
    data = html_card_contra_cheque_colaborador(request, contexto, data)
    data = html_decimo_terceiro(request, contexto, data)
    return JsonResponse(data)


def busca_contra_cheque_aquisitivo(idpessoal, idaquisitivo, descricao):
    colaborador = get_colaborador(idpessoal)
    aquisitivo = get_aquisitivo_id(idaquisitivo)
    faltas = aquisitivo_faltas(colaborador, aquisitivo)
    ano = aquisitivo.DataFinal.year
    mes = aquisitivo.DataFinal.month
    aquisitivo_inicial = datetime.datetime.strftime(
        aquisitivo.DataInicial, "%d/%m/%Y"
    )
    aquisitivo_final = datetime.datetime.strftime(
        aquisitivo.DataFinal, "%d/%m/%Y"
    )
    obs = f"AQUISITIVO: {aquisitivo_inicial} - {aquisitivo_final}"
    try:
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
        update_contra_cheque_obs(contra_cheque, obs, "aquisitivo")
    except ContraCheque.DoesNotExist:  # pylint: disable=no-member
        nova_obs = dict()
        nova_obs["aquisitivo"] = obs
        create_contra_cheque(
            meses[mes - 1], ano, "FERIAS", colaborador, nova_obs
        )
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
    ferias = Ferias.objects.filter(idAquisitivo=aquisitivo)
    for index, feria in enumerate(ferias):
        gozo_inicial = datetime.datetime.strftime(
            feria.DataInicial, "%d/%m/%Y"
        )
        gozo_final = datetime.datetime.strftime(feria.DataFinal, "%d/%m/%Y")
        string_gozo = f"GOZO DE FÉRIAS - {index+1}"
        chave_gozo = f"gozo{index+1}"
        obs = f"{string_gozo}: {gozo_inicial} - {gozo_final}"
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
        update_contra_cheque_obs(contra_cheque, obs, chave_gozo)
    if faltas:
        obs = f"FALTAS: {faltas}"
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
        update_contra_cheque_obs(contra_cheque, obs, "faltas")
    return contra_cheque


def busca_contra_cheque_parcela(idpessoal, idparcela, descricao):
    colaborador = get_colaborador(idpessoal)
    parcela_decimo_terceiro = get_parcelas_decimo_terceiro_id(idparcela)
    ano = parcela_decimo_terceiro.idDecimoTerceiro.Ano
    if parcela_decimo_terceiro.Parcela == 1:
        mes = 11
    else:
        mes = 12
    try:
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
    except ContraCheque.DoesNotExist:  # pylint: disable=no-member
        create_contra_cheque(
            meses[mes - 1], ano, "DECIMO TERCEIRO", colaborador, ""
        )
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, descricao
        )
    return contra_cheque


def busca_contra_cheque_pagamento(idpessoal, mes, ano):
    colaborador = get_colaborador(idpessoal)
    salario = get_salario(colaborador)
    adiantamento = salario / 100 * 40
    try:
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, "PAGAMENTO"
        )
    except ContraCheque.DoesNotExist:  # pylint: disable=no-member
        print(colaborador, " - chequei aqui")
        create_contra_cheque(meses[mes - 1], ano, "PAGAMENTO", colaborador, "")
        contra_cheque = get_contra_cheque_mes_ano_descricao(
            colaborador, mes, ano, "PAGAMENTO"
        )
        create_contra_cheque_itens(
            "SALARIO", salario, "C", "30d", contra_cheque
        )
        create_contra_cheque_itens(
            "ADIANTAMENTO", adiantamento, "D", "40%", contra_cheque
        )
    return contra_cheque


def get_contra_cheque_mes_ano_pagamento(mes, ano):
    contra_cheque = ContraCheque.objects.filter(
        MesReferencia=meses[mes - 1],
        AnoReferencia=ano,
        Descricao="PAGAMENTO",
    )
    return contra_cheque


def get_contra_cheque_mes_ano_adiantamento(mes, ano):
    contra_cheque = ContraCheque.objects.filter(
        MesReferencia=meses[mes - 1],
        AnoReferencia=ano,
        Descricao="ADIANTAMENTO",
    )
    return contra_cheque


def get_contra_cheque_mes_ano_descricao(colaborador, mes, ano, descricao):
    print(colaborador)
    print(mes)
    print(ano)
    print(descricao)
    contra_cheque = ContraCheque.objects.get(
        idPessoal=colaborador,
        MesReferencia=meses[mes - 1],
        AnoReferencia=ano,
        Descricao=descricao,
    )
    return contra_cheque


def create_contra_cheque(mes, ano, descricao, colaborador, obs):
    ContraCheque.objects.create(
        MesReferencia=mes,
        AnoReferencia=ano,
        Valor=0.00,
        Pago=False,
        Descricao=descricao,
        Obs=obs,
        idPessoal=colaborador,
    )


def get_aquisitivo_id(idaquisitivo):
    aquisitivo = Aquisitivo.objects.get(idAquisitivo=idaquisitivo)
    return aquisitivo


def get_parcelas_decimo_terceiro_id(idparcela):
    parcela = ParcelasDecimoTerceiro.objects.get(
        idParcelasDecimoTerceiro=idparcela
    )
    return parcela


def get_contra_cheque_itens(contra_cheque):
    contra_cheque_itens = ContraChequeItens.objects.filter(
        idContraCheque=contra_cheque
    )
    return contra_cheque_itens


def create_contra_cheque_itens(
    descricao, valor, registro, referencia, contra_cheque
):
    ContraChequeItens.objects.create(
        Descricao=descricao,
        Valor=valor,
        Registro=registro,
        Referencia=referencia,
        idContraCheque=contra_cheque,
    )


def create_contra_cheque_itens_vale(idcontracheque, idvale):
    vale = get_vale_id(idvale)
    dia = datetime.datetime.strftime(vale.Data, "%d/%m/%Y")
    ContraChequeItens.objects.create(
        Descricao=f"{vale.Descricao} - {dia}",
        Valor=vale.Valor,
        Registro="D",
        idContraCheque_id=idcontracheque,
        Vales_id=idvale,
    )


def get_vale_id(idvale):
    vale = Vales.objects.get(idVales=idvale)
    return vale


def aquisitivo_faltas(colaborador, aquisitivo):
    inicio = aquisitivo.DataInicial
    final = aquisitivo.DataFinal
    cartao_ponto = CartaoPonto.objects.filter(
        idPessoal=colaborador,
        Dia__range=[inicio, final],
        Ausencia="FALTA",
        Remunerado=False,
    )
    lista = [
        datetime.datetime.strftime(i.Dia, "%d/%m/%Y") for i in cartao_ponto
    ]
    return lista


def aquisitivo_salario_ferias(salario, faltas):
    salario_dia = salario / 30
    faltas = len(faltas)
    if faltas < 6:
        salario_ferias = salario
    elif 5 < faltas < 15:
        salario_ferias = salario_dia * 24
    elif 14 < faltas < 24:
        salario_ferias = salario_dia * 18
    elif 23 < faltas < 33:
        salario_ferias = salario_dia * 12
    else:
        salario_ferias = Decimal(0.00)
    salario_ferias = round(salario_ferias, 2)
    return salario_ferias


def update_contra_cheque_obs(contra_cheque, obs, chave):
    print(obs)
    try:
        dict_obs = ast.literal_eval(contra_cheque.Obs)
    except (SyntaxError, ValueError) as e:
        print(f"[ERROR] {e}")
        dict_obs = {}
    except Exception as e:
        print(f"[ERROR] {e}")
        dict_obs = {}
    print(dict_obs.get(chave))

    if dict_obs.get(chave) != obs:
        print("aqui")
        dict_obs[chave] = obs
        obj = contra_cheque
        obj.Obs = str(dict_obs)
        obj.save()


def update_contra_cheque_item_valor(contra_cheque_item, valor):
    obj = contra_cheque_item[0]
    obj.Valor = valor
    obj.save()


def update_contra_cheque_item_referencia(contra_cheque_item, referencia):
    obj = contra_cheque_item[0]
    obj.Referencia = referencia
    obj.save()


def get_vales_colaborador(colaborador):
    vales = Vales.objects.filter(idPessoal=colaborador).order_by("Data")
    lista = []
    for item in vales:
        checked = False
        if ContraChequeItens.objects.filter(Vales_id=item.idVales):
            checked = True
        lista.append(
            {
                "idvale": item.idVales,
                "data": item.Data,
                "descricao": item.Descricao,
                "valor": item.Valor,
                "checked": checked,
            }
        )
    return lista


def get_saldo_vales_colaborador(vales):
    pagar = [d for d in vales if not d["checked"]]
    total = sum(item["valor"] for item in pagar)
    return total


def get_saldo_contra_cheque(contra_cheque_itens):
    itens_credito = contra_cheque_itens.filter(Registro="C")
    creditos = itens_credito.aggregate(Total=Sum("Valor"))
    itens_debito = contra_cheque_itens.filter(Registro="D")
    debitos = itens_debito.aggregate(Total=Sum("Valor"))
    if creditos["Total"] is None:
        creditos["Total"] = Decimal(0.00)
    if debitos["Total"] is None:
        debitos["Total"] = Decimal(0.00)
    total = creditos["Total"] - debitos["Total"]
    return creditos["Total"], debitos["Total"], total


def contexto_vales_colaborador(colaborador):
    vales = get_vales_colaborador(colaborador)
    saldo_vales = get_saldo_vales_colaborador(vales)
    contexto = {"vales": vales, "saldo_vales": saldo_vales}
    return contexto


def contexto_contra_cheque_id(idcontracheque):
    contra_cheque = get_contra_cheque_id(idcontracheque)
    contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
    contra_cheque_itens = contra_cheque_itens.order_by("idContraChequeItens")
    credito, debito, saldo_contra_cheque = get_saldo_contra_cheque(
        contra_cheque_itens
    )
    contexto = {
        "contra_cheque": contra_cheque,
        "contra_cheque_itens": contra_cheque_itens,
        "credito": credito,
        "debito": debito,
        "saldo_contra_cheque": saldo_contra_cheque,
        "tipo": contra_cheque.Descricao,
    }
    return contexto


def get_contra_cheque_id(idcontracheque):
    contra_cheque = ContraCheque.objects.get(idContraCheque=idcontracheque)
    return contra_cheque


def data_adiciona_vale_contra_cheque(request, contexto):
    data = {}
    data["html_card_contra_cheque_colaborador"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    data["html_vales_colaborador"] = render_to_string(
        "pessoas/card_vales_colaborador.html",
        contexto,
        request=request,
    )
    return JsonResponse(data)


def delete_contra_cheque_itens(idcontrachequeitens):
    contra_cheque_itens = get_contra_cheque_itens_id(idcontrachequeitens)
    contra_cheque_itens.delete()


def get_contra_cheque_itens_id(idcontrachequeitens):
    contra_cheque_item = ContraChequeItens.objects.get(
        idContraChequeItens=idcontrachequeitens
    )
    return contra_cheque_item


def busca_um_terco_ferias(contra_cheque_itens):
    um_terco = contra_cheque_itens.filter(Descricao="1/3 FERIAS")
    if not um_terco:
        return False
    return True


# TODO renomear para get_decimo_terceiro após exclusão da get_decimo_terceiro atual
def get_decimo_terceiro_colaborador(colaborador):
    decimo_terceiro = DecimoTerceiro.objects.filter(idPessoal=colaborador)
    return decimo_terceiro


def verifica_decimo_terceiro(colaborador):
    decimo_terceiro = get_decimo_terceiro_colaborador(colaborador)
    hoje = datetime.today().date()
    ano_inicio = colaborador.DataAdmissao.year
    ano_final = hoje.year
    ano = ano_inicio
    while ano <= ano_final:
        decimo_terceiro_ano = decimo_terceiro.filter(Ano=ano)
        if not decimo_terceiro_ano:
            DecimoTerceiro.objects.create(
                Ano=ano,
                Dozeavos=0,
                ValorBase=0.00,
                Valor=0.00,
                Pago=False,
                idPessoal=colaborador,
            )
        ano = ano + 1


def get_parcelas_decimo_terceiro(colaborador):
    parcelas = ParcelasDecimoTerceiro.objects.filter(
        idDecimoTerceiro__idPessoal=colaborador
    )
    return parcelas


def verifica_parcelas_decimo_terceiro(colaborador):
    decimo_terceiro = get_decimo_terceiro_colaborador(colaborador)
    for itens in decimo_terceiro:
        parcelas = ParcelasDecimoTerceiro.objects.filter(
            idDecimoTerceiro=itens
        )
        if not parcelas:
            ParcelasDecimoTerceiro.objects.create(
                Parcela=1,
                Valor=0,
                Pago=False,
                idDecimoTerceiro=itens,
            )
            ParcelasDecimoTerceiro.objects.create(
                Parcela=2,
                Valor=0,
                Pago=False,
                idDecimoTerceiro=itens,
            )


def get_salario_base_contra_cheque_itens(contra_cheque_itens, tipo):
    if tipo == "PAGAMENTO":
        tipo = "SALARIO"
    contra_cheque_itens = list(contra_cheque_itens.values())
    filtro = next(
        (item for item in contra_cheque_itens if item["Descricao"] == tipo),
        None,
    )
    salario = Decimal(0.00)
    if tipo == "FERIAS":
        salario = round(filtro["Valor"] / int(filtro["Referencia"][:-1]) * 30)
    elif tipo[:15] == "DECIMO TERCEIRO":
        salario = round(
            filtro["Valor"] / int(filtro["Referencia"][:-1]) * 12 * 2
        )
    elif tipo == "ADIANTAMENTO":
        salario = round(filtro["Valor"] / 40 * 100)
    elif tipo == "PAGAMENTO":
        salario = round(filtro["Valor"] / int(filtro["Referencia"][:-1]) * 30)
    return salario


def modal_vale_colaborador(request, idpessoal):
    data = dict()
    if request.method == "POST":
        descricao = request.POST.get("Descricao").upper()
        data_vale = request.POST.get("Data")
        valor = float(request.POST.get("Valor"))
        parcela = int(request.POST.get("Parcela"))
        registro_vales = []
        if parcela == 1:
            registro_vales.append(
                Vales(
                    Descricao=descricao,
                    Data=data_vale,
                    Valor=valor,
                    idPessoal_id=idpessoal,
                )
            )
        else:
            valor_parcela = valor / parcela
            for item in range(parcela):
                registro_vales.append(
                    Vales(
                        Descricao=f"{descricao} P-{item+1}/{parcela}",
                        Data=data_vale,
                        Valor=round(valor_parcela, 2),
                        idPessoal_id=idpessoal,
                    )
                )
        Vales.objects.bulk_create(registro_vales)
        contexto = contexto_vales_colaborador(idpessoal)
        html_vales_colaborador(request, contexto, data)
    else:
        contexto = {"form": FormVale, "idpessoal": idpessoal}
        data["html_modal"] = render_to_string(
            "pessoas/modal_vale_colaborador.html", contexto, request=request
        )
    return JsonResponse(data)


def get_contas_bancaria_colaborador(colaborador):
    contas = ContaPessoal.objects.filter(idPessoal=colaborador)
    contas = list(contas.values())
    return contas


def modal_confirma(request, confirma, idconfirma, idpessoal, mes_ano):
    data = dict()
    if confirma == "confirma_vale":
        vale = get_vale_id(idconfirma)
        contexto = {"vale": vale, "idpessoal": idpessoal}
        data["html_modal"] = render_to_string(
            "pessoas/modal_exclui_vale_colaborador.html",
            contexto,
            request=request,
        )
    elif confirma == "confirma_pagamento_contra_cheque":
        contra_cheque = get_contra_cheque_id(idconfirma)
        contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
        contra_cheque_itens = contra_cheque_itens.order_by(
            "idContraChequeItens"
        )
        credito, debito, saldo_contra_cheque = get_saldo_contra_cheque(
            contra_cheque_itens
        )
        contexto = {
            "contra_cheque": contra_cheque,
            "idpessoal": idpessoal,
            "saldo_contra_cheque": saldo_contra_cheque,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pessoas/modal_pagamento_contra_cheque.html",
            contexto,
            request=request,
        )
    elif confirma == "confirma_exclui_arquivo_contra_cheque":
        contra_cheque = get_contra_cheque_id(idconfirma)
        contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
        contra_cheque_itens = contra_cheque_itens.order_by(
            "idContraChequeItens"
        )

        credito, debito, saldo_contra_cheque = get_saldo_contra_cheque(
            contra_cheque_itens
        )
        contexto = {
            "contra_cheque": contra_cheque,
            "idpessoal": idpessoal,
            "saldo_contra_cheque": saldo_contra_cheque,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pessoas/modal_exclui_arquivo_contra_cheque.html",
            contexto,
            request=request,
        )
    elif confirma == "confirma_estorno_contra_cheque":
        contra_cheque = get_contra_cheque_id(idconfirma)
        contra_cheque_itens = get_contra_cheque_itens(contra_cheque)
        contra_cheque_itens = contra_cheque_itens.order_by(
            "idContraChequeItens"
        )

        credito, debito, saldo_contra_cheque = get_saldo_contra_cheque(
            contra_cheque_itens
        )
        contexto = {
            "contra_cheque": contra_cheque,
            "idpessoal": idpessoal,
            "saldo_contra_cheque": saldo_contra_cheque,
            "mes_ano": mes_ano,
        }
        data["html_modal"] = render_to_string(
            "pessoas/modal_exclui_arquivo_contra_cheque.html",
            contexto,
            request=request,
        )

    return JsonResponse(data)


def exclui_arquivo_contra_cheque_servidor(request, idcontracheque):
    file_descricao = f"CONTRA-CHEQUE_-_{str(idcontracheque).zfill(6)}"
    file = busca_arquivo_descricao(file_descricao)
    if file:
        try:
            os.remove(file.uploadFile.path)
            file.delete()
        except FileNotFoundError:
            print("ARQUIVO NÃO ENCONTRADO")


def get_descricao_contra_cheque_id(idcontracheque):
    contra_cheque = get_contrachequeid(idcontracheque)
    return contra_cheque[0].Descricao


def exclui_vale_colaborador_id(request, idvale, idpessoal):
    vale = get_vale_id(idvale)
    idpessoal = vale.idPessoal
    vale.delete()
    data = dict()
    contexto = contexto_vales_colaborador(idpessoal)
    html_vales_colaborador(request, contexto, data)
    return JsonResponse(data)


def paga_contra_cheque(request, idcontracheque):
    #  contra_cheque = get_contra_cheque_id(idcontracheque)
    valor = request.POST.get("valor")
    valor = valor.replace(".", "_").replace(",", ".").replace("_", ",")
    valor = Decimal(valor)
    registro_contra_cheque = []
    registro_contra_cheque.append(
        ContraCheque(
            idContraCheque=idcontracheque,
            Valor=valor,
            Pago=True,
        )
    )
    ContraCheque.objects.bulk_update(registro_contra_cheque, ["Valor", "Pago"])
    data = dict()
    data["pago"] = True
    return JsonResponse(data)


def estorna_contra_cheque(request, idcontracheque):
    registro_contra_cheque = []
    registro_contra_cheque.append(
        ContraCheque(
            idContraCheque=idcontracheque,
            Pago=False,
        )
    )
    ContraCheque.objects.bulk_update(registro_contra_cheque, ["Pago"])
    data = dict()
    data["pago"] = False
    return JsonResponse(data)


def salva_arquivo_contra_cheque(request, idcontracheque):
    message = {"text": None, "type": None}
    if request.method == "POST":
        if request.FILES:
            descricao = f"Contra-Cheque_-_{str(idcontracheque).zfill(6)}"
            ext_file = request.FILES["arquivo"].name.split(".")[-1]
            name_file = f"{descricao}.{ext_file}"
            request.FILES["arquivo"].name = name_file
            obj = FileUpload()
            obj.DescricaoUpload = descricao
            obj.uploadFile = request.FILES["arquivo"]
            try:
                obj.save()
                message["text"] = "Arquivo enviado ao servidor com sucesso"
                message["type"] = "SUCESSO"
            except:
                message["text"] = "Falha ao salvar o arquivo, tente novamente"
                message["type"] = "ERROR"
        else:
            message["text"] = "Arquivo não selecionado"
            message["type"] = "ERROR"
    return message


def colaborador_info(idpessoal):
    colaborador = list(Pessoal.objects.filter(idPessoal=idpessoal).values())
    colaborador[0]["nome_curto"] == nome_curto(colaborador[0].Nome)
    colaborador[0]["nome_curtoi_u"] == nome_curto_underscore(
        colaborador[0].Nome
    )
    colaborador[0]["endereco_completo"] == get_endereco_completo(
        colaborador.Endereco, colaborador.Bairro
    )
    colaborador[0]["cidade_estado"] == get_endereco_completo(
        colaborador.Cidade, colaborador.Estado, colaborador.CEP
    )
    return colaborador


def get_endereco_completo(endereco, bairro):
    endereco_completo = ""
    if endereco:
        endereco_completo = endereco
    if endereco and bairro:
        endereco_completo = endereco_completo + " - " + bairro
    if not endereco and bairro:
        endereco_completo = bairro
    return endereco_completo


def get_cidade_estado(cidade, estado, cep):
    cidade_estado = ""
    if cidade:
        cidade_estado = cidade
    if cidade and estado:
        cidade_estado = cidade_estado + " - " + estado
    if not cidade and estado:
        cidade_estado = estado
    if cep:
        if cidade_estado == "":
            cidade_estado = "CEP: " + cep
        else:
            cidade_estado = cidade_estado + " - CEP: " + cep
    return cidade_estado

    #  @staticmethod
    #  def get_faltas_aquisitivo(self):
    #  if self.tipo_pgto == "MENSALISTA":
    #  inicio = self.aquisitivo[0]["aquisitivo_inicial"]
    #  final = self.aquisitivo[0]["aquisitivo_final"]
    #  cartao_ponto = CartaoPonto.objects.filter(
    #  idPessoal=self.idpes,
    #  Dia__range=[inicio, final],
    #  Ausencia="FALTA",
    #  Remunerado=False,
    #  )
    #  lista = [
    #  datetime.datetime.strftime(i.Dia, "%d/%m/%Y")
    #  for i in cartao_ponto
    #  ]
    #  else:
    #  lista = []
    #  return lista


def create_contexto_contra_cheque_colaborador(idpessoal, mes_ano, descricao):
    mes, ano = converter_mes_ano(mes_ano)
    contra_cheque = get_contra_cheque_mes_ano_descricao(
        idpessoal, int(mes), ano, descricao
    )
    contexto = create_contexto_contra_cheque(
        idpessoal, contra_cheque, descricao
    )
    idcontracheque = contra_cheque.idContraCheque
    file = get_file_contra_cheque(idcontracheque)
    contexto.update({"file": file})
    return contexto


def get_file_contra_cheque(idcontracheque):
    file_descricao = f"CONTRA-CHEQUE_-_{str(idcontracheque).zfill(6)}"
    file = busca_arquivo_descricao(file_descricao)
    return file


def html_contra_cheque(request, contexto, data):
    data["html_contra_cheque"] = render_to_string(
        "pessoas/card_contra_cheque_colaborador.html",
        contexto,
        request=request,
    )
    return data


def html_files_contra_cheque(request, contexto, data):
    data["html_files_contra_cheque"] = render_to_string(
        "pessoas/html_files_contra_cheque.html", contexto, request=request
    )
    return data


def create_data_contra_cheque_colaborador(request, contexto):
    data = dict()
    html_contra_cheque(request, contexto, data)
    if contexto["contra_cheque"].Pago:
        if not contexto["file"]:
            html_files_contra_cheque(request, contexto, data)
    return JsonResponse(data)


def create_contexto_minutas_contra_cheque(idpessoal, contra_cheque):
    mes = meses.index(contra_cheque.MesReferencia) + 1
    ano = contra_cheque.AnoReferencia
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    minutas = facade_pagamentos.union_minutas_agenda_periodo_contra_cheque(
        idpessoal, primeiro_dia_mes, ultimo_dia_mes
    )
    return {"minutas": minutas}


def create_contexto_cartao_ponto_contra_cheque(idpessoal, contra_cheque):
    mes = meses.index(contra_cheque.MesReferencia) + 1
    ano = contra_cheque.AnoReferencia
    primeiro_dia_mes, ultimo_dia_mes = extremos_mes(mes, ano)
    cartao_ponto = facade_pagamentos.get_cartao_ponto_colaborador(
        idpessoal, primeiro_dia_mes, ultimo_dia_mes
    )
    return {"cartao_ponto": cartao_ponto}


def faltas_periodo_aquisitivo():
    pass
