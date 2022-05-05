from django.db.models import DecimalField, ExpressionWrapper, F
from django.http import JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from minutas.models import MinutaColaboradores, MinutaItens
from rolepermissions.decorators import has_permission_decorator

from pagamentos import facade

from .forms import CadastraCartaoPonto
from .print import print_contracheque, print_recibo


@has_permission_decorator("modulo_pagamentos")
def index_pagamento(request):
    contexto = facade.create_context_formcontracheque()
    contextovales = facade.cria_contexto_pagamentos()
    contexto.update(contextovales)
    contextoavulso = facade.create_context_avulso()
    contexto.update(contextoavulso)
    return render(request, "pagamentos/index.html", contexto)


def cria_folha(request):
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    facade.create_folha(c_mes, c_ano)
    data = facade.seleciona_folha(c_mes, c_ano)
    return data


def seleciona_folha(request):
    c_mes = request.POST.get("MesReferencia")
    c_ano = request.POST.get("AnoReferencia")
    data = facade.seleciona_folha(c_mes, c_ano)
    return data


def seleciona_contracheque(request):
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    c_idpesssoal = request.GET.get("idPessoal")
    facade.atualiza_cartaoponto(c_mes, c_ano, c_idpesssoal)
    facade.calcula_conducao(c_mes, c_ano, c_idpesssoal)
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpesssoal, request)
    return data


def cria_contrachequeitens(request):
    c_descricao = request.POST.get("Descricao")
    c_valor = request.POST.get("Valor")
    c_registro = request.POST.get("Registro")
    c_idcontracheque = request.POST.get("idContraCheque")
    facade.create_contracheque_itens(
        c_descricao, c_valor, "", c_registro, c_idcontracheque
    )
    c_mes = request.POST.get("MesReferencia")
    c_ano = request.POST.get("AnoReferencia")
    c_idpesssoal = request.POST.get("idPessoal")
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpesssoal, request)
    return data


def exclui_contrachequeitens(request):
    c_idcontracheque = request.GET.get("idContraCheque")
    c_descricao = request.GET.get("Descricao")
    c_registro = request.GET.get("Registro")
    facade.delete_contrachequeitens(c_idcontracheque, c_descricao, c_registro)
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    c_idpesssoal = request.GET.get("idPessoal")
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpesssoal, request)
    return data


def imprime_contracheque(request):
    c_idcontracheque = request.GET.get("idcc")
    c_mes = request.GET.get("mes")
    c_ano = request.GET.get("ano")
    c_idpesssoal = request.GET.get("idco")
    c_adiantamento = request.GET.get("adianta")
    c_valetransporte = request.GET.get("vale")
    response = ""
    if c_adiantamento == "False" and c_valetransporte == "False":
        contexto = facade.print_contracheque_context(
            c_idcontracheque, c_mes, c_ano, c_idpesssoal
        )
        response = print_contracheque(contexto, "CONTRACHEQUE")
    else:
        if c_adiantamento == "True":
            contexto = facade.print_contracheque_adiantamento_context(
                c_idcontracheque, c_mes, c_ano, c_idpesssoal
            )
            response = print_contracheque(contexto, "ADIANTAMENTO")
        if c_valetransporte == "True":
            contexto = facade.print_contracheque_valetransporte_context(
                c_idcontracheque, c_mes, c_ano, c_idpesssoal
            )
            response = print_contracheque(contexto, "VALE TRANSPORTE")
    return response


def cria_pagamento(request):
    c_idpessoal = request.GET.get("idPessoal")
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    c_vales = request.GET.getlist("ValesSelecionados[]")
    data = facade.create_pagamento_avulso(
        c_datainicial, c_datafinal, c_idpessoal, c_vales
    )
    return data


def cria_contrachequeitensvale(request):
    c_idpessoal = request.GET.get("idPessoal")
    c_idvales = request.GET.get("idVales")
    c_idcontracheque = request.GET.get("idContraCheque")
    facade.create_contracheque_itens_vales(c_idpessoal, c_idvales, c_idcontracheque)
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    c_idpesssoal = request.GET.get("idPessoal")
    c_switch = request.GET.get("EstadoSwitchMini")
    facade.estado_swith_vales[c_idpesssoal] = c_switch[0:-1].split("-")
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpesssoal, request)
    return data


def exclui_contrachequeitensvale(request):
    c_idvale = request.GET.get("idVales")
    facade.delete_contracheque_itens_vale(c_idvale)
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    c_idpesssoal = request.GET.get("idPessoal")
    c_switch = request.GET.get("EstadoSwitchMini")
    facade.estado_swith_vales[c_idpesssoal] = c_switch[0:-1].split("-")
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpesssoal, request)
    return data


def seleciona_periodo(request):
    c_datainicial = request.POST.get("DataInicial")
    c_datafinal = request.POST.get("DataFinal")
    data = facade.seleciona_saldoavulso(c_datainicial, c_datafinal)
    return data


def seleciona_saldoavulso(request):
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    c_idpesssoal = request.GET.get("idPessoal")
    data = facade.seleciona_minutasavulso(c_datainicial, c_datafinal, c_idpesssoal)
    return data


def inserefalta(request):
    c_mes = request.GET.get("MesReferencia")
    c_ano = request.GET.get("AnoReferencia")
    c_idpesssoal = request.GET.get("idPessoal")
    c_idcartaoponto = request.GET.get("idCartaoPonto")
    data = facade.altera_falta(c_mes, c_ano, c_idpesssoal, c_idcartaoponto, request)
    return data


