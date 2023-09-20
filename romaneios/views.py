from django.http import JsonResponse
from django.shortcuts import render
from minutas.facade import filtra_veiculo, motoristas_disponiveis

from romaneios import facade
from romaneios.print import print_notas_status, print_romaneio
from website.facade import str_hoje
from rolepermissions.decorators import has_permission_decorator


@has_permission_decorator("modulo_clientes")
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
        # notas = facade.create_contexto_seleciona_notas(idcliente, "-NumeroNota")
        contexto = facade.create_contexto_notas(idcliente, "PENDENTE", "-NumeroNota")
        # cliente = facade.create_contexto_cliente(idcliente)
        hoje = str_hoje()
        locais = facade.lista_locais()
        enderecos = facade.lista_enderecos()
        bairros = facade.lista_bairros()
        contexto.update({
            "hoje": hoje,
            "idcliente": idcliente,
            "locais": locais,
            "enderecos": enderecos,
            "bairros": bairros,
            "sort_status": "PENDENTE",
        })
        romaneios = facade.create_contexto_romaneios(idcliente)
        contexto.update({"romaneios": romaneios})
        motoristas = motoristas_disponiveis()
        veiculos = filtra_veiculo("17", "TRANSPORTADORA")
        contexto.update({"motoristas": motoristas, "veiculos": veiculos})
        status_nota = facade.create_contexto_filtro_status()
        contexto.update({"status_nota": status_nota})
        quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
        contexto.update({"rotas": quantidade_notas[0]["rota"]})
        contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
        contexto.update({"pendente": quantidade_notas[0]["pendente"]})
        contexto.update({"recusada": quantidade_notas[0]["recusada"]})
        contexto.update({"coletada": quantidade_notas[0]["coletada"]})
        data = facade.create_data_cliente_selecionado(request, contexto)
    else:
        clientes = facade.create_contexto_seleciona_cliente()
        contexto = {"clientes": clientes, "error": error}
        contexto.update(msg)
        data = facade.create_data_seleciona_cliente(request, contexto)
    return data


def busca_local_nota(request):
    local = request.GET.get("local")
    data = facade.create_data_busca_endereco(local)
    return data


def adiciona_nota_cliente(request):
    error, msg = facade.valida_notas_cliente(request)
    nota_form = facade.read_nota_post(request)
    idnota = request.POST.get("idnota")
    idcliente = request.POST.get("cliente")
    if not error:
        if idnota:
            facade.update_notas_cliente(nota_form, idnota)
        else:
            facade.save_notas_cliente(nota_form)
        nota_form = dict()
    contexto = facade.create_contexto_notas(idcliente, "NOTA CADASTRADA", "NumeroNota")
    hoje = str_hoje()
    contexto.update({"hoje": hoje, "idcliente": idcliente})
    contexto.update({"nota_form": nota_form, "error": error})
    contexto.update(msg)
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
    data = facade.create_data_cliente_selecionado(request, contexto)
    return data


def edita_nota_cliente(request):
    _id_not = request.GET.get("idNota")
    _id_cli = request.GET.get("idCliente")
    cliente = facade.create_contexto_cliente(_id_cli)
    error, msg = False, dict()
    nota_form = facade.read_nota_database(_id_not)
    locais = facade.lista_locais()
    enderecos = facade.lista_enderecos()
    bairros = facade.lista_bairros()
    contexto = {
        "nota_form": nota_form,
        "cliente": cliente,
        "error": error,
        "idcliente": _id_cli,
        "locais": locais,
        "enderecos": enderecos,
        "bairros": bairros,
    }
    contexto.update(msg)
    data = facade.create_data_edita_nota(request, contexto)
    return data


def exclui_nota_cliente(request):
    idnota = request.GET.get("idNota")
    idcliente = request.GET.get("idCliente")
    filtro_status = request.GET.get("filtro")
    facade.delete_notas_cliente(idnota)
    contexto = facade.create_contexto_notas(idcliente, filtro_status, "NumeroNota")
    hoje = str_hoje()
    contexto.update({
        "hoje": hoje,
        "idcliente": idcliente,
    })
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
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
        "statusnota": notas[0]["statusnota"],
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
    idromaneio = facade.create_contexto_romaneio_tem_nota(idnota)
    notas = facade.create_contexto_ocorrencia_notas(idnota)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(idnota, "NumeroNota")
    hoje = str_hoje()
    contexto = {
        "notas": notas,
        "ocorrencias": ocorrencias,
        "hoje": hoje,
        "id_nota": idnota,
        "idcliente": idcliente,
        "statusnota": notas[0]["statusnota"],
    }
    contexto.update({"error": error})
    contexto.update(msg)
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
    if idromaneio:
        notas_romaneio = facade.create_contexto_notas_romaneio(idromaneio)
        (
            quantidade_entregas,
            quantidade_falta,
        ) = facade.create_contexto_quantidade_entregas(notas_romaneio)
        romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
        contexto.update(
            {
                "notas_romaneio": notas_romaneio,
                "romaneios": romaneio,
                "quantidade_entregas": quantidade_entregas,
                "quantidade_falta": quantidade_falta,
            }
        )
    print(contexto)
    data = facade.create_data_ocorrencia_selecionada(request, contexto)
    return data

