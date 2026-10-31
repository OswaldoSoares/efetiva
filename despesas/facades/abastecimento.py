import datetime

from django.db.models import Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core.tools import get_mensagem
from despesas import html_data
from despesas.forms import CadastraAbastecimento
from despesas.models import Abastecimento

# Quantidade de dias exibidos no card de abastecimentos
DIAS_LISTAGEM = 30


def get_abastecimentos(dias=DIAS_LISTAGEM):
    """Retorna os abastecimentos dos últimos `dias` dias."""
    inicio = datetime.date.today() - datetime.timedelta(days=dias)
    return (
        Abastecimento.objects.filter(DataAbastecimento__gte=inicio)
        .select_related("idVeiculo")
        .order_by("-DataAbastecimento", "-idAbastecimento")
    )


def create_contexto_abastecimentos():
    """Contexto do card de abastecimentos: lista e totais do período."""
    abastecimentos = get_abastecimentos()
    totais = abastecimentos.aggregate(
        litros=Sum("LitrosAbastecidos"), valor=Sum("ValorAbastecido")
    )
    media = None
    if totais["litros"]:
        media = totais["valor"] / totais["litros"]

    return {
        "abastecimentos": abastecimentos,
        "dias_abastecimento": DIAS_LISTAGEM,
        "total_litros": totais["litros"] or 0,
        "total_valor": totais["valor"] or 0,
        "media_litro": media,
    }


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

    form.save()
    codigo = "deab0002" if id_abastecimento else "deab0001"
    return create_data_card_abastecimento(request, get_mensagem(codigo))


def delete_abastecimento(request):
    id_abastecimento = request.POST.get("id_abastecimento")
    abastecimento = get_object_or_404(Abastecimento, pk=id_abastecimento)
    abastecimento.delete()
    return create_data_card_abastecimento(request, get_mensagem("deab0003"))


def create_data_card_abastecimento(request, mensagem):
    contexto = create_contexto_abastecimentos()
    data = html_data.html_card_abastecimento(request, contexto, {})
    data.update(mensagem)
    return JsonResponse(data)
