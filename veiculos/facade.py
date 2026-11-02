from django.db import transaction
from django.db.models import Count, Max
from django.http import JsonResponse
from django.shortcuts import get_object_or_404

from core.tools import get_mensagem, nome_curto
from pessoas.models import FonePessoal
from veiculos import html_data
from veiculos.forms import CadastraCategoria, CadastraVeiculo
from veiculos.models import CategoriaVeiculo, Veiculo

# Nome exibido para os registros de outros módulos que usam o veículo
NOMES_VINCULOS = {
    "abastecimento_set": "abastecimento(s)",
    "minuta_set": "minuta(s)",
    "multas_set": "multa(s)",
    "romaneios_set": "romaneio(s)",
}

# Filtro de situação da lista: valor de Veiculo.Ativo (None = todos)
SITUACOES = {"ativos": True, "inativos": False, "todos": None}
SITUACAO_PADRAO = "ativos"
ROTULOS_SITUACAO = [
    ("ativos", "Ativos"),
    ("inativos", "Inativos"),
    ("todos", "Todos"),
]


def obter_situacao(valor):
    return valor if valor in SITUACOES else SITUACAO_PADRAO


def obter_id(valor):
    try:
        return int(valor)
    except (TypeError, ValueError):
        return None


def obter_filtros(request):
    """Lê os filtros da lista enviados por GET ou POST."""
    dados = request.POST if request.method == "POST" else request.GET
    return (
        obter_situacao(dados.get("situacao")),
        obter_id(dados.get("id_categoria")),
    )


def create_contexto_veiculos(situacao=SITUACAO_PADRAO, id_categoria=None):
    todos = Veiculo.objects.all()
    if id_categoria:
        todos = todos.filter(Categoria_id=id_categoria)

    veiculos = todos.select_related("Categoria", "Proprietario", "Motorista")
    if SITUACOES[situacao] is not None:
        veiculos = veiculos.filter(Ativo=SITUACOES[situacao])

    veiculos = list(veiculos.order_by("Placa"))
    # Na lista vai o nome curto; o completo aparece ao passar o mouse
    for veiculo in veiculos:
        veiculo.proprietario_curto = nome_curto(veiculo.Proprietario.Nome)
        veiculo.motorista_curto = nome_curto(veiculo.Motorista.Nome)

    return {
        "veiculos": veiculos,
        "situacao": situacao,
        "situacoes": ROTULOS_SITUACAO,
        "id_categoria": id_categoria,
        "total_ativos": todos.filter(Ativo=True).count(),
        "total_inativos": todos.filter(Ativo=False).count(),
        "categorias": CategoriaVeiculo.objects.order_by("Categoria"),
    }


def create_contexto_categorias():
    return {
        "categorias_veiculo": CategoriaVeiculo.objects.annotate(
            quantidade=Count("veiculo")
        ).order_by("Categoria"),
    }


def _fones(id_pessoal):
    return FonePessoal.objects.filter(idPessoal_id=id_pessoal)


def create_contexto_veiculo(id_veiculo):
    """Dados do veículo selecionado para o card de detalhes."""
    veiculo = get_object_or_404(
        Veiculo.objects.select_related("Categoria", "Proprietario", "Motorista"),
        pk=id_veiculo,
    )
    cubagem = (
        veiculo.MedidaAltura
        * veiculo.MedidaComprimento
        * veiculo.MedidaLargura
    )
    minutas = veiculo.minuta_set.aggregate(
        quantidade=Count("idMinuta"), ultima=Max("DataMinuta")
    )
    abastecimentos = veiculo.abastecimento_set.aggregate(
        quantidade=Count("idAbastecimento"), ultimo=Max("DataAbastecimento")
    )
    return {
        "veiculo": veiculo,
        "cubagem": cubagem,
        "fones_proprietario": _fones(veiculo.Proprietario_id),
        "fones_motorista": _fones(veiculo.Motorista_id),
        "minutas": minutas,
        "abastecimentos": abastecimentos,
    }


def vinculos_veiculo(veiculo):
    """Registros de outros módulos que usam o veículo, por tipo."""
    vinculos = []
    for relacao in Veiculo._meta.related_objects:
        acessor = relacao.get_accessor_name()
        quantidade = getattr(veiculo, acessor).count()
        if quantidade:
            nome = NOMES_VINCULOS.get(acessor, relacao.related_model._meta.model_name)
            vinculos.append(f"{quantidade} {nome}")
    return vinculos


def create_data_veiculos(
    request, situacao, id_categoria, id_veiculo=None, mensagem=None
):
    """Resposta JSON com a lista e o card do veículo selecionado.

    Sem veículo selecionado, o card de detalhes volta vazio.
    """
    contexto = create_contexto_veiculos(situacao, id_categoria)
    contexto["id_veiculo"] = id_veiculo
    data = html_data.html_card_veiculos(request, contexto, {})
    contexto_veiculo = (
        create_contexto_veiculo(id_veiculo) if id_veiculo else {}
    )
    data = html_data.html_card_veiculo(request, contexto_veiculo, data)
    if mensagem:
        data.update(mensagem)
    return JsonResponse(data)


def create_data_veiculo(request, id_veiculo):
    data = html_data.html_card_veiculo(
        request, create_contexto_veiculo(id_veiculo), {}
    )
    return JsonResponse(data)