def manutencao(request):
    contracheque = facade.ContraCheque.objects.all()
    contrachequeitens = facade.ContraChequeItens.objects.all()
    cartaoponto = facade.CartaoPonto.objects.all()
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "cartaoponto": cartaoponto,
    }
    return render(request, "pagamentos/manutencao.html", contexto)


def apagar_tudo(request):
    contracheque = facade.ContraCheque.objects.all()
    contrachequeitens = facade.ContraChequeItens.objects.all()
    cartaoponto = facade.CartaoPonto.objects.all()
    contracheque.delete()
    cartaoponto.delete()
    contexto = {
        "contracheque": contracheque,
        "contrachequeitens": contrachequeitens,
        "cartaoponto": cartaoponto,
    }
    return render(request, "pagamentos/manutencao.html", contexto)


def edita_cartaoponto(request, idcartaoponto):
    c_form = CadastraCartaoPonto
    c_idobj = idcartaoponto
    c_url = "/pagamentos/editacartaoponto/{}/".format(c_idobj)
    c_view = "edita_cartaoponto"
    c_idcartaoponto = request.GET.get("idcartaoponto")
    c_mes = request.POST.get("MesReferencia")
    c_ano = request.POST.get("AnoReferencia")
    c_idpessoal = request.POST.get("idPessoal")
    data = facade.form_pagamento(
        request,
        c_form,
        c_idobj,
        c_url,
        c_view,
        c_idcartaoponto,
        c_mes,
        c_ano,
        c_idpessoal,
    )
    return data


def cria_vale(request):
    c_data = request.POST.get("Data")
    c_descricao = request.POST.get("Descricao")
    c_valor = request.POST.get("Valor")
    c_parcelas = request.POST.get("Parcelas")
    c_idpessoal = request.POST.get("idPessoal")
    if request.method == "POST":
        facade.cria_vale(c_data, c_descricao, c_valor, c_parcelas, c_idpessoal)
    data = facade.seleciona_vales(c_idpessoal)
    return data


def exclui_vale(request):
    c_idvales = request.GET.get("idVales")
    c_mes = request.POST.get("MesReferencia")
    c_ano = request.POST.get("AnoReferencia")
    c_idpessoal = request.POST.get("idPessoal")
    facade.exclui_vale(c_idvales)
    data = facade.seleciona_contracheque(c_mes, c_ano, c_idpessoal, request)
    return data


def exclui_recibo(request):
    c_idrecibo = request.GET.get("idRecibo")
    c_idpessoal = request.GET.get("idPessoal")
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    # c_vales = request.GET.getlist('ValesSelecionados[]')
    data = facade.exclui_recibo(c_idrecibo, c_datainicial, c_datafinal, c_idpessoal)
    return data


def imprime_recibo(request):
    c_idrecibo = request.GET.get("idrecibo")
    contexto = facade.print_recibo(c_idrecibo)
    response = print_recibo(contexto)
    return response


def seleciona_mes_ano(request):
    v_mes_ano = request.GET.get("mes_ano")
    data = facade.html_folha_pagamento(v_mes_ano)
    return data


def seleciona_funcionario(request):
    v_mes = request.GET.get("mes")
    v_ano = request.GET.get("ano")
    v_idpessoal = request.GET.get("idpessoal")
    v_admissao = request.GET.get("admissao")
    v_demissao = request.GET.get("demissao")
    v_salario_base = request.GET.get("salario_base")
    data = facade.html_cartao_ponto(
        v_mes, v_ano, v_idpessoal, v_admissao, v_demissao, v_salario_base
    )
    return data


def ausencia_falta(request):
    v_idcartaoponto = request.GET.get("idcartaoponto")
    v_mes_ano = request.GET.get("mes_ano")
    v_admissao = request.GET.get("admissao")
    v_demissao = request.GET.get("demissao")
    v_salario_base = request.GET.get("salario_base")
    data = facade.altera_ausencia_falta(
        v_idcartaoponto, v_mes_ano, v_admissao, v_demissao, v_salario_base
    )
    return data


def altera_horario_cartao_ponto(request):
    v_mes_ano = request.GET.get("mes_ano")
    v_idcartaoponto = request.GET.get("idcartaoponto")
    v_admissao = request.GET.get("admissao")
    v_demissao = request.GET.get("demissao")
    v_idpessoal = None
    v_salario_base = request.GET.get("salario_base")
    if request.method == "POST":
        v_mes_ano = request.POST.get("mes_ano")
        v_idcartaoponto = request.POST.get("idcartaoponto")
        v_admissao = request.POST.get("admissao")
        v_demissao = request.POST.get("demissao")
        v_idpessoal = request.POST.get("idPessoal")
        v_salario_base = request.POST.get("salario_base")
    data = facade.form_modal_horario(
        request,
        v_idcartaoponto,
        v_mes_ano,
        v_admissao,
        v_demissao,
        v_idpessoal,
        v_salario_base,
    )
    return data


def atestada(request):
    v_idcartaoponto = request.GET.get("idcartaoponto")
    v_mes_ano = request.GET.get("mes_ano")
    v_admissao = request.GET.get("admissao")
    v_demissao = request.GET.get("demissao")
    v_salario_base = request.GET.get("salario_base")
    data = facade.falta_remunerada(
        v_idcartaoponto, v_mes_ano, v_admissao, v_demissao, v_salario_base
    )
    return data
