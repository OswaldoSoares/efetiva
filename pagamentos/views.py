"""
    Módulo Pagamentos:
    Gerencia o pagamento dos colaboradores mensalista e avulsos.
"""
from django.shortcuts import render
from rolepermissions.decorators import has_permission_decorator
from website.facade import str_hoje

from pagamentos import facade
from pessoas import facade as facade_pessoas

from .print import (
    print_contracheque,
    print_recibo,
    print_relatorio_saldo_avulso,
)


@has_permission_decorator("modulo_pagamentos")
def index_pagamento(request):
    contexto = facade.create_contexto_meses_pagamento()
    contexto.update(facade.create_context_avulso())
    return render(request, "pagamentos/index.html", contexto)


def selecionar_mes_pagamento(request):
    _mes_ano = request.GET.get("mes_ano")
    contexto = facade.create_contexto_folha_pagamento(_mes_ano)
    data = facade.create_data_seleciona_mes_ano(request, contexto)
    return data


def selecionar_contra_cheque_pagamento(request):
    contexto = facade_pessoas.create_contexto_contra_cheque_pagamento(request)
    return facade_pessoas.contra_cheque_html_data(request, contexto)


def adiciona_agenda(request):
    _descricao = request.POST.get("descricao")
    _data = request.POST.get("data")
    _id_pes = request.POST.get("idPessoal")
    if request.POST.get("idAgenda"):
        _id_age = request.POST.get("idAgenda")
        facade.update_agenda(_descricao, _data, _id_age)
    else:
        facade.create_agenda(_descricao, _data, _id_pes)
    _mes_ano = request.POST.get("mes_ano")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_gera_agenda(request, contexto)
    return data