def get_veiculo_or_none(id_veiculo):
    if not id_veiculo:
        return None
    return get_object_or_404(Veiculo, pk=id_veiculo)


def modal_veiculo(request, id_veiculo=None, form=None):
    veiculo = get_veiculo_or_none(id_veiculo)
    if form is None:
        form = CadastraVeiculo(instance=veiculo)
    contexto = {"form": form, "veiculo": veiculo}
    return html_data.html_modal_veiculo(request, contexto)


def save_veiculo(request):
    id_veiculo = request.POST.get("id_veiculo")
    veiculo = get_veiculo_or_none(id_veiculo)
    form = CadastraVeiculo(request.POST, instance=veiculo)

    if not form.is_valid():
        modal_html = modal_veiculo(request, id_veiculo, form)
        return JsonResponse({"html_form": modal_html})

    veiculo = form.save()
    codigo = "veic0002" if id_veiculo else "veic0001"
    situacao, id_categoria = obter_filtros(request)
    return create_data_veiculos(
        request,
        situacao,
        id_categoria,
        veiculo.pk,
        get_mensagem(codigo, placa=veiculo.Placa),
    )


def alterar_situacao_veiculo(request):
    veiculo = get_object_or_404(Veiculo, pk=request.POST.get("id_veiculo"))
    veiculo.Ativo = not veiculo.Ativo
    veiculo.save(update_fields=["Ativo"])
    codigo = "veic0004" if veiculo.Ativo else "veic0005"
    situacao, id_categoria = obter_filtros(request)
    return create_data_veiculos(
        request,
        situacao,
        id_categoria,
        veiculo.pk,
        get_mensagem(codigo, placa=veiculo.Placa),
    )


def delete_veiculo(request):
    """Exclui o veículo somente se nenhum outro módulo o utiliza.

    Multas são apagadas em cascata pelo banco, por isso a checagem
    precisa vir antes do delete.
    """
    veiculo = get_object_or_404(Veiculo, pk=request.POST.get("id_veiculo"))
    situacao, id_categoria = obter_filtros(request)
    vinculos = vinculos_veiculo(veiculo)
    if vinculos:
        mensagem = get_mensagem(
            "veic0006", placa=veiculo.Placa, vinculos=", ".join(vinculos)
        )
        return create_data_veiculos(
            request, situacao, id_categoria, veiculo.pk, mensagem
        )

    placa = veiculo.Placa
    veiculo.delete()
    return create_data_veiculos(
        request,
        situacao,
        id_categoria,
        mensagem=get_mensagem("veic0003", placa=placa),
    )


def create_data_categorias(request, mensagem=None):
    """Atualiza o card de categorias e a lista (filtro de categoria)."""
    situacao, id_categoria = obter_filtros(request)
    if not CategoriaVeiculo.objects.filter(pk=id_categoria).exists():
        id_categoria = None
    id_veiculo = obter_id(request.POST.get("id_selecionado"))
    contexto = create_contexto_veiculos(situacao, id_categoria)
    contexto["id_veiculo"] = id_veiculo
    data = html_data.html_card_veiculos(request, contexto, {})
    data = html_data.html_card_categorias(
        request, create_contexto_categorias(), data
    )
    if mensagem:
        data.update(mensagem)
    return JsonResponse(data)


def get_categoria_or_none(id_categoria):
    if not id_categoria:
        return None
    return get_object_or_404(CategoriaVeiculo, pk=id_categoria)


def modal_categoria(request, id_categoria=None, form=None):
    categoria = get_categoria_or_none(id_categoria)
    if form is None:
        form = CadastraCategoria(instance=categoria)
    contexto = {"form": form, "categoria": categoria}
    return html_data.html_modal_categoria(request, contexto)


def save_categoria(request):
    id_categoria = request.POST.get("id_categoria_form")
    categoria = get_categoria_or_none(id_categoria)
    form = CadastraCategoria(request.POST, instance=categoria)

    if not form.is_valid():
        modal_html = modal_categoria(request, id_categoria, form)
        return JsonResponse({"html_form": modal_html})

    categoria = form.save()
    codigo = "veic0008" if id_categoria else "veic0007"
    return create_data_categorias(
        request, get_mensagem(codigo, categoria=categoria.Categoria)
    )


def delete_categoria(request):
    """Exclui a categoria se nenhum veículo, minuta ou orçamento a usa.

    As linhas das tabelas de preço dos clientes para a categoria são
    apagadas junto, como já fazia a tela antiga.
    """
    categoria = get_object_or_404(
        CategoriaVeiculo, pk=request.POST.get("id_categoria_excluir")
    )
    em_uso = {
        "veículo(s)": categoria.veiculo_set.count(),
        "minuta(s)": categoria.minuta_set.count(),
        "orçamento(s)": categoria.orcamento_set.count(),
    }
    vinculos = [f"{qtd} {nome}" for nome, qtd in em_uso.items() if qtd]
    if vinculos:
        return create_data_categorias(
            request,
            get_mensagem(
                "veic0010",
                categoria=categoria.Categoria,
                vinculos=", ".join(vinculos),
            ),
        )

    nome = categoria.Categoria
    with transaction.atomic():
        categoria.tabelaveiculo_set.all().delete()
        categoria.delete()
    return create_data_categorias(
        request, get_mensagem("veic0009", categoria=nome)
    )

