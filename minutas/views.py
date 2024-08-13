from io import BytesIO
from textwrap import wrap
from clientes.facade import create_contexto_seleciona_cliente

from clientes.models import FoneContatoCliente
from django.db.models import F, Max, Sum, Value
from django.db.models.functions import Concat
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import (
    get_list_or_404,
    get_object_or_404,
    redirect,
    render,
)
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from rolepermissions.decorators import has_permission_decorator
from transefetiva.settings.settings import STATIC_ROOT
from veiculos.models import Veiculo

from minutas import facade
from minutas.itens_card import criar_itens_card_minuta
from minutas.facade import MinutaSelecionada
from minutas.print import print_minutas_periodo
from website.facade import str_hoje

from .facade import (
    MinutasStatus,
    edita_km_final,
    estorna_paga,
    filtra_consulta,
    filtro_cidades,
    filtro_clientes,
    filtro_colaboradores,
    filtro_veiculos,
    forn_minuta,
    novo_status_minuta,
    remove_colaborador,
    remove_despessa,
    remove_entrega,
    retorna_json,
)
from .forms import (
    CadastraComentarioMinuta,
    CadastraMinutaDespesa,
    CadastraMinutaHoraFinal,
    CadastraMinutaKMFinal,
    CadastraMinutaKMInicial,
    CadastraMinutaNota,
    CadastraMinutaVeiculo,
    FormEditaVeiculoSolicitado,
    FormInsereDespesa,
    FormInsereEntrega,
    FormMinuta,
)
from .models import Minuta, MinutaColaboradores, MinutaItens, MinutaNotas


def cmp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def convertemp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def excluiminutaitens(idminutaitens):
    """
    Função para excluir um item da Minuta

    :param idminutaitens:
    :return:
    """
    minutaitens = MinutaItens.objects.filter(idMinutaItens=idminutaitens)
    if minutaitens:
        obj = MinutaItens()
        obj.idMinutaItens = idminutaitens
        obj.delete()
    return True


def cria_minuta_fatura(valor, idminuta):
    """
    Função para inserir e atualizar fatura da minuta

    :param :
    :param :
    :return:
    """
    minuta = Minuta.objects.get(idMinuta=idminuta)
    if minuta:
        obj = Minuta()
        obj.idMinuta = minuta.idMinuta
        obj.Minuta = minuta.Minuta
        obj.DataMinuta = minuta.DataMinuta
        obj.HoraInicial = minuta.HoraInicial
        obj.HoraFinal = minuta.HoraFinal
        obj.Coleta = minuta.Coleta
        obj.Entrega = minuta.Entrega
        obj.KMInicial = minuta.KMInicial
        obj.KMFinal = minuta.KMFinal
        obj.Obs = minuta.Obs
        obj.StatusMinuta = minuta.StatusMinuta
        obj.Valor = valor
        obj.Comentarios = minuta.Comentarios
        obj.idFatura_id = None
        obj.idCliente = minuta.idCliente
        obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
        obj.idVeiculo = minuta.idVeiculo
        obj.save()
    return True


def altera_status_minuta(novo_status, idminuta):
    minuta = get_object_or_404(Minuta, idMinuta=idminuta)
    if minuta:
        obj = Minuta()
        obj.idMinuta = minuta.idMinuta
        obj.Minuta = minuta.Minuta
        obj.DataMinuta = minuta.DataMinuta
        obj.HoraInicial = minuta.HoraInicial
        obj.HoraFinal = minuta.HoraFinal
        obj.Coleta = minuta.Coleta
        obj.Entrega = minuta.Entrega
        obj.KMInicial = minuta.KMInicial
        obj.KMFinal = minuta.KMFinal
        obj.Obs = minuta.Obs
        obj.StatusMinuta = novo_status
        obj.Valor = minuta.Valor
        obj.Comentarios = minuta.Comentarios
        obj.idCliente = minuta.idCliente
        obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
        obj.idVeiculo = minuta.idVeiculo
        obj.idfatura = None
        obj.save()
    return True


def kmfinal_veiculo(idveiculo):
    veiculo = Minuta.objects.filter(idVeiculo=idveiculo).aggregate(
        Max("KMFinal")
    )
    kmfinal = [item for item in veiculo.values()]
    return kmfinal[0]