def exclui_ocorrencia(request):
    idnotasocorrencia = request.GET.get("idnotasocorrencia")
    idnota = request.GET.get("idnota")
    idcliente = request.GET.get("idcliente")
    facade.delete_ocorrencia(idnotasocorrencia, idnota)
    idromaneio = facade.create_contexto_romaneio_tem_nota(idnota)
    notas = facade.create_contexto_ocorrencia_notas(idnota)
    ocorrencias = facade.create_contexto_seleciona_ocorrencia(idnota, "NumeroNota")
    hoje = str_hoje()
    contexto = {
        "notas": notas,
        "ocorrencias": ocorrencias,
        "hoje": hoje,
        "id_nota": idnota,
        "idcliente": idcliente,
        "statusnota": notas[0]["statusnota"],
    }
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
    if idromaneio:
        notas_romaneio = facade.create_contexto_notas_romaneio(idromaneio)
        (
            quantidade_entregas,
            quantidade_falta,
        ) = facade.create_contexto_quantidade_entregas(notas_romaneio)
        romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
        contexto.update(
            {
                "notas_romaneio": notas_romaneio,
                "romaneios": romaneio,
                "quantidade_entregas": quantidade_entregas,
                "quantidade_falta": quantidade_falta,
            }
    )
    print(contexto)
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
    contexto = {"romaneios": romaneios, "idcliente": idcliente}
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
    print(f"[INFO] - contexto: {contexto}")
    data = facade.create_data_edita_romaneio(request, contexto)
    return data


def seleciona_romaneio(request):
    idromaneio = request.GET.get("idRomaneio")
    idcliente = request.GET.get("idCliente")
    notas_romaneio = facade.create_contexto_notas_romaneio(idromaneio)
    quantidade_entregas, quantidade_falta = facade.create_contexto_quantidade_entregas(
        notas_romaneio
    )
    romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
    peso = facade.create_contexto_peso_romaneio(notas_romaneio)
    arquivo = facade.create_contexto_pdf_romaneio(romaneio[0]["romaneio"])
    contexto = {
        "notas_romaneio": notas_romaneio,
        "romaneios": romaneio,
        "idcliente": idcliente,
        "arquivo": arquivo,
        "quantidade_entregas": quantidade_entregas,
        "quantidade_falta": quantidade_falta,
    }
    contexto.update(peso)
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def seleciona_filtro_emitente(request):
    emitente = request.GET.get("emitente")
    idcliente = request.GET.get("idcliente")
    notas = facade.create_contexto_filtro_emitente(emitente, idcliente)
    idromaneio = None
    notas_romaneio = None
    romaneio = None
    if notas:
        idromaneio = facade.create_contexto_romaneio_tem_nota(
            int(notas[0]["id_nota_clientes"])
        )
    contexto = {"notas": notas, "idcliente": idcliente}
    contexto.update(
        {
            "notas_romaneio": notas_romaneio,
            "romaneios": romaneio,
            "idcliente": idcliente,
            "id_rom": idromaneio,
        }
    )
    data = facade.create_data_filtro_nota(request, contexto)
    return data


def seleciona_filtro_destinatario(request):
    destinatario = request.GET.get("destinatario")
    idcliente = request.GET.get("idcliente")
    notas = facade.create_contexto_filtro_destinatario(destinatario, idcliente)
    idromaneio = None
    notas_romaneio = None
    romaneio = None
    if notas:
        idromaneio = facade.create_contexto_romaneio_tem_nota(
            int(notas[0]["id_nota_clientes"])
        )
    print(f"[INFO] idromaneio: {idromaneio}")
    contexto = {"notas": notas, "idcliente": idcliente}
    contexto.update(
        {
            "notas_romaneio": notas_romaneio,
            "romaneios": romaneio,
            "idcliente": idcliente,
            "id_rom": idromaneio,
        }
    )
    data = facade.create_data_filtro_nota(request, contexto)
    return data


def adiciona_nota_romaneio(request):
    idnota = request.GET.get("idNota")
    idromaneio = request.GET.get("idRomaneio")
    idcliente = request.GET.get("idCliente")
    facade.save_nota_romaneio(idnota, idromaneio)
    facade.altera_status_rota(idromaneio, idnota)
    not_rom = facade.create_contexto_notas_romaneio(idromaneio)
    romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
    contexto = {
        "notas_romaneio": not_rom,
        "romaneios": romaneio,
        "idcliente": idcliente,
    }
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def exclui_nota_romaneio(request):
    idromaneionotas = request.GET.get("idRomaneioNota")
    idromaneio = request.GET.get("idRomaneio")
    idnota = request.GET.get("idNota")
    idcliente = request.GET.get("idCliente")
    filtro_status = request.GET.get("status")
    hoje = str_hoje()
    facade.delete_nota_romaneio(idromaneionotas)
    facade.altera_status_remove_romaneio(idromaneio, idnota, hoje)
    contexto = facade.create_contexto_notas(idcliente, filtro_status, "NumeroNota")
    # contexto = facade.create_contexto_filtro_notas_status(
    #     idcliente, filtro_status, "NumeroNota"
    # )
    notas_romaneio = facade.create_contexto_notas_romaneio(idromaneio)
    romaneio = facade.create_contexto_seleciona_romaneio(idromaneio)
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update(
        {
            "notas_romaneio": notas_romaneio,
            "romaneios": romaneio,
            "rotas": quantidade_notas[0]["rota"],
            "cadastrada": quantidade_notas[0]["cadastrada"],
            "pendente": quantidade_notas[0]["pendente"],
            "recusada": quantidade_notas[0]["recusada"],
            "coletada": quantidade_notas[0]["coletada"],
        }
    )
    data = facade.create_data_lista_notas_romaneio(request, contexto)
    return data


