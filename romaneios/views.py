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
    error, msg = facade.valida_notas_cliente(request)
    nota_form = facade.read_nota_post(request)
    id_not = request.POST.get("idnota")
    if not error:
        if id_not:
            facade.update_notas_cliente(nota_form, id_not)
        else:
            # facade.save_notas_cliente(nota_form)
            print("oi")
        nota_form = dict()
    id_cli = request.POST.get("cliente")
    notas = facade.create_contexto_seleciona_notas(id_cli, "NumeroNota")
    cliente = facade.create_contexto_cliente(id_cli)
    hoje = facade.hoje
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": id_cli}
    contexto.update({"nota_form": nota_form, "error": error})
    contexto.update(msg)
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data


def edita_nota_cliente(request):
    _id_not = request.GET.get("idNota")
    _id_cli = request.GET.get("idCliente")
    cliente = facade.create_contexto_cliente(_id_cli)
    error, msg = False, dict()
    nota_form = facade.read_nota_database(_id_not)
    contexto = {
        "nota_form": nota_form,
        "cliente": cliente,
        "error": error,
        "idcliente": _id_cli,
    }
    contexto.update(msg)
    data = facade.create_data_edita_nota(request, contexto)
    return data