@has_permission_decorator("modulo_minutas")
def index_minuta(request):
    """
    Função para carregar a página principal do Módulo: Minuta.
    Cria como padrão a QuerySet minuta apenas com as Minutas cujo StatusMinuta é Aberta.
    Caso tenha request GET cria variaveis e QuerySet com as Minutas cujo Status ou minuta
    foi selecionado.
    Cria uma lista 'minuta_status' com as opções de Status para compor o Filtro.
    Cria a QuerySet minutacolaboradores apenas com os Colaboradores cujo Cargo é Motorista.

    :param request:
    :return:
    """
    aberta = ""
    m_aberta = MinutasStatus("ABERTA").minutas
    t_aberta = len(m_aberta)
    m_concluida = MinutasStatus("CONCLUIDA").minutas
    t_concluida = len(m_concluida)
    m_fechada = MinutasStatus("FECHADA").minutas
    t_fechada = len(m_fechada)
    clientes = create_contexto_seleciona_cliente()
    filtro_cliente = filtro_clientes()
    filtro_colaborador = filtro_colaboradores()
    filtro_veiculo = filtro_veiculos()
    filtro_cidade = filtro_cidades()
    faturada = Minuta.objects.filter(StatusMinuta="FATURADA")
    meu_filtro_minuta = request.GET.get("filtrominuta")
    meu_filtro_status = request.GET.get("filtrostatus")
    if meu_filtro_minuta:
        minuta = Minuta.objects.filter(Minuta=meu_filtro_minuta)
    elif meu_filtro_status:
        if meu_filtro_status == "CONCLUIDA":
            minuta = Minuta.objects.filter(StatusMinuta=meu_filtro_status)
        else:
            minuta = Minuta.objects.filter(
                StatusMinuta=meu_filtro_status
            ).order_by("-Minuta")
    else:
        minuta = Minuta.objects.filter(StatusMinuta="ABERTA").values()
    minuta_status = Minuta.objects.all().values_list("StatusMinuta", flat=True)
    minuta_status = sorted(list(dict.fromkeys(minuta_status)))
    minutacolaboradores = MinutaColaboradores.objects.filter(Cargo="MOTORISTA")
    hoje = str_hoje()
    contexto = {
        "m_aberta": m_aberta,
        "m_concluida": m_concluida,
        "m_fechada": m_fechada,
        "t_aberta": t_aberta,
        "t_concluida": t_concluida,
        "t_fechada": t_fechada,
        "filtro_cliente": filtro_cliente,
        "filtro_colaborador": filtro_colaborador,
        "filtro_veiculo": filtro_veiculo,
        "filtro_cidade": filtro_cidade,
        "faturada": faturada,
        "minuta": minuta,
        "minuta_status": minuta_status,
        "minutacolaboradores": minutacolaboradores,
        "hoje": hoje,
    }
    contexto.update({"clientes": clientes})
    return render(request, "minutas/index.html", contexto)


def minuta(request, idminuta):
    s_minuta = MinutaSelecionada(idminuta).__dict__
    minuta = Minuta.objects.filter(idMinuta=idminuta)
    minutaform = get_object_or_404(minuta, idMinuta=idminuta)
    form_veiculo_solicitado = FormEditaVeiculoSolicitado(instance=minutaform)
    form_hora_final = CadastraMinutaHoraFinal(instance=minutaform)
    form_km_inicial = CadastraMinutaKMInicial(instance=minutaform)
    form_km_final = CadastraMinutaKMFinal(instance=minutaform)
    # contexto 12/08/2024
    minuta = MinutaSelecionada(idminuta)
    contexto = {
        "s_minuta": s_minuta,
        "form_veiculo_solicitado": form_veiculo_solicitado,
        "form_hora_final": form_hora_final,
        "form_km_inicial": form_km_inicial,
        "form_km_final": form_km_final,
        "minuta": minuta,
    }
    itens_minuta = criar_itens_card_minuta(s_minuta)
    contexto.update({"itens_minuta": itens_minuta})
    romaneios = facade.create_contexto_romaneios(s_minuta["idcliente"])
    contexto.update({"romaneios": romaneios})
    checklist = facade.itens_card_checklist(s_minuta)
    contexto.update({"checklist": checklist})
    return render(request, "minutas/minuta.html", contexto)