def ler_nota_xml(request):
    pass


def carrega_xml(request):
    file = request.FILES["uploadFile"]
    dados = facade.ler_nota_xml(file)
    return JsonResponse(dados)


def carrega_pasta_xml(request):
    """ Carrega pasta com arquivos XML """
    local_coleta = request.POST.get("local_coleta")
    id_cliente = request.POST.get("id_cliente")
    files = request.FILES.getlist("xml_files")
    if local_coleta:
        for x in files:
            nota = facade.ler_nota_xml(x)
            nota['local_coleta'] = local_coleta
            nota['id_cliente'] = id_cliente
            nota_xml = facade.read_nota_xml(nota)
            facade.save_notas_cliente(nota_xml)
    dados = {}
    return JsonResponse(dados)


def orderna_notas(request):
    idcliente = request.GET.get("cliente")
    sort_nota = request.GET.get("sort")
    tipo_sort = request.GET.get("tipo_sort")
    filtro_status = request.GET.get("status")
    contexto = facade.create_contexto_notas(idcliente, filtro_status, sort_nota)
    # if tipo_sort == "completo":
    #     notas = facade.create_contexto_seleciona_notas(idcliente, sort_nota)
    #     contexto = {"notas": notas, "idcliente": idcliente, "tipo_sort": tipo_sort}
    # else:
    #     contexto = facade.create_contexto_filtro_notas_status(
    #         idcliente, filtro_status, sort_nota
    #     )
    contexto.update({"idcliente": idcliente, "tipo_sort": tipo_sort})
    data = facade.create_data_sort_notas(request, contexto)
    return data


def imprime_romaneio(request):
    id_rom = request.GET.get("idRomaneio")
    id_cli = request.GET.get("idCliente")
    contexto = facade.create_contexto_imprime_romaneio(id_rom, id_cli)
    response = print_romaneio(contexto)
    return response


def imprime_notas_status(request):
    filter_status = request.GET.get("StatusNota")
    idcliente = request.GET.get("idCliente")
    order_nota = request.GET.get("ordem")
    if not order_nota:
        order_nota = "NumeroNota"
    contexto = facade.create_contexto_notas(idcliente, filter_status, order_nota)
    # contexto = facade.create_contexto_filtro_notas_status(idcliente, sort_status, order_nota)
    contexto.update({"sort_status": filter_status})
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
    facade.fecha_romaneio_cliente(idromaneio)
    romaneio = facade.create_contexto_romaneios(idcliente)
    contexto = {
        "romaneios": romaneio,
        "idcliente": idcliente,
    }
    data = facade.create_data_romaneios(request, contexto)
    return data


def reabre_romaneio(request):
    idromaneio = request.GET.get("idRomaneio")
    idcliente = request.GET.get("idCliente")
    facade.reabre_romaneio_cliente(idromaneio)
    romaneio = facade.create_contexto_romaneios(idcliente)
    contexto = {
        "romaneios": romaneio,
        "idcliente": idcliente,
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
    filter_status = request.GET.get("status")
    idcliente = request.GET.get("cliente")
    contexto = facade.create_contexto_notas(idcliente, filter_status, "NumeroNota")
    # contexto = facade.create_contexto_filtro_notas_status(
    #     idcliente, filter_status, "NumeroNota"
    # )
    contexto.update({"idcliente": idcliente})
    data = facade.create_data_filtro_status_reduzida(request, contexto)
    return data


def nota_deposito(request):
    idnotasclientes = request.GET.get("idNotaClientes")
    facade.altera_status_pendente(idnotasclientes)
    idcliente = request.GET.get("cliente")
    contexto = facade.create_contexto_notas(idcliente, "NOTA CADASTRADA", "NumeroNota")
    contexto.update({"idcliente": idcliente})
    quantidade_notas = facade.create_contexto_quantidades_status(idcliente)
    contexto.update({"rotas": quantidade_notas[0]["rota"]})
    contexto.update({"cadastrada": quantidade_notas[0]["cadastrada"]})
    contexto.update({"pendente": quantidade_notas[0]["pendente"]})
    contexto.update({"recusada": quantidade_notas[0]["recusada"]})
    contexto.update({"coletada": quantidade_notas[0]["coletada"]})
    data = facade.create_data_filtro_status_reduzida(request, contexto)
    return data
