import datetime
from collections import defaultdict

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.formats import date_format

from core.tools import get_mensagem
from despesas import html_data
from despesas.facades import consumo
from despesas.forms import CadastraAbastecimento
from despesas.models import Abastecimento

def obter_mes(valor=None):
    """Converte 'AAAA-MM' no primeiro dia do mês; padrão é o mês atual."""
    try:
        return datetime.datetime.strptime(valor, "%Y-%m").date()
    except (TypeError, ValueError):
        return datetime.date.today().replace(day=1)


def somar_meses(mes, quantidade):
    total = mes.year * 12 + mes.month - 1 + quantidade
    return datetime.date(total // 12, total % 12 + 1, 1)


def get_abastecimentos_mes(mes):
    return Abastecimento.objects.filter(
        DataAbastecimento__gte=mes,
        DataAbastecimento__lt=somar_meses(mes, 1),
    )


def create_contexto_abastecimentos(mes=None):
    """Contexto do card de abastecimentos: lista e totais do mês."""
    mes = mes or obter_mes()
    abastecimentos = (
        get_abastecimentos_mes(mes)
        .select_related("idVeiculo")
        .order_by("-DataAbastecimento", "-idAbastecimento")
    )
    totais = abastecimentos.aggregate(
        litros=Sum("LitrosAbastecidos"), valor=Sum("ValorAbastecido")
    )
    media = None
    if totais["litros"]:
        media = totais["valor"] / totais["litros"]

    proximo = somar_meses(mes, 1)
    return {
        "abastecimentos": abastecimentos,
        "mes_abastecimento": mes,
        "mes_param": mes.strftime("%Y-%m"),
        "mes_anterior": somar_meses(mes, -1).strftime("%Y-%m"),
        "mes_proximo": (
            proximo.strftime("%Y-%m") if proximo <= obter_mes() else None
        ),
        "total_litros": totais["litros"] or 0,
        "total_valor": totais["valor"] or 0,
        "media_litro": media,
    }


def _resumo(litros, valor, quantidade):
    return {
        "litros": litros or 0,
        "valor": valor or 0,
        "quantidade": quantidade,
        "media": valor / litros if litros else None,
    }


def _percentual_do_maior(itens):
    """Adiciona 'percentual' (valor em relação ao maior) para as barras."""
    maior = max((item["valor"] for item in itens), default=0)
    for item in itens:
        item["percentual"] = round(item["valor"] * 100 / maior) if maior else 0
    return itens


def _com_consumo(resumo, km, litros, descartadas=0):
    """Adiciona km rodados e consumo (km/L) ao resumo."""
    resumo["km"] = km
    resumo["descartadas"] = descartadas
    resumo["consumo"], resumo["verificar"] = consumo.calcular_consumo(
        km, litros
    )
    return resumo


def create_contexto_resumo_abastecimento(mes=None, quantidade_meses=12):
    """Contexto do card de resumo: mês a mês e por placa no mês."""
    mes = mes or obter_mes()
    inicio = somar_meses(mes, -(quantidade_meses - 1))
    fim = somar_meses(mes, 1)

    linhas = (
        Abastecimento.objects.filter(
            DataAbastecimento__gte=inicio, DataAbastecimento__lt=fim
        )
        .annotate(mes=TruncMonth("DataAbastecimento"))
        .values("mes", "idVeiculo", "idVeiculo__Placa")
        .annotate(
            litros=Sum("LitrosAbastecidos"),
            valor=Sum("ValorAbastecido"),
            quantidade=Count("idAbastecimento"),
        )
        .order_by()
    )
    km_veiculos = consumo.km_rodados_por_veiculo_mes(inicio, fim)
    sem_km = {"km": 0, "descartadas": 0}

    por_mes = defaultdict(
        lambda: {
            "litros": 0,
            "valor": 0,
            "quantidade": 0,
            "km": 0,
            "litros_com_km": 0,
        }
    )
    placas = []
    for linha in linhas:
        km = km_veiculos.get((linha["idVeiculo"], linha["mes"]), sem_km)
        total = por_mes[linha["mes"]]
        for campo in ("litros", "valor", "quantidade"):
            total[campo] += linha[campo]
        # Veículo sem minuta no mês não entra no consumo da frota
        if km["km"]:
            total["km"] += km["km"]
            total["litros_com_km"] += linha["litros"]
        if linha["mes"] == mes:
            resumo = _resumo(
                linha["litros"], linha["valor"], linha["quantidade"]
            )
            resumo["placa"] = linha["idVeiculo__Placa"]
            placas.append(
                _com_consumo(
                    resumo, km["km"], linha["litros"], km["descartadas"]
                )
            )
    placas.sort(key=lambda item: item["valor"], reverse=True)

    meses = []
    for indice in range(quantidade_meses):
        data_mes = somar_meses(mes, -indice)
        total = por_mes.get(data_mes, {})
        resumo = _resumo(
            total.get("litros"), total.get("valor"), total.get("quantidade", 0)
        )
        resumo.update(mes=data_mes, param=data_mes.strftime("%Y-%m"))
        meses.append(
            _com_consumo(
                resumo, total.get("km", 0), total.get("litros_com_km", 0)
            )
        )

    contexto = {
        "mes_abastecimento": mes,
        "resumo_meses": _percentual_do_maior(meses),
        "resumo_placas": _percentual_do_maior(placas),
    }
    contexto.update(create_contexto_graficos_abastecimento(meses, mes))
    return contexto


def create_contexto_graficos_abastecimento(resumo_meses, mes):
    """Séries dos gráficos em ordem cronológica, para o json_script."""
    pontos = []
    for item in reversed(resumo_meses):
        pontos.append(
            {
                "rotulo": date_format(item["mes"], "M/y"),
                "mes": item["param"],
                "valor": float(item["valor"]),
                "media": float(item["media"]) if item["media"] else None,
                "consumo": (
                    round(item["consumo"], 2)
                    if item["consumo"] and not item["verificar"]
                    else None
                ),
                "ativo": item["mes"] == mes,
            }
        )
    return {"graficos_abastecimento": pontos}


def get_abastecimento_or_none(id_abastecimento):
    if not id_abastecimento:
        return None
    return get_object_or_404(Abastecimento, pk=id_abastecimento)


def modal_abastecimento(request, id_abastecimento=None, form=None):
    """Prepara o formulário de abastecimento para exibição no modal."""
    abastecimento = get_abastecimento_or_none(id_abastecimento)
    if form is None:
        form = CadastraAbastecimento(instance=abastecimento)

    contexto = {"form": form, "abastecimento": abastecimento}
    return html_data.html_modal_abastecimento(request, contexto)


def save_abastecimento(request):
    """Valida e salva o abastecimento enviado pelo formulário.

    Retorna a resposta JSON: com o formulário e os erros quando inválido,
    ou com o card atualizado e a mensagem quando salvo.
    """
    id_abastecimento = request.POST.get("id_abastecimento")
    abastecimento = get_abastecimento_or_none(id_abastecimento)
    form = CadastraAbastecimento(request.POST, instance=abastecimento)

    if not form.is_valid():
        modal_html = modal_abastecimento(request, id_abastecimento, form)
        return JsonResponse({"html_form": modal_html})

    abastecimento = form.save()
    codigo = "deab0002" if id_abastecimento else "deab0001"
    # Mostra o mês do abastecimento salvo
    mes = abastecimento.DataAbastecimento.replace(day=1)
    return create_data_card_abastecimento(request, mes, get_mensagem(codigo))


def delete_abastecimento(request):
    id_abastecimento = request.POST.get("id_abastecimento")
    abastecimento = get_object_or_404(Abastecimento, pk=id_abastecimento)
    mes = abastecimento.DataAbastecimento.replace(day=1)
    abastecimento.delete()
    return create_data_card_abastecimento(
        request, mes, get_mensagem("deab0003")
    )


def create_data_card_abastecimento(request, mes, mensagem=None):
    contexto = create_contexto_abastecimentos(mes)
    contexto.update(create_contexto_resumo_abastecimento(mes))
    data = html_data.html_card_abastecimento(request, contexto, {})
    data = html_data.html_card_resumo_abastecimento(request, contexto, data)
    data = html_data.html_card_graficos_abastecimento(request, contexto, data)
    if mensagem:
        data.update(mensagem)
    return JsonResponse(data)
