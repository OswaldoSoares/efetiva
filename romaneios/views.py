from django.shortcuts import render
from minutas.facade import filtra_veiculo, motoristas_disponiveis

from romaneios import facade
from romaneios.print import print_notas_status, print_romaneio
from website.facade import str_hoje


def index_romaneio(request):
    clientes = facade.create_contexto_seleciona_cliente()
    contexto = {"clientes": clientes}
    return render(request, "romaneios/index.html", contexto)


def seleciona_cliente(request):
    error, msg = facade.valida_seleciona_cliente(request)
    if not error:
        if request.POST:
            idcliente = request.POST.get("cliente")
        else:
            idcliente = request.GET.get("cliente")
        notas = facade.create_contexto_seleciona_notas(idcliente, "-NumeroNota")
        cliente = facade.create_contexto_cliente(idcliente)
        hoje = str_hoje()
        destinatarios = facade.lista_destinatarios()
        enderecos = facade.lista_enderecos()
        bairros = facade.lista_bairros()
        contexto = {
            "notas": notas,
            "cliente": cliente,
            "hoje": hoje,
            "idcliente": idcliente,
            "destinatarios": destinatarios,
            "enderecos": enderecos,
            "bairros": bairros,
            "sort_status": "SEM FILTRO",
        }
        romaneios = facade.create_contexto_romaneios(idcliente)
        contexto.update({"romaneios": romaneios})
        motoristas = motoristas_disponiveis()
        veiculos = filtra_veiculo("17", "TRANSPORTADORA")
        contexto.update({"motoristas": motoristas, "veiculos": veiculos})
        status_nota = facade.create_contexto_filtro_status()
        contexto.update({"status_nota": status_nota})
        quantidade_notas = facade.create_contexto_quantidades_status()
        contexto.update({"rotas": quantidade_notas[0]["rota"]})
        contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
        contexto.update({"pendente": quantidade_notas[0]["pendente"]})
        contexto.update({"recusada": quantidade_notas[0]["recusada"]})
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
    hoje = str_hoje()
    filtro_status = request.POST.get("filtro")
    if filtro_status:
        contexto = facade.create_contexto_filtro_notas_status(
            id_cli, filtro_status, "NumeroNota"
        )
    else:
        cliente = facade.create_contexto_cliente(id_cli)
        contexto = {
            "notas": notas,
            "cliente": cliente,
        }
    contexto.update({"hoje": hoje, "idcliente": id_cli})
    contexto.update({"nota_form": nota_form, "error": error})
    contexto.update(msg)
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
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
    hoje = str_hoje()
    contexto = {"notas": notas, "cliente": cliente, "hoje": hoje, "idcliente": _id_cli}
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data


def ocorrencia_nota_cliente(request):
    idnota = request.GET.get("idNota")
    idcliente = request.GET.get("idCliente")
    notas = facade.create_contexto_ocorrencia_notas(idnota)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(idnota, "NumeroNota")
    hoje = str_hoje()
    contexto = {
        "ocorrencias": ocorrencias,
        "notas": notas,
        "hoje": hoje,
        "id_nota": idnota,
        "idcliente": idcliente,
    }
    data = facade.create_data_nota_selecionada(request, contexto)
    return data


def adiciona_ocorrencia(request):
    error, msg = facade.valida_ocorrencia(request)
    ocorrencia_form = facade.read_ocorrencia_post(request)
    idocorrencia = request.POST.get("idocorrencia")
    idcliente = request.POST.get("idcliente")
    if not error:
        if idocorrencia:
            facade.update_ocorrencia(ocorrencia_form, idocorrencia)
        else:
            facade.save_ocorrencia(ocorrencia_form, idcliente)
        ocorrencia_form = dict()
    idnota = request.POST.get("id_nota_clientes")
    idtomaneio = facade.create_contexto_romaneio_tem_nota(idnota)
    notas = facade.create_contexto_ocorrencia_notas(idnota)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(idnota, "NumeroNota")
    hoje = str_hoje()
    contexto = {
        "notas": notas,
        "ocorrencias": ocorrencias,
        "hoje": hoje,
        "id_nota": idnota,
        "idcliente": idcliente,
    }
    contexto.update({"error": error})
    contexto.update(msg)
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    if idtomaneio:
        notas_romaneio = facade.create_contexto_notas_romaneio(idtomaneio)
        romaneio = facade.create_contexto_seleciona_romaneio(idtomaneio)
        contexto.update({"notas_romaneio": notas_romaneio, "romaneios": romaneio})
    data = facade.create_data_ocorrencia_selecionada(request, contexto)
    return data