def imprimeminuta(request, idmin):
    if request.user.is_authenticated:
        minuta = Minuta.objects.get(idMinuta=idmin)
        contato = FoneContatoCliente.objects.filter(idCliente=minuta.idCliente)
        veiculo = ""
        if minuta.idVeiculo_id:
            veiculo = Veiculo.objects.get(idVeiculo=minuta.idVeiculo_id)
        colaboradores = MinutaColaboradores.objects.filter(idMinuta=idmin)
        motorista = ""
        ajudante = ""
        if colaboradores:
            minutacolaboradores = MinutaColaboradores.objects.filter(
                idMinuta=idmin, Cargo="MOTORISTA"
            )
            motorista = [item.idPessoal for item in minutacolaboradores]
            motorista = motorista[0]
            ajudante = MinutaColaboradores.objects.filter(
                idMinuta=idmin, Cargo="AJUDANTE"
            )
        response = HttpResponse(content_type="application/pdf")
        buffer = BytesIO()
        # Create the PDF object, using the BytesIO object as its "file."
        pdf = canvas.Canvas(buffer)
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.

        url = f"{STATIC_ROOT}/website/img/transportadora.jpg"
        pdf.roundRect(
            convertemp(10),
            convertemp(10),
            convertemp(190),
            convertemp(277),
            10,
        )
        pdf.drawImage(
            url,
            convertemp(12),
            convertemp(265),
            convertemp(40),
            convertemp(20),
        )
        pdf.setFont("Times-Bold", 18)
        pdf.drawString(
            convertemp(56),
            convertemp(279),
            "TRANSEFETIVA TRANSPORTE - EIRELLI - ME",
        )
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(
            convertemp(53),
            convertemp(273),
            "RUA OLIMPIO PORTUGAL, 245 - MOOCA - SÃO PAULO - SP - CEP 03112-010",
        )
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(
            convertemp(70),
            convertemp(268),
            "(11) 2305-0582 - WHATSAPP (11) 94167-0583",
        )
        pdf.drawString(
            convertemp(67),
            convertemp(263),
            "e-mail: transefetiva@terra.com.br - "
            "operacional.efetiva@terra.com.br",
        )
        pdf.line(
            convertemp(10), convertemp(260), convertemp(200), convertemp(260)
        )
        # ----
        pdf.setFillColor(HexColor("#FFFFFF"))
        pdf.setStrokeColor(HexColor("#FFFFFF"))
        pdf.rect(
            convertemp(10),
            convertemp(254.1),
            convertemp(190),
            convertemp(5.6),
            fill=1,
            stroke=1,
        )
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        # ----
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(
            convertemp(10),
            convertemp(255.8),
            "ORDEM DE SERVIÇO Nº: " + str(minuta.Minuta),
        )
        pdf.drawRightString(
            convertemp(200),
            convertemp(255.8),
            "DATA: " + minuta.DataMinuta.strftime("%d/%m/%Y"),
        )
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(249),
            convertemp(95),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(57.5), convertemp(250.3), "DADOS DO CLIENTE"
        )
        # ----
        pdf.setFont("Times-Roman", 8)
        pdf.drawString(
            convertemp(11),
            convertemp(246),
            "CLIENTE: " + str(minuta.idCliente.Nome),
        )
        endereco = minuta.idCliente.Endereco + " - " + minuta.idCliente.Bairro
        if len(endereco) > 45:
            pdf.drawString(
                convertemp(11),
                convertemp(242),
                "ENDEREÇO: " + endereco[0:45] + "...",
            )
        else:
            pdf.drawString(
                convertemp(11),
                convertemp(242),
                "ENDEREÇO: "
                + minuta.idCliente.Endereco
                + " - "
                + minuta.idCliente.Bairro,
            )
        pdf.drawString(
            convertemp(27),
            convertemp(238),
            minuta.idCliente.Cidade
            + " - "
            + minuta.idCliente.Estado
            + " - "
            + minuta.idCliente.CEP,
        )
        pdf.drawString(
            convertemp(11),
            convertemp(234),
            "INSCRIÇÃO CNPJ:" + minuta.idCliente.CNPJ,
        )
        pdf.drawString(
            convertemp(11),
            convertemp(230),
            "INSCRIÇÃO ESTADUAL: " + minuta.idCliente.IE,
        )
        if contato:
            pdf.drawString(
                convertemp(11),
                convertemp(226),
                "CONTATO: " + contato[0].Contato,
            )
            pdf.drawString(
                convertemp(11), convertemp(222), "TELEFONE: " + contato[0].Fone
            )
        # ----
        pdf.line(
            convertemp(105), convertemp(249), convertemp(105), convertemp(217)
        )
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(105),
            convertemp(249),
            convertemp(95),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(152.5), convertemp(250.3), "DADOS DO SERVIÇO SOLICITADO"
        )
        # ----
        pdf.setFont("Times-Roman", 8)
        y = 250
        if minuta.idCategoriaVeiculo:
            y -= 4
            pdf.drawString(
                convertemp(106),
                convertemp(y),
                "VEÍCULO: {}".format(minuta.idCategoriaVeiculo),
            )
            if veiculo:
                pdf.drawRightString(
                    convertemp(199), convertemp(y), "PLACA: {}".format(veiculo)
                )
        if motorista:
            y -= 4
            pdf.drawString(
                convertemp(106),
                convertemp(y),
                "MOTORISTA: {}".format(motorista),
            )
        if ajudante:
            if ajudante.count() == 1:
                y -= 4
                pdf.drawString(
                    convertemp(106),
                    convertemp(y),
                    "AJUDANTE: {}".format(ajudante[0].idPessoal),
                )
            else:
                for x in range(ajudante.count()):
                    y -= 4
                    if x == 0:
                        pdf.drawString(
                            convertemp(106),
                            convertemp(y),
                            str(ajudante.count())
                            + " AJUDANTES: "
                            + str(ajudante[x].idPessoal),
                        )
                    else:
                        pdf.drawString(
                            convertemp(126),
                            convertemp(y),
                            str(ajudante[x].idPessoal),
                        )
        if minuta.KMInicial:
            y -= 4
            pdf.drawString(
                convertemp(106),
                convertemp(y),
                "KM Inicial: " + str(minuta.KMInicial),
            )
        y -= 4
        pdf.drawString(
            convertemp(106),
            convertemp(y),
            "HORA INICIAL: " + minuta.HoraInicial.strftime("%H:%M"),
        )
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(212),
            convertemp(95),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(57.5),
            convertemp(213.3),
            "DESCRIÇÃO DO SERVIÇO EXECUTADO",
        )
        # ----
        pdf.line(
            convertemp(105), convertemp(212), convertemp(105), convertemp(172)
        )
        # TODO Excluido custo operacional da minuta 18/09/2020
        # pdf.setFont("Times-Roman", 10)
        # pdf.setFillColor(HexColor("#c1c1c1"))
        # pdf.rect(convertemp(105), convertemp(212), convertemp(95), convertemp(5), fill=1)
        # pdf.setFillColor(HexColor("#000000"))
        # pdf.drawCentredString(convertemp(152.5), convertemp(213.3), 'CUSTO OPERACIONAL')
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(167),
            convertemp(190),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(105), convertemp(168.3), "DESCRIÇÃO DOS SERVIÇOS"
        )
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(87),
            convertemp(190),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(105), convertemp(88.3), "LOCAIS DE ENTREGAS E COLETAS"
        )
        pdf.setFont("Times-Roman", 8)
        entregacoleta = ""
        if minuta.Entrega and minuta.Coleta:
            entregacoleta = (
                "ENTREGA: " + minuta.Entrega + " - COLETA: " + minuta.Coleta
            )
        elif minuta.Entrega:
            entregacoleta = "ENTREGA: " + minuta.Entrega
        elif minuta.Coleta:
            entregacoleta = "COLETA: " + minuta.Coleta
        if len(entregacoleta) > 115:
            wrap_entcol = wrap(entregacoleta, width=115)
            y = 87.4
            for linha in range(len(wrap_entcol)):
                if linha == 4:
                    break
                y -= 3
                pdf.drawString(
                    convertemp(11), convertemp(y), wrap_entcol[linha]
                )
        else:
            pdf.drawString(convertemp(11), convertemp(84.4), entregacoleta)
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(69),
            convertemp(190),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(105), convertemp(70.3), "OBSERVAÇÕES")
        pdf.setFont("Times-Roman", 8)
        observ = minuta.Obs
        if len(observ) > 115:
            wrap_obs = wrap(observ, width=115)
            y = 69.4
            for linha in range(len(wrap_obs)):
                if linha == 4:
                    break
                y -= 3
                pdf.drawString(convertemp(11), convertemp(y), wrap_obs[linha])
        else:
            pdf.drawString(convertemp(11), convertemp(66.4), observ)
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(
            convertemp(10),
            convertemp(51),
            convertemp(190),
            convertemp(5),
            fill=1,
        )
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(
            convertemp(105), convertemp(52.3), "KILOMETRAGEM"
        )
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(convertemp(11), convertemp(45.5), "KM INICIAL: ")
        pdf.drawString(convertemp(106), convertemp(45.5), "KM FINAL: ")
        # ----
        pdf.line(
            convertemp(10), convertemp(43), convertemp(200), convertemp(43)
        )
        # ----
        pdf.roundRect(
            convertemp(12), convertemp(12), convertemp(101), convertemp(19), 3
        )
        pdf.setFont("Times-Roman", 7)
        textominuta = (
            "A TRANSEFETIVA TRANSPORTE - EIRELI - ME, só se responsabilizará pela mercadoria que o\ncliente"
            " pagar seguro antes da mesma ser carregada. A responsabilidade da mercadoria e demais en-\ncargos"
            " nela contida é unicamente do cliente. É de responsábilidade do cliente MULTAS DE TRAN-\nSITO e"
            " outros encargos que podem ser cobrados, devido as restrições de horário e locais de entrega.\n"
            "Reconheço estar de pleno acordo com o serviço executado e dos dados informados, não tendo"
            " recla-\nmações posteriores à assinatura deste documento."
        )
        textobject = pdf.beginText(convertemp(13), convertemp(28))
        for line in textominuta.splitlines(False):
            textobject.textLine(line.rstrip())
        pdf.drawText(textobject)
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.line(
            convertemp(118), convertemp(15), convertemp(194), convertemp(15)
        )
        pdf.drawString(
            convertemp(118),
            convertemp(12),
            "DATA, ASSINATURA E CARIMBO DO CLIENTE",
        )
        # Close the PDF object cleanly.
        pdf.setTitle("Minuta.pdf")
        pdf.showPage()
        pdf.save()
        # Get the value of the BytesIO buffer and write it to the response.
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    else:
        return redirect("consultaminuta", idmin)


