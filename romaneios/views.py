from django.shortcuts import render
from minutas.facade import filtra_veiculo, motoristas_disponiveis

from romaneios import facade


def index_romaneio(request):
    clientes = facade.create_contexto_seleciona_cliente()
    romaneios = facade.create_contexto_romaneios()
    contexto = {"clientes": clientes, "romaneios": romaneios}
    return render(request, "romaneios/index.html", contexto)


def seleciona_cliente(request):
    if request.POST:
        id_cli = request.POST.get("cliente")
    else:
        id_cli = request.GET.get("cliente")
    notas = facade.create_contexto_seleciona_notas(id_cli, "-NumeroNota")
    cliente = facade.create_contexto_cliente(id_cli)
    hoje = facade.hoje
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": id_cli}
    motoristas = motoristas_disponiveis()
    veiculos = filtra_veiculo("17", "TRANSPORTADORA")
    contexto.update({"motoristas": motoristas, "veiculos": veiculos})
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
            facade.save_notas_cliente(nota_form)
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


def exclui_nota_cliente(request):
    _id_not = request.GET.get("idNota")
    _id_cli = request.GET.get("idCliente")
    facade.delete_notas_cliente(_id_not)
    notas = facade.create_contexto_seleciona_notas(_id_cli, "NumeroNota")
    cliente = facade.create_contexto_cliente(_id_cli)
    hoje = facade.hoje
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": _id_cli}
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data


def ocorrencia_nota_cliente(request):
    _id_not = request.GET.get("idNota")
    _id_cli = request.GET.get("idCliente")
    notas = facade.create_contexto_ocorrencia_notas(_id_not)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(_id_not, "NumeroNota")
    hoje = facade.hoje
    contexto = {
        "ocorrencias": ocorrencias,
        "notas": notas,
        "hoje": hoje,
        "id_nota": _id_not,
    }
    data = facade.create_data_nota_selecionada(request, contexto)
    return data


def adiciona_ocorrencia(request):
    error, msg = facade.valida_ocorrencia(request)
    ocorrencia_form = facade.read_ocorrencia_post(request)
    id_ocor = request.POST.get("idocorrencia")
    if not error:
        if id_ocor:
            facade.update_ocorrencia(ocorrencia_form, id_ocor)
        else:
            facade.save_ocorrencia(ocorrencia_form)
        ocorrencia_form = dict()
    id_not = request.POST.get("id_nota_clientes")
    notas = facade.create_contexto_ocorrencia_notas(id_not)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(id_not, "NumeroNota")
    hoje = facade.hoje
    contexto = {
        "notas": notas,
        "ocorrencias": ocorrencias,
        "hoje": hoje,
        "id_nota": id_not,
    }
    contexto.update({"error": error})
    contexto.update(msg)
    data = facade.create_data_ocorrencia_selecionada(request, contexto)
    return data


def adiciona_romaneio(request):
    romaneio = facade.read_romaneio_post(request)
    facade.save_romaneio(romaneio)
    pass


def edita_romaneio(request):
    pass


def seleciona_romaneio(request):
    pass
