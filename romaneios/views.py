from django.shortcuts import render

from romaneios import facade


def index_romaneio(request):
    clientes = facade.create_contexto_seleciona_cliente()
    contexto = {"clientes": clientes}
    return render(request, "romaneios/index.html", contexto)


def seleciona_cliente(request):
    id_cli = request.POST.get("cliente")
    notas = facade.create_contexto_seleciona_notas(id_cli, "-NumeroNota")
    cliente = facade.create_contexto_cliente(id_cli)
    hoje = facade.hoje
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": id_cli}
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data


def adiciona_nota_cliente(request):
    nota = facade.read_nota_post(request)
    facade.save_notas_cliente(nota)
    id_cli = request.POST.get("cliente")
    notas = facade.create_contexto_seleciona_notas(id_cli, "NumeroNota")
    cliente = facade.create_contexto_cliente(id_cli)
    hoje = facade.hoje
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": id_cli}
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data