def adiciona_contra_cheque_itens(request):
    _descricao = request.POST.get("descricao")
    _valor = request.POST.get("valor")
    _registro = request.POST.get("registro")
    _idcontracheque = request.POST.get("idContraCheque")
    facade.create_contracheque_itens(
        _descricao, _valor, "", _registro, _idcontracheque
    )
    _mes_ano = request.POST.get("mes_ano")
    _id_pes = request.POST.get("idPessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_cci(request, contexto)
    return data


def adiciona_vales(request):
    _descricao = request.POST.get("descricao")
    _data = request.POST.get("data")
    _valor = request.POST.get("valor")
    if request.POST.get("parcelas") == "":
        _parcelas = 1
    else:
        _parcelas = request.POST.get("parcelas")
    _id_pes = request.POST.get("idPessoal")
    data = facade.create_vales(_descricao, _data, _valor, _parcelas, _id_pes)
    _mes_ano = request.POST.get("mes_ano")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_vale(request, contexto)
    return data


def altera_horario_cartao_ponto(request):
    if request.method == "POST":
        mes_ano = request.POST.get("mes_ano")
        idpessoal = request.POST.get("idPessoal")
        data = facade.modal_horario_cartao_ponto(request)
        contexto = facade.create_contexto_mensalista(idpessoal, mes_ano)
        contexto.update(facade.create_contexto_folha_pagamento(mes_ano))
        data = facade.create_data_altera_cartao_ponto(request, contexto)
    else:
        data = facade.modal_horario_cartao_ponto(request)
    return data


def atestada(request):
    mes_ano = request.GET.get("mes_ano")
    idpessoal = request.GET.get("idpessoal")
    idcartaoponto = request.GET.get("idcartaoponto")
    remunerado = request.GET.get("remunerado")
    facade.falta_remunerada(idcartaoponto, remunerado)
    contexto = facade.create_contexto_mensalista(idpessoal, mes_ano)
    contexto.update(facade.create_contexto_folha_pagamento(mes_ano))
    data = facade.create_data_altera_cartao_ponto(request, contexto)
    return data


def ausencia_falta(request):
    mes_ano = request.GET.get("mes_ano")
    idpessoal = request.GET.get("idpessoal")
    idcartaoponto = request.GET.get("idcartaoponto")
    ausencia = request.GET.get("ausencia")
    facade.altera_ausencia_falta(idcartaoponto, ausencia)
    contexto = facade.create_contexto_mensalista(idpessoal, mes_ano)
    contexto.update(facade.create_contexto_folha_pagamento(mes_ano))
    data = facade.create_data_altera_cartao_ponto(request, contexto)
    return data


def carrega_agenda(request):
    _id_age = request.GET.get("idagenda")
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    data = facade.read_agenda(request, _id_age, _id_pes, _mes_ano)
    return data


def carro_empresa(request):
    mes_ano = request.GET.get("mes_ano")
    idpessoal = request.GET.get("idpessoal")
    idcartaoponto = request.GET.get("idcartaoponto")
    carro_empresa = request.GET.get("carro_empresa")
    facade.altera_carro_empresa(idcartaoponto, carro_empresa)
    contexto = facade.create_contexto_mensalista(idpessoal, mes_ano)
    contexto.update(facade.create_contexto_folha_pagamento(mes_ano))
    data = facade.create_data_altera_cartao_ponto(request, contexto)
    return data


def delete_file(request):
    _id_fu = request.GET.get("idfileupload")
    facade.exclui_arquivo(_id_fu)
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_delete_file(request, contexto)
    return data


def exclui_agenda(request):
    _id_age = request.GET.get("idagenda")
    facade.delete_agenda(_id_age)
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_delete_agenda(request, contexto)
    return data


def gera_pagamento_avulso(request):
    c_idpessoal = request.GET.get("idPessoal")
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    c_zerado = int(request.GET.get("Zerado"))
    data = facade.create_pagamento_avulso(
        c_datainicial, c_datafinal, c_idpessoal, c_zerado
    )
    return data


def print_contra_cheque_adiantamento(request):
    _id_cc = request.GET.get("idcc")
    contexto = facade.imprime_contra_cheque_pagamento(_id_cc, "adian")
    response = print_contracheque(contexto, "ADIANTAMENTO")
    return response


def print_contra_cheque_pagamento(request):
    _id_cc = request.GET.get("idcc")
    contexto = facade.imprime_contra_cheque_pagamento(_id_cc, "paga")
    response = print_contracheque(contexto, "CONTRACHEQUE")
    return response


def print_contra_cheque_transporte(request):
    _id_cc = request.GET.get("idcc")
    contexto = facade.imprime_contra_cheque_pagamento(_id_cc, "transp")
    response = print_contracheque(contexto, "VALE TRANSPORTE")
    return response


def imprime_relatorio_saldo_avulso(request):
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    contexto = facade.create_contexto_imprime_relatorio_saldo_avulso(
        c_datainicial, c_datafinal
    )
    response = print_relatorio_saldo_avulso(contexto)
    return response


def remove_contra_cheque_itens(request):
    _id_cci = request.GET.get("idcontrachequeitens")
    facade.delete_contra_cheque_itens(_id_cci)
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_cci(request, contexto)
    return data


def remove_vales(request):
    _id_val = request.GET.get("idvales")
    facade.delete_vales(_id_val)
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_remove_vale(request, contexto)
    return data


def salva_file(request):
    _mes_ano = request.POST.get("mes_ano")
    _id_pes = request.POST.get("idpessoal")
    _nome_curto = request.POST.get("nome_curto")
    _tipo = request.POST["tipo_comprovante"]
    if request.FILES:
        _arquivo = request.FILES["arquivo"]
        _descricao = facade.nome_arquivo(_nome_curto, _mes_ano, _tipo)
        facade.salva_arquivo(_arquivo, _descricao)
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_save_file(request, contexto)
    return data


def seleciona_colaborador_avulso(request):
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    c_idpesssoal = request.GET.get("idPessoal")
    data = facade.seleciona_minutasavulso(
        c_datainicial, c_datafinal, c_idpesssoal
    )
    return data


def seleciona_funcionario(request):
    idpessoal = request.GET.get("idpessoal")
    mes_ano = request.GET.get("mes_ano")
    contexto = facade.create_contexto_mensalista(idpessoal, mes_ano)
    data = facade.create_data_seleciona_funcionario(request, contexto)
    return data


def seleciona_periodo_avulso(request):
    c_datainicial = request.GET.get("DataInicial")
    c_datafinal = request.GET.get("DataFinal")
    data = facade.seleciona_saldoavulso(c_datainicial, c_datafinal)
    return data


def seleciona_vales(request):
    _id_val = request.GET.get("idvales")
    _id_cc = request.GET.get("idcontracheque")
    facade.insere_vale_contra_cheque(_id_val, _id_cc)
    _mes_ano = request.GET.get("mes_ano")
    _id_pes = request.GET.get("idpessoal")
    contexto = facade.create_contexto_funcionario(_mes_ano, _id_pes)
    contexto.update(facade.create_contexto_folha(_mes_ano))
    data = facade.create_data_seleciona_vale(request, contexto)
    return data


def exclui_recibo(request):
    print(f"[INFO] Request GET - {request.GET}")
    idrecibo = request.GET.get("idrecibo")
    idpessoal = request.GET.get("idpessoal")
    data_inicial = request.GET.get("data_inicial")
    data_final = request.GET.get("data_final")
    facade.exclui_recibo(idrecibo)
    contexto = {
        "idrecibo": idrecibo,
        "idpessoal": idpessoal,
        "data_inicial": data_inicial,
        "data_final": data_final,
    }
    data = facade.seleciona_saldoavulso(data_inicial, data_final)
    return data


def imprime_recibo(request):
    c_idrecibo = request.GET.get("idrecibo")
    contexto = facade.print_recibo(c_idrecibo)
    response = print_recibo(contexto)
    return response


def form_paga_recibo(request):
    idrecibo = request.GET.get("idrecibo")

    idpessoal = request.GET.get("idpessoal")
    recibo = request.GET.get("recibo")
    valor_recibo = (
        request.GET.get("valor_recibo").replace(".", "").replace(",", ".")
    )
    hoje = str_hoje()
    contexto = {
        "idrecibo": idrecibo,
        "idpessoal": idpessoal,
        "recibo": recibo,
        "valor_recibo": valor_recibo,
        "hoje": hoje,
    }
    data = facade.create_data_form_paga_recibo_colaborador(request, contexto)
    return data


def paga_recibo(request):
    print(f"[INFO] - Request POST - {request.POST}")
    idrecibo = int(request.POST.get("idrecibo"))
    print(f"[INFO] - Type idrecibo - {type(idrecibo)}")
    data_pgto = request.POST.get("data_pgto")
    facade.paga_recibo_colabotador(idrecibo, data_pgto)
    data = []
    return data


def seleciona_contra_cheque(request):
    idpessoal = request.GET.get("idpessoal")
    mes_ano = request.GET.get("mes_ano")
    descricao = request.GET.get("descricao")
    contexto = facade.create_contexto_contra_cheque(
        idpessoal, mes_ano, descricao
    )
    data = facade.create_data_contra_cheque_colaborador(request, contexto)
    return data


def adiciona_agenda_colaborador(request):
    if request.method == "POST":
        idpessoal = int(request.POST.get("idpessoal"))
        mes_ano = request.POST.get("mes_ano")
    else:
        idpessoal = int(request.GET.get("idpessoal"))
        mes_ano = request.GET.get("mes_ano")
    data = facade.modal_agenda_colaborador(request, idpessoal, mes_ano)
    return data


def edita_agenda_colaborador(request):
    if request.method == "POST":
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        idagenda = request.POST.get("idagenda")
        facade.update_agenda_colaborador(request, idagenda, idpessoal)
        contexto = facade.contexto_agenda_colaborador(idpessoal, mes_ano)
        data = facade.create_data_agenda_colaborador(request, contexto)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data


def exclui_agenda_colaborador(request):
    if request.method == "POST":
        idagenda = request.POST.get("idagenda")
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        facade.exclui_agenda_colaborador_id(
            request, idagenda, idpessoal, mes_ano
        )
        contexto = facade.contexto_agenda_colaborador(idpessoal, mes_ano)
        data = facade.create_data_agenda_colaborador(request, contexto)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data


def arquiva_agenda(request):
    idagenda = request.POST.get("idagenda")
    idpessoal = request.POST.get("idpessoal")
    mes_ano = request.POST.get("mes_ano")
    message = facade.salva_arquivo_agenda(request, idagenda)
    contexto = facade.contexto_agenda_colaborador(idpessoal, mes_ano)
    contexto.update({"message": message})
    data = facade.create_data_agenda_colaborador(request, contexto)
    return data


def exclui_arquivo_agenda(request):
    if request.method == "POST":
        idagenda = request.POST.get("idagenda")
        idpessoal = request.POST.get("idpessoal")
        mes_ano = request.POST.get("mes_ano")
        facade.exclui_arquivo_agenda_servidor(request, idagenda)
        contexto = facade.contexto_agenda_colaborador(idpessoal, mes_ano)
        data = facade.create_data_agenda_colaborador(request, contexto)
    else:
        confirma = request.GET.get("confirma")
        idconfirma = request.GET.get("idconfirma")
        idpessoal = request.GET.get("idpessoal")
        mes_ano = request.GET.get("mes_ano")
        data = facade.modal_confirma(
            request, confirma, idconfirma, idpessoal, mes_ano
        )
    return data
