from datetime import date, timedelta

from clientes.models import Cliente, EMailContatoCliente, Tabela
from django.db.models import Count, Max, Sum
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from minutas.models import Minuta, MinutaColaboradores, MinutaItens
from pessoas.models import Pessoal
from rolepermissions.decorators import has_permission_decorator
from website.models import FileUpload

from faturamentos.facade import (
    FaturaPagas,
    FaturaSelecionada,
    FaturaVencimento,
    delete_arquivo,
    envia_email,
    get_clientes_faturas_pagas,
    get_fatura_pagas,
    html_clientes_paga,
    salva_arquivo,
    salva_pagamento,
)

from .forms import PagaFatura
from .imprime import imprime_fatura_pdf
from .models import Fatura


@has_permission_decorator("modulo_faturamento")
def index_faturamento(request):
    vencimentos = FaturaVencimento().__dict__["dias_vencimentos"]
    pagas = FaturaPagas().__dict__
    recebimentos_dias = pagas["dias_pagos"]
    recebimentos_meses = pagas["meses_pagos"]
    faturas_pagas_cliente = get_clientes_faturas_pagas()
    fatura = (
        Cliente.objects.values("idCliente", "Fantasia")
        .filter(minuta__StatusMinuta="FECHADA", minuta__Valor__gt="0.00")
        .annotate(Valor=Sum("minuta__Valor"), Quantidade=Count("minuta__Minuta"))
        .order_by("Fantasia")
    )
    total_fatura = Minuta.objects.filter(StatusMinuta="FECHADA").aggregate(
        ValorTotal=Sum("Valor"), Quantidade=Count("Minuta")
    )
    faturada = (
        Fatura.objects.filter(StatusFatura="ABERTA")
        .annotate(TotalMinutas=Count("minuta"))
        .exclude(TotalMinutas=0)
        .values(
            "minuta__idCliente__Fantasia",
            "idFatura",
            "Fatura",
            "VencimentoFatura",
            "ValorFatura",
            "TotalMinutas",
        )
        .order_by("VencimentoFatura")
    )
    total_faturada = Fatura.objects.filter(StatusFatura="ABERTA").aggregate(
        ValorTotal=Sum("ValorFatura"), Quantidade=Count("Fatura")
    )
    paga = (
        Cliente.objects.filter(minuta__idFatura__StatusFatura="PAGA")
        .values(
            "minuta__idFatura__Fatura",
            "Fantasia",
            "minuta__idFatura__ValorPagamento",
            "minuta__idFatura__DataPagamento",
            "minuta__idFatura__idFatura",
        )
        .annotate(minutas=Count("minuta__idFatura__Fatura"))
        .order_by("-minuta__idFatura__Fatura")
    )
    return render(
        request,
        "faturamentos/index.html",
        {
            "fatura": fatura,
            "faturada": faturada,
            "total_fatura": total_fatura,
            "total_faturada": total_faturada,
            "paga": paga,
            "vencimentos": vencimentos,
            "recebimentos_dias": recebimentos_dias,
            "recebimentos_meses": recebimentos_meses,
            "faturas_pagas_cliente": faturas_pagas_cliente,
        },
    )


def minutas_faturar_cliente(request, idcli):
    minutas_faturar = Minuta.objects.values("Minuta", "DataMinuta", "Valor").filter(
        idCliente=idcli, StatusMinuta="FECHADA", Valor__gt="0.00"
    )
    minuta = Minuta.objects.filter(idCliente=idcli, StatusMinuta="FECHADA")
    minutaitens = MinutaItens.objects.filter(RecebePaga="R").order_by("-TipoItens")
    ultima_fatura = Fatura.objects.aggregate(UltimaFatura=Max("Fatura"))
    if ultima_fatura["UltimaFatura"] == None:
        ultima_fatura["UltimaFatura"] = 1
    else:
        ultima_fatura["UltimaFatura"] += 1
    tabela = Tabela.objects.get(idCliente=idcli)
    dia_vencimento = (
        date.today() + timedelta(days=tabela.idFormaPagamento.Dias)
    ).strftime("%Y-%m-%d")
    return render(
        request,
        "faturamentos/minutasfaturarcliente.html",
        {
            "minuta": minuta,
            "minutaitens": minutaitens,
            "minutas_faturar": minutas_faturar,
            "ultima_fatura": ultima_fatura,
            "dia_vencimento": dia_vencimento,
        },
    )


def cria_div_selecionada(request):
    data = dict()
    numero_minuta = request.GET.get("minuta")
    minuta = Minuta.objects.get(Minuta=numero_minuta)
    minutaitens = MinutaItens.objects.filter(
        idMinuta_id=minuta.idMinuta, RecebePaga="R"
    ).order_by("-TipoItens")
    motorista = MinutaColaboradores.objects.filter(
        idMinuta_id=minuta.idMinuta, Cargo="MOTORISTA"
    )
    if motorista:
        motorista = Pessoal.objects.get(idPessoal=motorista[0].idPessoal_id)
    context = {"minuta": minuta, "minutaitens": minutaitens, "motorista": motorista}
    data["html_minuta"] = render_to_string(
        "criadivselecionada.html", context, request=request
    )
    return JsonResponse(data)