def estorna_minuta(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if minuta.StatusMinuta == "ABERTA":
        pass
    elif minuta.StatusMinuta == "CONCLUIDA":
        altera_status_minuta("ABERTA", idmin)
    elif minuta.StatusMinuta == "FECHADA":
        altera_status_minuta("ABERTA", idmin)
        itens_minuta_recebe_excluir = MinutaItens.objects.filter(
            idMinuta=idmin
        ).filter(TipoItens="RECEBE")
        for itens in itens_minuta_recebe_excluir:
            excluiminutaitens(itens.idMinutaItens)
        itens_minuta_paga_excluir = MinutaItens.objects.filter(
            idMinuta=idmin
        ).filter(RecebePaga="P")
        for itens in itens_minuta_paga_excluir:
            excluiminutaitens(itens.idMinutaItens)
    return redirect("consultaminuta", idmin)


def editaminutaveiculo(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == "POST":
        form = CadastraMinutaVeiculo(request.POST)
        if form.is_valid():
            km_inicial = kmfinal_veiculo(form.cleaned_data["Veiculo"])
            if not km_inicial:
                km_inicial = 0
            obj = Minuta()
            obj.idMinuta = form.cleaned_data["idMinuta"]
            obj.Minuta = minuta.Minuta
            obj.DataMinuta = minuta.DataMinuta
            obj.HoraInicial = minuta.HoraInicial
            obj.HoraFinal = minuta.HoraFinal
            obj.Coleta = minuta.Coleta
            obj.Entrega = minuta.Entrega
            obj.KMInicial = km_inicial
            obj.KMFinal = minuta.KMFinal
            obj.Obs = minuta.Obs
            obj.StatusMinuta = minuta.StatusMinuta
            obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
            obj.idCliente = minuta.idCliente
            obj.idVeiculo_id = form.cleaned_data["Veiculo"]
            obj.save()
    else:
        form = CadastraMinutaVeiculo(
            initial={"idMinuta": idmin, "Veiculo": minuta.idVeiculo_id}
        )
    return salva_form(request, form, "minutas/editaminutaveiculo.html", idmin)


def criaminutaentrega(request):
    if request.method == "POST":
        idminuta = request.POST.get("idMinuta")
        form = CadastraMinutaNota(idminuta, request.POST)
    else:
        idminuta = request.GET.get("idminuta")
        form = CadastraMinutaNota(idminuta, initial={"idMinuta": idminuta})
    return salva_form(
        request, form, "minutas/criaminutaentrega.html", idminuta
    )


def editaminutaentrega(request, idminent):
    notaminuta = get_object_or_404(MinutaNotas, idMinutaNotas=idminent)
    data = dict()
    if request.method == "POST":
        form = CadastraMinutaNota(
            notaminuta.idMinuta_id, request.POST, instance=notaminuta
        )
        if form.is_valid():
            form.save()
        return redirect("consultaminuta", notaminuta.idMinuta_id)
    else:
        form = CadastraMinutaNota(notaminuta.idMinuta_id, instance=notaminuta)
        context = {
            "form": form,
            "numerominuta": request.GET.get("idminuta"),
            "idminent": idminent,
        }
        data["html_form"] = render_to_string(
            "minutas/editaminutaentrega.html", context, request=request
        )
    return JsonResponse(data)


def excluiminutaentrega(request, idminent):
    notaminuta = get_object_or_404(MinutaNotas, idMinutaNotas=idminent)
    data = dict()
    if request.method == "POST":
        notaminuta.delete()
        return redirect("consultaminuta", notaminuta.idMinuta_id)
    else:
        context = {"notaminuta": notaminuta}
        data["html_form"] = render_to_string(
            "minutas/excluiminutaentrega.html", context, request=request
        )
    return JsonResponse(data)


def buscaminutaentrega(request):
    nota_guia = MinutaNotas.objects.filter(
        idMinuta_id=request.GET.get("id_minuta"),
        Nota=request.GET.get("nota_guia"),
    )
    nota_guia_nome = list(nota_guia.values("Nome")[0].values())[0]
    nota_guia_cidade = list(nota_guia.values("Cidade")[0].values())[0]
    nota_guia_estado = list(nota_guia.values("Estado")[0].values())[0]
    data = {
        "nota_guia_nome": nota_guia_nome,
        "nota_guia_cidade": nota_guia_cidade,
        "nota_guia_estado": nota_guia_estado,
    }
    return JsonResponse(data)


def filtraminutaveiculo(request):
    data = dict()
    propriedade = request.GET.get("propriedade")
    idminutamotoristacolaboradores = MinutaColaboradores.objects.filter(
        idMinutaColaboradores=request.GET.get("idminutacolaboradores")
    )
    idmotorista = idminutamotoristacolaboradores.values_list("idPessoal_id")[0]
    veiculo = ""
    if propriedade == "1":
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat(
                "Marca", Value(" - "), "Modelo", Value(" - "), "Placa"
            )
        ).filter(Motorista=idmotorista)
    elif propriedade == "2":
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat(
                "Marca", Value(" - "), "Modelo", Value(" - "), "Placa"
            )
        ).filter(Motorista=17)
    elif propriedade == "3":
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat(
                "Marca", Value(" - "), "Modelo", Value(" - "), "Placa"
            )
        ).all()
    listaveiculo = []
    for x in veiculo:
        listaveiculo.append(x)
    context = {"listaveiculo": listaveiculo}
    data["html_form"] = render_to_string(
        "minutas/editaminutaveiculolista.html", context, request=request
    )
    return JsonResponse(data)