def adiciona_romaneio(request):
    idromaneio = request.POST.get("idRomaneio")
    idcliente = request.POST.get("idCliente")
    romaneio = facade.read_romaneio_post(request)
    if idromaneio:
        facade.update_romaneio(romaneio, idromaneio)
    else:
        facade.save_romaneio(romaneio)
    romaneios = facade.create_contexto_romaneios(idcliente)
    contexto = {"romaneios": romaneios}
    data = facade.create_data_romaneios(request, contexto)
    return data


def edita_romaneio(request):
    idromaneio = request.GET.get("idRomaneio")
    idcliente = request.GET.get("idCliente")
    romaneio = facade.read_romaneio_database(idromaneio)
    contexto = {"romaneio": romaneio, "idcliente": idcliente}
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
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def exclui_nota_romaneio(request):
    id_romaneio_nota = request.GET.get("idRomaneioNota")
    id_rom = request.GET.get("idRomaneio")
    id_not = request.GET.get("idNota")
    hoje = str_hoje()
    facade.delete_nota_romaneio(id_romaneio_nota)
    facade.altera_status_remove_romaneio(id_rom, id_not, hoje)
    not_rom = facade.create_contexto_notas_romaneio(id_rom)
    romaneio = facade.create_contexto_seleciona_romaneio(id_rom)
    contexto = {
        "notas_romaneio": not_rom,
        "romaneios": romaneio,
    }
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
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
    ordem = request.GET.get("ordem")
    if not ordem:
        ordem = "NumeroNota"
    contexto = facade.create_contexto_filtro_notas_status(id_cli, status, ordem)
    contexto.update({"sort_status": status})
    response = print_notas_status(contexto)
    return response


def filtra_nota_cliente(request):
    nota = request.GET.get("nota")
    idcliente = request.GET.get("cliente")
    notas = facade.create_contexto_filtro_nota(nota, idcliente)
    idromaneio = None
    notas_romaneio = None
    romaneio = None
    if notas:
        idromaneio = facade.create_contexto_romaneio_tem_nota(
            int(notas[0]["id_nota_clientes"])
        )
        notas_romaneio = facade.create_contexto_notas_romaneio(idromaneio)
        romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
    contexto = {"notas": notas, "idcliente": idcliente}
    arquivo = False
    if romaneio:
        arquivo = facade.create_contexto_pdf_romaneio(romaneio[0]["romaneio"])
    contexto.update(
        {
            "notas_romaneio": notas_romaneio,
            "romaneios": romaneio,
            "idcliente": idcliente,
            "id_rom": idromaneio,
            "arquivo": arquivo,
        }
    )
    data = facade.create_data_filtro_nota(request, contexto)
    return data


def fecha_romaneio(request):
    idromaneio = request.GET.get("idRomaneio")
    idcliente = request.GET.get("idCliente")
    facade.fecha_romaneio(idromaneio)
    romaneio = facade.create_contexto_romaneios(idcliente)
    contexto = {
        "romaneios": romaneio,
    }
    data = facade.create_data_romaneios(request, contexto)
    return data


def envia_telegram_romaneio(request):
    rom = request.GET.get("Romaneio")
    idcliente = request.GET.get("idCliente")
    facade.send_arquivo(rom, idcliente)
    data = facade.create_data_send_arquivo()
    return data


def envia_telegram_relatorio(request):
    sort_nota = request.GET.get("status")
    idcliente = request.GET.get("idCliente")
    facade.send_arquivo_relatorio(sort_nota, idcliente)
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
    quantidade_notas = facade.create_contexto_quantidades_status()
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    data = facade.create_data_filtro_status_reduzida(request, contexto)
    return data
