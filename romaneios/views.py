from django.shortcuts import render
from minutas.facade import filtra_veiculo, motoristas_disponiveis

from romaneios import facade
from romaneios.print import print_notas_status, print_romaneio


def index_romaneio(request):
    clientes = facade.create_contexto_seleciona_cliente()
    contexto = {"clientes": clientes}
    return render(request, "romaneios/index.html", contexto)


def seleciona_cliente(request):
    error, msg = facade.valida_seleciona_cliente(request)
    if not error:
        if request.POST:
            id_cli = request.POST.get("cliente")
        else:
            id_cli = request.GET.get("cliente")
        notas = facade.create_contexto_seleciona_notas(id_cli, "-NumeroNota")
        cliente = facade.create_contexto_cliente(id_cli)
        hoje = facade.hoje
        destinatarios = facade.lista_destinatarios()
        enderecos = facade.lista_enderecos()
        bairros = facade.lista_bairros()
        contexto = {
            "notas": notas,
            "cliente": cliente,
            "hoje": hoje,
            "idcliente": id_cli,
            "destinatarios": destinatarios,
            "enderecos": enderecos,
            "bairros": bairros,
        }
        romaneios = facade.create_contexto_romaneios()
        contexto.update({"romaneios": romaneios})
        motoristas = motoristas_disponiveis()
        veiculos = filtra_veiculo("17", "TRANSPORTADORA")
        contexto.update({"motoristas": motoristas, "veiculos": veiculos})
        status_nota = facade.create_contexto_filtro_status()
        contexto.update({"status_nota": status_nota})
        data = facade.create_data_cliente_selecionado(request, contexto)
    else:
        clientes = facade.create_contexto_seleciona_cliente()
        contexto = {"clientes": clientes, "error": error}
        contexto.update(msg)
        data = facade.create_data_seleciona_cliente(request, contexto)
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
    destinatarios = facade.lista_destinatarios()
    enderecos = facade.lista_enderecos()
    bairros = facade.lista_bairros()
    contexto = {
        "nota_form": nota_form,
        "cliente": cliente,
        "error": error,
        "idcliente": _id_cli,
        "destinatarios": destinatarios,
        "enderecos": enderecos,
        "bairros": bairros,
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
    id_rom = facade.create_contexto_romaneio_tem_nota(id_not)
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
    if id_rom:
        not_rom = facade.create_contexto_notas_romaneio(id_rom)
        romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
        contexto.update({"notas_romaneio": not_rom, "romaneios": romaneio})
    data = facade.create_data_ocorrencia_selecionada(request, contexto)
    return data


def adiciona_romaneio(request):
    id_rom = request.POST.get("idRomaneio")
    romaneio = facade.read_romaneio_post(request)
    if id_rom:
        facade.update_romaneio(romaneio, id_rom)
    else:
        facade.save_romaneio(romaneio)
    romaneios = facade.create_contexto_romaneios()
    contexto = {"romaneios": romaneios}
    data = facade.create_data_romaneios(request, contexto)
    return data


def edita_romaneio(request):
    _id_rom = request.GET.get("idRomaneio")
    romaneio = facade.read_romaneio_database(_id_rom)
    contexto = {"romaneio": romaneio}
    motoristas = motoristas_disponiveis()
    veiculos = filtra_veiculo("17", "TRANSPORTADORA")
    contexto.update({"motoristas": motoristas, "veiculos": veiculos})
    data = facade.create_data_edita_romaneio(request, contexto)
    return data


def seleciona_romaneio(request):
    id_rom = request.GET.get("idRomaneio")
    id_cli = request.GET.get("idCliente")
    not_rom = facade.create_contexto_notas_romaneio(id_rom)
    romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
    arquivo = facade.create_contexto_pdf_romaneio(romaneio[0]["romaneio"])
    contexto = {
        "notas_romaneio": not_rom,
        "romaneios": romaneio,
        "idcliente": id_cli,
        "arquivo": arquivo,
    }
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def adiciona_nota_romaneio(request):
    id_not = request.GET.get("idNota")
    id_rom = request.GET.get("idRomaneio")
    id_cli = request.GET.get("idCliente")
    facade.save_nota_romaneio(id_not, id_rom)
    facade.altera_status_rota(id_rom, id_not)
    not_rom = facade.create_contexto_notas_romaneio(id_rom)
    romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
    contexto = {
        "notas_romaneio": not_rom,
        "romaneios": romaneio,
        "idcliente": id_cli,
    }
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def exclui_nota_romaneio(request):
    id_romaneio_nota = request.GET.get("idRomaneioNota")
    id_rom = request.GET.get("idRomaneio")
    id_not = request.GET.get("idNota")
    hoje = facade.hoje()
    facade.delete_nota_romaneio(id_romaneio_nota)
    facade.altera_status_remove_romaneio(id_rom, id_not, hoje)
    not_rom = facade.create_contexto_notas_romaneio(id_rom)
    romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
    contexto = {
        "notas_romaneio": not_rom,
        "romaneios": romaneio,
    }
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def ler_nota_xml(request):
    pass


def carrega_xml(request):
    file = request.FILES["uploadFile"]
    dados = facade.ler_nota_xml(file)
    return dados


def orderna_notas(request):
    id_cli = request.GET.get("cliente")
    sort_nota = request.GET.get("sort")
    tipo_sort = request.GET.get("tipo_sort")
    filtro_status = request.GET.get("status")
    if tipo_sort == "completo":
        notas = facade.create_contexto_seleciona_notas(id_cli, sort_nota)
        contexto = {"notas": notas, "idcliente": id_cli, "tipo_sort": tipo_sort}
    else:
        contexto = facade.create_contexto_filtro_notas_status(
            id_cli, filtro_status, sort_nota
        )
        contexto.update({"idcliente": id_cli, "tipo_sort": tipo_sort})
    data = facade.create_data_sort_notas(request, contexto)
    return data


def imprime_romaneio(request):
    id_rom = request.GET.get("idRomaneio")
    id_cli = request.GET.get("idCliente")
    contexto = facade.create_contexto_imprime_romaneio(id_rom, id_cli)
    response = print_romaneio(contexto)
    return response


def imprime_notas_status(request):
    status = request.GET.get("StatusNota")
    id_cli = request.GET.get("idCliente")
    contexto = facade.create_contexto_filtro_notas_status(id_cli, status, "NumeroNota")
    contexto.update({"sort_status": status})
    response = print_notas_status(contexto)
    return response


def filtra_nota_cliente(request):
    nota = request.GET.get("nota")
    id_cli = request.GET.get("cliente")
    notas = facade.create_contexto_filtro_nota(nota)
    id_rom = facade.create_contexto_romaneio_tem_nota(int(notas[0]["id_nota_clientes"]))
    contexto = {"notas": notas, "idcliente": id_cli}
    not_rom = facade.create_contexto_notas_romaneio(id_rom)
    romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
    arquivo = False
    if romaneio:
        arquivo = facade.create_contexto_pdf_romaneio(romaneio[0]["romaneio"])
    contexto.update(
        {
            "notas_romaneio": not_rom,
            "romaneios": romaneio,
            "idcliente": id_cli,
            "id_rom": id_rom,
            "arquivo": arquivo,
        }
    )
    data = facade.create_data_filtro_nota(request, contexto)
    return data


def fecha_romaneio(request):
    id_rom = request.GET.get("idRomaneio")
    facade.fecha_romaneio(id_rom)
    romaneio = facade.create_contexto_romaneios()
    contexto = {
        "romaneios": romaneio,
    }
    data = facade.create_data_romaneios(request, contexto)
    return data


def envia_telegram_romaneio(request):
    rom = request.GET.get("Romaneio")
    facade.send_arquivo(rom)
    data = facade.create_data_send_arquivo()
    return data


def envia_telegram_relatorio(request):
    sort_nota = request.GET.get("status")
    facade.send_arquivo_relatorio(sort_nota)
    data = facade.create_data_send_arquivo()
    return data


def filtra_status(request):
    filtro_status = request.GET.get("status")
    id_cli = request.GET.get("cliente")
    contexto = facade.create_contexto_filtro_notas_status(
        id_cli, filtro_status, "NumeroNota"
    )
    contexto.update({"idcliente": id_cli})
    data = facade.create_data_filtro_status_reduzida(request, contexto)
    return data


def nota_deposito(request):
    id_nota_clientes = request.GET.get("idNotaClientes")
    facade.altera_status_pendente(id_nota_clientes)
    filtro_status = request.GET.get("status")
    id_cli = request.GET.get("cliente")
    contexto = facade.create_contexto_filtro_notas_status(
        id_cli, filtro_status, "NumeroNota"
    )
    contexto.update({"idcliente": id_cli})
    data = facade.create_data_filtro_status_reduzida(request, contexto)
    return data