def edita_comentario(request, idmin):
    minuta = Minuta.objects.get(idMinuta=idmin)
    form = ""
    if request.method == "POST":
        form = CadastraComentarioMinuta(request.POST, instance=minuta)
    return salva_form(request, form, "minutas/consultaminuta.html", idmin)


def salva_form(request, form, template_name, idmin):
    data = dict()
    numerominuta = 0
    numeroidminuta = idmin
    if template_name != "minutas/editaminutaveiculo.html":
        numeroidminuta = form.instance
    if request.method == "POST":
        if form.is_valid():
            data["form_is_valid"] = True
            if template_name != "minutas/editaminutaveiculo.html":
                form.save()
            if template_name == "minutas/criaminuta.html":
                return redirect("consultaminuta", numeroidminuta.idMinuta)
            else:
                return redirect("consultaminuta", idmin)
        else:
            return redirect("consultaminuta", idmin)
    context = {
        "form": form,
        "numerominuta": numerominuta,
        "numeroidminuta": numeroidminuta,
    }
    data["html_form"] = render_to_string(
        template_name, context, request=request
    )
    return JsonResponse(data)


def estorna_pagamentos(request):
    c_idminuta = request.GET.get("idMinuta")
    estorna_paga(c_idminuta)
    data = dict()
    data["html_idminuta"] = request.GET.get("idMinuta")
    return JsonResponse(data)