def cria_fatura(request):
    if request.POST.get("valor-fatura") != "R$ 0,00":
        numero_fatura = request.POST.get("numero-fatura")[10:]
        valor_fatura = request.POST.get("valor-fatura")[3:].replace(",", ".")
        vencimento_fatura = request.POST.get("vencimento-fatura")
        minutas_faturadas = request.POST.getlist("numero-minuta")
        obj = Fatura()
        obj.Fatura = numero_fatura
        obj.DataFatura = date.today()
        obj.ValorFatura = valor_fatura
        obj.VencimentoFatura = vencimento_fatura
        obj.DataPagamento = "2020-01-01"
        obj.StatusFatura = "ABERTA"
        obj.save()
        fatura = Fatura.objects.get(Fatura=numero_fatura)
        for itens in minutas_faturadas:
            minuta = Minuta.objects.get(Minuta=itens)
            if minuta:
                obj = Minuta()
                obj.idMinuta = minuta.idMinuta
                obj.Minuta = minuta.Minuta
                obj.DataMinuta = minuta.DataMinuta
                obj.HoraInicial = minuta.HoraInicial
                obj.HoraFinal = minuta.HoraFinal
                obj.Coleta = minuta.Coleta
                obj.Entrega = minuta.Entrega
                obj.KMInicial = minuta.KMInicial
                obj.KMFinal = minuta.KMFinal
                obj.Obs = minuta.Obs
                obj.StatusMinuta = "FATURADA"
                obj.Valor = minuta.Valor
                obj.Comentarios = minuta.Comentarios
                obj.idFatura_id = fatura.idFatura
                obj.idCliente = minuta.idCliente
                obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
                obj.idVeiculo = minuta.idVeiculo
                obj.save()
        imprime_fatura(request, fatura.idFatura)
    return redirect("index_faturamento")


def estorna_fatura(request, idfatura):
    novo_status = ""
    fatura = Fatura.objects.get(idFatura=idfatura)
    if fatura.StatusFatura == "ABERTA":
        minutas = Minuta.objects.filter(idFatura=fatura.idFatura)
        for itens in minutas:
            minuta = Minuta.objects.get(idMinuta=itens.idMinuta)
            if minuta:
                obj = Minuta()
                obj.idMinuta = minuta.idMinuta
                obj.Minuta = minuta.Minuta
                obj.DataMinuta = minuta.DataMinuta
                obj.HoraInicial = minuta.HoraInicial
                obj.HoraFinal = minuta.HoraFinal
                obj.Coleta = minuta.Coleta
                obj.Entrega = minuta.Entrega
                obj.KMInicial = minuta.KMInicial
                obj.KMFinal = minuta.KMFinal
                obj.Obs = minuta.Obs
                obj.StatusMinuta = "FECHADA"
                obj.Valor = minuta.Valor
                obj.Comentarios = minuta.Comentarios
                obj.idFatura_id = None
                obj.idCliente = minuta.idCliente
                obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
                obj.idVeiculo = minuta.idVeiculo
                obj.save()
        novo_status = "CANCEL"
    if fatura.StatusFatura == "PAGA":
        novo_status = "ABERTA"
    if fatura:
        obj = Fatura(fatura)
        obj.idFatura = fatura.idFatura
        obj.Fatura = fatura.Fatura
        obj.DataFatura = fatura.DataFatura
        obj.ValorFatura = fatura.ValorFatura
        obj.VencimentoFatura = fatura.VencimentoFatura
        obj.DataPagamento = "2020-01-01"
        obj.StatusFatura = novo_status
        obj.save()
    return redirect("index_faturamento")


def paga_fatura(request):
    data = dict()
    v_idobj = request.GET.get("idobj")
    v_datapagto = request.GET.get("datapagto")
    v_valorpago = request.GET.get("valorpago")
    data = salva_pagamento(request, v_idobj, v_datapagto, v_valorpago)
    return data


def imprime_fatura(request, idfatura):
    response = imprime_fatura_pdf(idfatura)[0]
    return response


def email_fatura(request):
    v_idobj = request.GET.get("idobj")
    v_emails = request.GET.get("emails")
    v_texto = request.GET.get("texto")
    data = envia_email(v_idobj, v_emails, v_texto)
    return data


def fatura(request, idfatura):
    msg = {"text_mensagem": None, "type_mensagem": None}
    msg = salva_arquivo(request, msg, idfatura)
    s_fatura = FaturaSelecionada(idfatura).__dict__
    hoje = date.today().strftime("%Y-%m-%d")
    contexto = {
        "s_fatura": s_fatura,
        "msg": msg,
        "hoje": hoje,
    }
    return render(request, "faturamentos/fatura.html", contexto)


def delete_file(request):
    v_idobj = request.GET.get("idobj")
    v_idfatura = request.GET.get("idfatura")
    data = delete_arquivo(request, v_idobj, v_idfatura)
    return data


def cliente_fatura(request):
    v_idobj = request.GET.get("idobj")
    faturas = get_fatura_pagas(v_idobj)
    data = html_clientes_paga(faturas)
    return data
