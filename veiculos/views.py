from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse
from django.views.decorators.http import require_GET, require_POST
from rolepermissions.decorators import has_permission_decorator

from veiculos import facade


@has_permission_decorator("modulo_veiculos")
def indexveiculo(request):
    """Lista de veículos, detalhes do selecionado e categorias."""
    situacao, id_categoria = facade.obter_filtros(request)
    contexto = facade.create_contexto_veiculos(situacao, id_categoria)
    contexto.update(facade.create_contexto_categorias())
    id_veiculo = facade.obter_id(request.GET.get("id_veiculo"))
    if id_veiculo:
        contexto.update(facade.create_contexto_veiculo(id_veiculo))
        contexto["id_veiculo"] = id_veiculo
    return render(request, "veiculos/index.html", contexto)


@has_permission_decorator("modulo_veiculos")
@require_GET
def veiculos_lista(request):
    situacao, id_categoria = facade.obter_filtros(request)
    id_veiculo = facade.obter_id(request.GET.get("id_veiculo"))
    return facade.create_data_veiculos(
        request, situacao, id_categoria, id_veiculo
    )


@has_permission_decorator("modulo_veiculos")
@require_GET
def veiculo_consulta(request):
    return facade.create_data_veiculo(request, request.GET.get("id_veiculo"))


@has_permission_decorator("modulo_veiculos")
def veiculo_form(request):
    """GET abre o modal de cadastro/edição; POST salva."""
    if request.method == "POST":
        return facade.save_veiculo(request)
    modal_html = facade.modal_veiculo(request, request.GET.get("id_veiculo"))
    return JsonResponse({"modal_html": modal_html})


@has_permission_decorator("edita_veiculo")
@require_POST
def veiculo_situacao(request):
    return facade.alterar_situacao_veiculo(request)


@has_permission_decorator("exclui_veiculo")
@require_POST
def veiculo_excluir(request):
    return facade.delete_veiculo(request)


@has_permission_decorator("modulo_veiculos")
def categoria_form(request):
    """GET abre o modal da categoria; POST salva."""
    if request.method == "POST":
        return facade.save_categoria(request)
    modal_html = facade.modal_categoria(
        request, request.GET.get("id_categoria_form")
    )
    return JsonResponse({"modal_html": modal_html})


@has_permission_decorator("modulo_veiculos")
@require_POST
def categoria_excluir(request):
    return facade.delete_categoria(request)


def consultaveiculo(request, idvei):
    """Endereço antigo da consulta: abre a tela nova com o veículo."""
    return redirect(f"{reverse('indexveiculo')}?id_veiculo={idvei}")