def filtra_minuta(request):
    c_filtro = request.GET.get("Filtro")
    c_filtro_consulta = request.GET.get("FiltroConsulta")
    c_meses = request.GET.get("Meses")
    c_anos = request.GET.get("Anos")
    data = filtra_consulta(
        request, c_filtro, c_filtro_consulta, c_meses, c_anos
    )
    return data


def edita_minuta(request):
    c_form = FormMinuta
    c_idobj = None
    if request.method == "GET":
        c_idobj = request.GET.get("idobj")
    elif request.method == "POST":
        c_idobj = request.POST.get("idMinuta")
    c_url = "/minutas/editaminuta/"
    c_view = "edita_minuta"
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_minuta_saida_extra_ajudante(request, idminuta):
    minutanotas = MinutaNotas.objects.filter(idMinuta=idminuta)
    for itens in minutanotas:
        obj = itens
        obj.ExtraValorAjudante = request.POST.get("ExtraValorAjudante")
        obj.save(update_fields=["ExtraValorAjudante"])
    return redirect("consultaminuta", idminuta)


def remove_minuta_colaborador(request):
    c_idobj = request.GET.get("idMinutaColaboradores")
    c_idminuta = request.GET.get("idMinuta")
    c_cargo = request.GET.get("Cargo")
    data = remove_colaborador(request, c_idobj, c_idminuta, c_cargo)
    data = retorna_json(data)
    return data


def insere_minuta_despesa(request):
    c_form = FormInsereDespesa
    c_idobj = None
    if request.method == "GET":
        c_idobj = request.GET.get("idobj")
    elif request.method == "POST":
        c_idobj = request.POST.get("idMinuta")
    c_url = "/minutas/inseredespesa/"
    c_view = "insere_minuta_despesa"
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def remove_minuta_despesa(request):
    c_idobj = request.GET.get("idMinutaItens")
    c_idminuta = request.GET.get("idMinuta")
    data = remove_despessa(request, c_idobj, c_idminuta)
    data = retorna_json(data)
    return data


def insere_minuta_entrega(request):
    c_form = FormInsereEntrega
    c_idobj = None
    if request.method == "GET":
        c_idobj = request.GET.get("idobj")
    elif request.method == "POST":
        c_idobj = request.POST.get("idMinuta")
    c_url = "/minutas/insereentrega/"
    c_view = "insere_minuta_entrega"
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def remove_minuta_entrega(request):
    c_idobj = request.GET.get("idMinutaNotas")
    c_idminuta = request.GET.get("idMinuta")
    data = remove_entrega(request, c_idobj, c_idminuta)
    data = retorna_json(data)
    return data


def adiciona_romaneio_minuta(request):
    idromaneio = request.GET.get("idromaneio")
    idminuta = request.GET.get("idminuta")
    idcliente = request.GET.get("idcliente")
    facade.save_notas_romaneio_minuta(idromaneio, idminuta)
    contexto = facade.create_contexto_minuta_selecionada(idminuta)
    romaneios = facade.create_contexto_romaneios(idcliente)
    contexto.update({"romaneios": romaneios, "idminuta": idminuta})
    data = facade.create_data_entrega_romaneio_minuta(request, contexto)
    return data


def remove_romaneio_minuta(request):
    numero_romaneio = request.GET.get("romaneio")
    idminuta = request.GET.get("idminuta")
    idcliente = request.GET.get("idcliente")
    facade.remove_numero_romaneio_minuta(numero_romaneio, idminuta)
    contexto = facade.create_contexto_minuta_selecionada(idminuta)
    romaneios = facade.create_contexto_romaneios(idcliente)
    contexto.update({"romaneios": romaneios, "idminuta": idminuta})
    data = facade.create_data_entrega_romaneio_minuta(request, contexto)
    return data


def gera_receitas(request):
    idminuta = request.POST.get("idminuta")
    facade.gera_itens_receitas(request)
    contexto = facade.create_contexto_minuta(idminuta)
    data = {}
    data = facade.create_html_card_recebe(data, contexto, request)
    return JsonResponse(data)


def gera_pagamentos(request):
    idminuta = request.POST.get("idminuta")
    pagamento_de = request.POST.get("pagamento")
    if pagamento_de == "AJUDANTE":
        facade.gera_itens_pagamento_ajudantes(request)
    elif pagamento_de == "MOTORISTA":
        facade.gera_itens_pagamento_motorista(request)
    contexto = facade.cria_contexto(idminuta)
    contexto.update({"idminuta": idminuta})
    data = facade.create_data_gera_pagamentos_ajudantes(request, contexto)
    return data


def estorna_pagamentos_ajudantes(request):
    idminuta = request.GET.get("idminuta")
    facade.exclui_pagamentos_ajudantes(idminuta)
    contexto = facade.cria_contexto(idminuta)
    contexto.update({"idminuta": idminuta})
    data = facade.create_data_exclui_pagamentos_ajudantes(request, contexto)
    return data


def estorna_pagamentos_motorista(request):
    idminuta = request.GET.get("idminuta")
    facade.exclui_pagamentos_motorista(idminuta)
    contexto = facade.cria_contexto(idminuta)
    contexto.update({"idminuta": idminuta})
    data = facade.create_data_exclui_pagamentos_ajudantes(request, contexto)
    return data


def estorna_minuta_concluida(request):
    idminuta = request.GET.get("idminuta")
    proximo_status = request.GET.get("proximo_status")
    facade.define_novo_status_minuta(idminuta, proximo_status)
    contexto = facade.cria_contexto(idminuta)
    contexto.update({"idminuta": idminuta})
    data = facade.create_data_minuta_checklist_pagamentos(request, contexto)
    return data


def minutas_periodo(request):
    inicial = request.GET.get("inicial")
    final = request.GET.get("final")
    idcliente = int(request.GET.get("cliente"))
    contexto = facade.create_contexto_minutas_periodo(
        inicial, final, idcliente
    )
    contexto.update({"inicial": inicial, "final": final})
    response = print_minutas_periodo(contexto)
    return response


def minuta_cards(request):
    """
        Criada: 15/07/2024
        Requisita o contexto da minuta selecionada e o data (html) que será
        retornado com JsonResponse. Mostrando os detalhes da minuta em cards
        separados.
    Args:
        request: GET - idminuta

    Returns:
        data JsonResponse

    """
    idminuta = request.GET.get("idminuta")
    contexto = facade.create_contexto_minuta(idminuta)
    data = facade.create_data_minuta(request, contexto)
    return data


def estorna_faturamento(request):
    idminuta = request.GET.get("idminuta")
    facade.estorna_minutaitens_recebe(idminuta)
    contexto = facade.create_contexto_minuta(idminuta)
    data = {}
    data = facade.create_html_card_recebe(data, contexto, request)
    return JsonResponse(data)


# Código verificado a partir de 31/07/2024
def handle_modal_minuta(request, modal_func, update_func):
    """
    Manipula a adição ou modificação de informações em uma minuta com
    base em uma solicitação GET ou POST.
    Itens do card minuta que usam modal.

    Args:
        request: O objeto de solicitação HTTP.
        modal_func: Função para renderizar o modal.
        update_func: Função para atualizar o item.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    id_minuta = request.POST.get("id_minuta") or request.GET.get("idobj")

    if request.method == "GET":
        return modal_func(id_minuta, request)
    if request.method == "POST":
        contexto = update_func(request)
        contexto.update(facade.contexto_minuta_alterada(id_minuta))

        return facade.data_minuta_alterada(request, contexto)

    return JsonResponse({"error": "Método não permitido"}, status=405)


def adicionar_veiculo_solicitado(request):
    """
    Adiciona um veículo solicitado à minuta.

    Args:
        request: O objeto de solicitação HTTP.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    return handle_modal_minuta(
        request,
        facade.modal_veiculo_solicitado,
        facade.update_veiculo_solicitado,
    )


def adicionar_motorista_minuta(request):
    """
    Adiciona um motorista à minuta.

    Args:
        request: O objeto de solicitação HTTP.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    return handle_modal_minuta(
        request,
        facade.modal_motorista_minuta,
        facade.update_motorista_minuta,
    )


def adicionar_veiculo_minuta(request):
    """
    Adiciona um veículo à minuta.

    Args:
        request: O objeto de solicitação HTTP.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    return handle_modal_minuta(
        request,
        facade.modal_veiculo_minuta,
        facade.update_veiculo_minuta,
    )


def adicionar_ajudante_minuta(request):
    """
    Adiciona um ajudante à minuta.

    Args:
        request: O objeto de solicitação HTTP.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    return handle_modal_minuta(
        request,
        facade.modal_ajudante_minuta,
        facade.update_ajudante_minuta,
    )


def editar_informacoes_minuta(request):
    """
    Edita as informações de uma minuta.

    Args:
        request: O objeto de solicitação HTTP.

    Returns:
        JsonResponse: Dados atualizados ou modal renderizado.
    """
    return handle_modal_minuta(
        request,
        facade.modal_informacoes_minuta,
        facade.update_informacoes_minuta,
    )


def handle_input_minuta(request, update_func):
    """
    Manipula a modificação de propriedades de uma minuta com base em uma
    solicitação GET.

    Args:
        request: O objeto de solicitação HTTP GET.
        update_func: Função para atualizar o item da minuta.

    Returns:
        JsonResponse: Dados atualizados da minuta.
    """
    id_minuta = request.GET.get("id_minuta")

    contexto = update_func(request)
    contexto.update(facade.contexto_minuta_alterada(id_minuta))

    return facade.data_minuta_alterada(request, contexto)


def editar_minuta_hora_final(request):
    """
    Edita a hora final de uma minuta.

    Args:
        request: O objeto de solicitação HTTP GET contendo o ID da minuta.

    Returns:
        JsonResponse: Dados atualizados da minuta com a hora final editada.
    """
    return handle_input_minuta(request, facade.edita_hora_final)


def editar_minuta_km_inicial(request):
    """
    Edita a quilometragem inicial de uma minuta.

    Args:
        request: O objeto de solicitação HTTP GET contendo o ID da minuta.

    Returns:
        JsonResponse: Dados atualizados da minuta com a quilometragem inicial
        editada.
    """
    return handle_input_minuta(request, facade.editar_km_inicial)


def editar_minuta_km_final(request):
    """
    Edita a quilometragem final de uma minuta.

    Args:
        request: O objeto de solicitação HTTP GET contendo o ID da minuta.

    Returns:
        JsonResponse: Dados atualizados da minuta com a quilometragem final
        editada.
    """
    return handle_input_minuta(request, facade.editar_km_final)


def excluir_colaborador_minuta(request):
    """
    Exclui um colaborador (motorista ou ajudante) de uma minuta.

    Args:
        request: O objeto de solicitação HTTP GET contendo os parâmetros
                 necessários.
                 - "id_minuta": O ID da minuta.
                 - "cargo": O cargo do colaborador ("MOTORISTA" ou outro).

    Returns:
        JsonResponse: Dados atualizados da minuta após a exclusão do
                      colaborador.
    """
    id_minuta = request.GET.get("id_minuta")
    cargo = request.GET.get("cargo")

    if cargo == "MOTORISTA":
        facade.excluir_veiculo_minuta(id_minuta)

    contexto = facade.excluir_colaborador(request)
    contexto.update(facade.contexto_minuta_alterada(id_minuta))

    return facade.data_minuta_alterada(request, contexto)


def filtra_minuta_veiculo_escolhido(request):
    """
    Filtra veículos com base em uma das opções fornecidas e retorna
    os resultados filtrados.

    Args:
        request: O objeto de solicitação HTTP GET contendo os parâmetros
                 de filtragem.
                 - "idPessoal": O ID da pessoa.
                 - "Filtro": O filtro a ser aplicado ("PRÓPRIO",
                 "TRANSPORTADORA", ou "CADASTRADOS").

    Returns:
        JsonResponse: Dados dos veículos filtrados.
    """
    idpessoal = request.GET.get("idPessoal")
    opcao = request.GET.get("Filtro")

    veiculos = facade.filtra_veiculo(idpessoal, opcao)

    return facade.html_filtro_veiculo(request, veiculos)


def adicionar_minuta(request):
    """
    Processa a requisição para adicionar uma minuta.

    Se o método da requisição for GET, renderiza o modal de minuta.
    Se o método for diferente de GET (presumivelmente POST), salva a minuta.

    Args:
        request (HttpRequest): O objeto HttpRequest contendo os dados da
        requisição.

    Returns:
        JsonResponse: O resultado da operação, dependendo do método da
        requisição.
    """
    if request.method == "GET":
        return facade.modal_minuta(id_minuta=None, request=request)
    return facade.salvar_minuta(request)


def editar_minuta(request):
    """
    Gerencia a edição de uma minuta, utilizando um modal para exibir e
    atualizar dados.

    Args:
        request (HttpRequest): Objeto de requisição HTTP com os dados
        necessários para a edição.

    Returns:
        HttpResponse: Resposta HTTP gerada pela função handle_modal_minuta.
    """
    return handle_modal_minuta(
        request, facade.modal_minuta, facade.atualizar_minuta
    )


def adicionar_despesa(request):
    """
    Gerencia a adição de uma despesa a uma minuta, utilizando um modal
    para exibir e salvar dados.

    Args:
        request (HttpRequest): Objeto de requisição HTTP com os dados
        necessários para adicionar a despesa.

    Returns:
        HttpResponse: Resposta HTTP gerada pela função handle_modal_minuta.
    """
    return handle_modal_minuta(
        request,
        facade.renderizar_modal_despesas_minuta,
        facade.salvar_ou_atualizar_despesa_minuta,
    )


def excluir_despesa(request):
    """
    Gerencia a exclusão de uma despesa associada a uma minuta e atualiza
    o contexto da minuta.

    Args:
        request (HttpRequest): Objeto de requisição HTTP com os dados
        necessários para excluir a despesa.

    Returns:
        HttpResponse: Resposta HTTP gerada pela função data_minuta_alterada.
    """
    id_minuta = request.GET.get("id_minuta")
    id_minuta_itens = request.GET.get("id_minuta_itens")

    contexto = facade.deletar_despesa_minuta(id_minuta_itens)
    contexto.update(facade.contexto_minuta_alterada(id_minuta))

    return facade.data_minuta_alterada(request, contexto)


def alterar_status_minuta(request):
    """
    Altera o status de uma minuta e atualiza o contexto com as novas
    informações.

    Args:
        request (HttpRequest): Objeto de requisição HTTP contendo os
        parâmetros da minuta e do próximo status.

    Returns:
        HttpResponse: Resposta HTTP gerada pela função data_minuta_alterada,
        com o contexto atualizado.
    """
    id_minuta = request.GET.get("id_minuta")
    proximo_status = request.GET.get("proximo_status")
    contexto = novo_status_minuta(id_minuta, proximo_status)
    contexto.update(facade.contexto_minuta_alterada(id_minuta))

    return facade.data_minuta_alterada(request, contexto)
