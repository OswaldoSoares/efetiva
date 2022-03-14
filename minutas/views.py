from io import BytesIO
from textwrap import wrap
from django.db.models import Value, Sum, Max, F
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.shortcuts import redirect, get_object_or_404, get_list_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from django.templatetags.static import static
from django.urls import reverse
from rolepermissions.decorators import has_permission_decorator
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta, time
import json
from decimal import Decimal
from clientes.models import FoneContatoCliente, Tabela, TabelaVeiculo, TabelaCapacidade, TabelaPerimetro
from minutas.facade import MinutaSelecionada, MinutaEntrega, MinutaDespesa
from veiculos.models import Veiculo
from .forms import FormInsereColaborador, FormEditaVeiculoSolicitado, FormEditaVeiculoEscolhido, \
    FormColetaEntregaObs, FormInsereDespesa, FormInsereEntrega, CadastraMinuta, \
    CadastraMinutaMotorista, CadastraMinutaAjudante, CadastraMinutaVeiculo, CadastraMinutaKMInicial, \
    CadastraMinutaKMFinal, CadastraMinutaHoraFinal, CadastraMinutaDespesa, CadastraMinutaParametroDespesa, \
    CadastraMinutaNota, CadastraComentarioMinuta, CadastraMinutaSaidaExraAjudante, FormMinuta
from .models import Minuta, MinutaColaboradores, MinutaItens, MinutaNotas
from .facade import forn_minuta, edita_hora_final, filtra_veiculo, html_filtro_veiculo, edita_km_final, \
    edita_km_inicial, \
    remove_colaborador, remove_despessa, remove_entrega, retorna_json, prepara_itens, estorna_paga, \
    novo_status_minuta, MinutasStatus, filtro_clientes, filtro_colaboradores, filtro_veiculos, filtro_cidades, \
    filtra_consulta

def convertemp(mm):
    """
    Converte milimetros em pontos - Criação de Relatórios

    :param mm: milimetros
    :return: pontos
    """
    return mm / 0.352777


def horascobra(horai, horaf, datam, horam):
    horainicial = horai
    horafinal = horaf
    dataminuta = datam
    minimohoras = timedelta(days=0, hours=horam.hour, minutes=horam.minute)
    excedehoras = timedelta(days=0, hours=0, minutes=0)
    totalhoras = timedelta(days=0, hours=0, minutes=0)
    if horainicial != horafinal:
        datainicial = datetime.combine(dataminuta, horainicial)
        if horainicial < horafinal:
            datafinal = datetime.combine(dataminuta, horafinal)
            totalhoras = datafinal - datainicial
        else:
            dataminuta = dataminuta + timedelta(days=1)
            datafinal = datetime.combine(dataminuta, horafinal)
            totalhoras = datafinal - datainicial
    if totalhoras > minimohoras:
        excedehoras = totalhoras - minimohoras
    return totalhoras, minimohoras, excedehoras


def parametrominutadespesa():
    # arquivo_json = open('', 'r')
    # dados_json = json.load(arquivo_json)
    # arquivo_json.close()
    # despesas = dados_json['Despesa']['Descricao']
    # despesas.sort()
    # return despesas
    # TODO removido arquivo parametro, criado banco de dados, remover view
    pass


def salvaminutaitens(descricao, tipoitens, recebepaga, valor, quantidade, porcento, peso, valorbase, tempo, idminuta):
    """
    Função para inserir e atualizar um item da minuta

    :param descricao:
    :param tipoitens:
    :param recebepaga:
    :param valor:
    :param quantidade:
    :param porcento:
    :param peso:
    :param valorbase:
    :param tempo:
    :param idminuta:
    :return:
    """
    minutaitens = MinutaItens.objects.filter(idMinuta=idminuta, Descricao=descricao, RecebePaga=recebepaga,
                                             TipoItens=tipoitens)
    hora_datetime = datetime.strptime(tempo, '%H:%M')
    hora_timedelta = timedelta(days=0, hours=hora_datetime.hour, minutes=hora_datetime.minute)
    obj = MinutaItens()
    if minutaitens:
        obj.idMinutaItens = list(minutaitens.values('idMinutaItens')[0].values())[0]
    obj.Descricao = descricao
    obj.TipoItens = tipoitens
    obj.RecebePaga = recebepaga
    obj.Valor = valor
    obj.Quantidade = quantidade
    obj.Porcento = porcento
    obj.Peso = peso
    obj.ValorBase = valorbase
    obj.Tempo = hora_timedelta
    obj.idMinuta_id = idminuta
    obj.Obs = ''
    obj.save()
    return True


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
    veiculo = Minuta.objects.filter(idVeiculo=idveiculo).aggregate(Max('KMFinal'))
    kmfinal = [item for item in veiculo.values()]
    return kmfinal[0]


@has_permission_decorator('modulo_minutas')
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
    aberta = ''
    m_aberta = MinutasStatus('ABERTA').minutas
    t_aberta = len(m_aberta)
    m_concluida = MinutasStatus('CONCLUIDA').minutas
    t_concluida = len(m_concluida)
    m_fechada = MinutasStatus('FECHADA').minutas
    t_fechada = len(m_fechada)
    filtro_cliente = filtro_clientes()
    filtro_colaborador = filtro_colaboradores()
    filtro_veiculo = filtro_veiculos()
    filtro_cidade = filtro_cidades()
    faturada = Minuta.objects.filter(StatusMinuta='FATURADA')
    meu_filtro_minuta = request.GET.get('filtrominuta')
    meu_filtro_status = request.GET.get('filtrostatus')
    if meu_filtro_minuta:
        minuta = Minuta.objects.filter(Minuta=meu_filtro_minuta)
    elif meu_filtro_status:
        if meu_filtro_status == 'CONCLUIDA':
            minuta = Minuta.objects.filter(StatusMinuta=meu_filtro_status)
        else:
            minuta = Minuta.objects.filter(StatusMinuta=meu_filtro_status).order_by('-Minuta')
    else:
        minuta = Minuta.objects.filter(StatusMinuta='ABERTA').values()
    minuta_status = Minuta.objects.all().values_list('StatusMinuta', flat=True)
    minuta_status = sorted(list(dict.fromkeys(minuta_status)))
    minutacolaboradores = MinutaColaboradores.objects.filter(Cargo='MOTORISTA')
    return render(request, 'minutas/index.html', {'m_aberta': m_aberta, 'm_concluida': m_concluida,
                                                  'm_fechada': m_fechada, 't_aberta': t_aberta,
                                                  't_concluida': t_concluida, 't_fechada': t_fechada,
                                                  'filtro_cliente': filtro_cliente,
                                                  'filtro_colaborador': filtro_colaborador,
                                                  'filtro_veiculo': filtro_veiculo, 'filtro_cidade': filtro_cidade,
                                                  'faturada': faturada, 'minuta': minuta,
                                                  'minuta_status': minuta_status,
                                                  'minutacolaboradores': minutacolaboradores})


def consultaminuta(request, idmin):
    # Cria queryset obj minuta - motorista - ajudante - ajudante quantidade
    minuta = Minuta.objects.filter(idMinuta=idmin)
    motorista_da_minuta = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='MOTORISTA').annotate(
        TipoPgto=F('idPessoal__TipoPgto'))
    ajudantes_da_minuta = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='AJUDANTE').annotate(
        TipoPgto=F('idPessoal__TipoPgto'))
    total_de_ajudantes = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='AJUDANTE').count()
    itens_paga_motorista = MinutaItens.objects.filter(idMinuta=idmin, TipoItens='PAGA').exclude(Descricao='AJUDANTE')
    soma_paga_motorista = str(sum([i['Valor'] for i in itens_paga_motorista.values('Valor')]))
    # Cria variaveis idcliente - idcategoriaveiculo - horainicial - horafinal - dataminuta
    idcliente = list(minuta.values('idCliente')[0].values())[0]
    idcategoriaveiculo = list(minuta.values('idCategoriaVeiculo')[0].values())[0]
    horainicial = list(minuta.values('HoraInicial')[0].values())[0]
    horafinal = list(minuta.values('HoraFinal')[0].values())[0]
    dataminuta = list(minuta.values('DataMinuta')[0].values())[0]
    # cria queryset obj tabela cliente
    tabelacliente = Tabela.objects.filter(idCliente=idcliente)
    # Cria variavel phksec de cobrança - taxa expedição - valor ajudante
    phkescrecebe = list(tabelacliente.values('phkescCobra')[0].values())[0]
    phkescpaga = list(tabelacliente.values('phkescPaga')[0].values())[0]
    valortaxaexpedicao = list(tabelacliente.values('TaxaExpedicao')[0].values())[0]
    valorajudanterecebe = list(tabelacliente.values('AjudanteCobra')[0].values())[0]
    valor_ajudante_recebe_hora_extra = list(tabelacliente.values('AjudanteCobraHoraExtra')[0].values())[0]
    valorajudantepaga = list(tabelacliente.values('AjudantePaga')[0].values())[0]
    # Cria queryset obj tabela veículo
    tabelaveiculo = TabelaVeiculo.objects.filter(idCliente=idcliente, idCategoriaVeiculo=idcategoriaveiculo)
    inicialkm = list(minuta.values('KMInicial')[0].values())[0]
    finalkm = list(minuta.values('KMFinal')[0].values())[0]
    totalkm = finalkm - inicialkm
    # Cria variaveis zerada
    totalhoras = timedelta(days=0, hours=0, minutes=0)
    minimohoras = 0.00
    excedehoras = 0.00
    valorporcentagemrecebe = 0.00
    valorporcentagempaga = 0.00
    valorhorarecebe = 0.00
    valorhorapaga = 0.00
    valorkmrecebe = 0.00
    valorkmpaga = 0.00
    minimokm = 0.00
    minimoentrega = 0.00
    valorsaidarecebe = 0.00
    valorsaidapaga = 0.00
    valorcapacidaderecebe = 0.00
    valorcapacidadepaga = 0.00
    porceperimetrorecebe = 0.00
    porceperimetropaga = 0.00
    valorentrega_recebe = 0.00
    valorentregakg_recebe = 0.00
    valorentregavolume_recebe = 0.00
    valorentrega_paga = 0.00
    valorentregakg_paga = 0.00
    valorentregavolume_paga = 0.00
    porcesegurorecebe = 1.00
    porcepernoite = 100
    numero_saidas_do_ajudante = -1
    dezhoras = timedelta(days=0, hours=10, minutes=0)
    if tabelaveiculo:
        # Cria variavel horaminimo
        horaminimo = list(tabelaveiculo.values('HoraMinimo')[0].values())[0]
        # Cria variaveis totalhoras - minimohoras - excedehoras (Type timedelta) - geradas pela função horascobra
        totalhoras, minimohoras, excedehoras = horascobra(horainicial, horafinal, dataminuta, horaminimo)
        # Cria variaveis para demonstrativo
        valorporcentagemrecebe = list(tabelaveiculo.values('PorcentagemCobra')[0].values())[0]
        valorporcentagempaga = list(tabelaveiculo.values('PorcentagemPaga')[0].values())[0]
        valorhorarecebe = list(tabelaveiculo.values('HoraCobra')[0].values())[0]
        valorhorapaga = list(tabelaveiculo.values('HoraPaga')[0].values())[0]
        valorkmrecebe = list(tabelaveiculo.values('KMCobra')[0].values())[0]
        valorkmpaga = list(tabelaveiculo.values('KMPaga')[0].values())[0]
        valorentrega_recebe = list(tabelaveiculo.values('EntregaCobra')[0].values())[0]
        valorentregakg_recebe = list(tabelaveiculo.values('EntregaKGCobra')[0].values())[0]
        valorentregavolume_recebe = list(tabelaveiculo.values('EntregaVolumeCobra')[0].values())[0]
        valorentrega_paga = list(tabelaveiculo.values('EntregaPaga')[0].values())[0]
        valorentregakg_paga = list(tabelaveiculo.values('EntregaKGPaga')[0].values())[0]
        valorentregavolume_paga = list(tabelaveiculo.values('EntregaVolumePaga')[0].values())[0]
        minimokm = list(tabelaveiculo.values('KMMinimo')[0].values())[0]
        # TODO VALOR DA ENTREGA MUDOU PARA TABELA DE CLIENTE 03/10/2020
        # valorentrega = list(tabelaveiculo.values('EntregaCobra')[0].values())[0]
        # minimoentrega = list(tabelaveiculo.values('EntregaMinimo')[0].values())[0]
        valorsaidarecebe = list(tabelaveiculo.values('SaidaCobra')[0].values())[0]
        valorsaidapaga = list(tabelaveiculo.values('SaidaPaga')[0].values())[0]
        # Cria variavel dezhoras para verificar quantidade de digitos da
        # horas excedentes e minimo
        # Converte a hora excedente (teltatime em str) em horas e minutos
        # e segundos
        if excedehoras < dezhoras:
            horas = str(excedehoras)[0:1]
            minutos = str(excedehoras)[2:4]
        else:
            horas = str(excedehoras)[0:2]
            minutos = str(excedehoras)[3:5]
        strexcedehoras = horas + ':' + minutos + ':00'
        # Converte a hora minimo (teltatime em string) em horas e minutos e segundos
        if minimohoras < dezhoras:
            horas = str(minimohoras)[0:1]
            minutos = str(minimohoras)[2:4]
        else:
            horas = str(minimohoras)[0:2]
            minutos = str(minimohoras)[3:5]
        strminimohoras = horas + ':' + minutos + ':00'
        # Converte string minimo horas e excedente hora em datetime.time
        datetimeexcedehoras = datetime.strptime(strexcedehoras, '%H:%M:%S')
        excedehoras = datetimeexcedehoras.time()
        datetimeminimohoras = datetime.strptime(strminimohoras, '%H:%M:%S')
        minimohoras = datetimeminimohoras.time()
    # Cria queryset obj tabela perimetro
    tabelaperimetro = TabelaPerimetro.objects.filter(idCliente=idcliente)
    # Cria queryset obj tabela capacidade
    tabelacapacidade = TabelaCapacidade.objects.filter(idCliente=idcliente)
    # Recupera minuta e instancia os forms
    minutaform = get_object_or_404(minuta, idMinuta=idmin)
    formhorafinal = CadastraMinutaHoraFinal(instance=minutaform)
    formkminicial = CadastraMinutaKMInicial(instance=minutaform)
    formkmfinal = CadastraMinutaKMFinal(instance=minutaform)
    comentarios = list(minuta.values('Comentarios')[0].values())[0]
    formcomentarios = CadastraComentarioMinuta(initial={'idMinuta': '29', 'Comentarios': comentarios})
    # Cria queryset notas e dassomas
    notas_minuta = MinutaNotas.objects.filter(idMinuta=idmin).order_by('Nota')
    formsaidaextraajudante = CadastraMinutaSaidaExraAjudante()
    if notas_minuta:
        minutanotasform = get_list_or_404(notas_minuta)
        formsaidaextraajudante = CadastraMinutaSaidaExraAjudante(instance=minutanotasform[0])
    notas_minuta_guia = MinutaNotas.objects.filter(idMinuta=idmin, NotaGuia='0').order_by('Nota')
    notas_perimetro = MinutaNotas.objects.values('Cidade').filter(idMinuta=idmin).exclude(Cidade='SÃO PAULO')
    notas_bairro = MinutaNotas.objects.values('Bairro').filter(idMinuta=idmin).exclude(Bairro__isnull=True).exclude(
        Bairro__exact='')
    totalvalornotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalvalor=Sum('ValorNota'))
    totalpesonotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalpeso=Sum('Peso'))
    peso = totalpesonotas['totalpeso']
    totalvolumenotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalvolume=Sum('Volume'))
    totalquantidadenotas = MinutaNotas.objects.filter(idMinuta=idmin, NotaGuia='0').count()
    extra_valor_ajudante = MinutaNotas.objects.filter(idMinuta=idmin)
    if extra_valor_ajudante:
        numero_saidas_do_ajudante = extra_valor_ajudante[0].ExtraValorAjudante
        if numero_saidas_do_ajudante == 2:
            # TODO COLOCAR O VALOR DE 10 (R$ 10,00) COMO PARAMETRO 13/08/2021
            valorajudantepaga = valorajudantepaga + 10
    # Percorre a tabelacapacidade para localizar o peso
    if tabelacapacidade and peso:
        for x in tabelacapacidade:
            if peso >= x.CapacidadeInicial:
                if peso <= x.CapacidadeFinal:
                    valorcapacidaderecebe = x.CapacidadeCobra
                    valorcapacidadepaga = x.CapacidadePaga
                    break
    if notas_perimetro:
        # Percorre a tabelaperimetro para localizar a km
        for x in tabelaperimetro:
            if totalkm >= x.PerimetroInicial:
                if totalkm <= x.PerimetroFinal:
                    porceperimetrorecebe = x.PerimetroCobra
                    porceperimetropaga = x.PerimetroPaga
                    break
    formhoracobra = ''
    formhoraexcede = ''
    despesas = parametrominutadespesa()
    itensminuta = MinutaItens.objects.filter(idMinuta=idmin, TipoItens='DESPESA').order_by('Descricao')
    veiculo = ''
    idveiculo = list(minuta.values('idVeiculo')[0].values())[0]
    ajudantes_mensalistas = 0
    for itens in ajudantes_da_minuta:
        if itens.TipoPgto == 'MENSALISTA':
            ajudantes_mensalistas += 1
    ajudantes_paga = total_de_ajudantes - ajudantes_mensalistas
    if motorista_da_minuta:
        veiculo = Veiculo.objects.filter(idVeiculo=idveiculo)
    minuta_itens_fechada = MinutaItens.objects.filter(idMinuta=idmin).order_by('TipoItens', 'Descricao')
    " ADICIONA VALOR HORA EXTRA NA COBRANÇA DO AJUDANTE "
    calcula_ajudante_recebe_hora_extra = Decimal(0.00)
    if totalhoras > dezhoras:
        horas = str(totalhoras)[0:2]
        minutos = str(totalhoras)[3:5]
        if int(minutos) < 16  and int(minutos) > 0:
            fator = Decimal(0.25)
        elif int(minutos) < 31 and int(minutos) > 15:
            fator = Decimal(0.5)
        elif int(minutos) < 46 and int(minutos) > 30:
            fator = Decimal(0.75)
        elif int(minutos) < 59 and int(minutos) > 45:
            fator = Decimal(1.00)
        else:
            fator = Decimal(0.00)
        calcula_ajudante_recebe_hora_extra = valor_ajudante_recebe_hora_extra * fator
        calcula_ajudante_recebe_hora_extra += valor_ajudante_recebe_hora_extra * Decimal(int(horas) - 10)
    valorajudanterecebe += calcula_ajudante_recebe_hora_extra
    """
    Criaremos um dict 'tabela_recebe_e_paga' com todas as informações para gerar a tabela de recebimento e
    pagamento. A tabela será formada por 9 colunas sendo a primeira com as descrições (keys) e as demais divididas em
    4 para recebimento e 4 para pagamento. 1ª Coluna - switch - 2ª Coluna dados das tabelas - 3ª Coluna dados da
    minuta - 4ª Coluna para os totais que serão executados no frontend.

    """
    # Cria dict vazio
    tabela_recebe_e_paga = {}
    # Cria lista a receber para a descrições dos itens
    keys_recebe = ['TAXA DE EXPEDIÇÃO', 'SEGURO', 'PORCENTAGEM DA NOTA', 'HORAS', 'HORAS EXCEDENTE',
                   'KILOMETRAGEM', 'ENTREGAS', 'ENTREGAS KG', 'ENTREGAS VOLUME', 'SAIDA', 'CAPACIDADE PESO',
                   'PERIMETRO', 'PERNOITE', 'AJUDANTE', 'DESCONTO']
    # Cria lista a receber para as descrições para usar nos atributos (Ex. id, name, class)
    keys_nome_recebe = ['taxaexpedicao', 'seguro', 'porcentagem', 'horas', 'horasexcede', 'kilometragem', 'entregas',
                        'entregaskg', 'entregasvolume', 'saida', 'capacidade', 'perimetro', 'pernoite', 'ajudante',
                        'desconto']
    # Cria lista a receber para os labels dos inputs dos valores das tabelas do cliente
    type_tabela_recebe = ['R$', '%', '%', 'R$', '%', 'R$', 'R$', 'R$', 'R$', 'R$', 'R$', '%', '%', 'R$', 'R$']
    # Cria lista a receber para os inputs com os valores das tabelas do cliente
    values_tabela_recebe = [valortaxaexpedicao, 0.23, valorporcentagemrecebe, valorhorarecebe, 100, valorkmrecebe,
                            valorentrega_recebe, valorentregakg_recebe, valorentregavolume_recebe, valorsaidarecebe,
                            valorcapacidaderecebe, porceperimetrorecebe, 0, valorajudanterecebe, 0]
    # Cria lista a receber para os labels dos inputs dos valores da minuta
    type_minuta_recebe = [None, 'R$', 'R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN', None]
    # Cria lista a receber para os inputs com os valores daminuta
    values_minuta_recebe = [None, totalvalornotas['totalvalor'], totalvalornotas['totalvalor'], minimohoras,
                            excedehoras, totalkm, totalquantidadenotas, totalpesonotas['totalpeso'],
                            totalvolumenotas['totalvolume'], None, None, 0, 0, total_de_ajudantes, None]
    # Cria lista a pagar para a descrições dos itens
    keys_paga = ['PORCENTAGEM DA NOTA', 'HORAS', 'HORAS EXCEDENTE', 'KILOMETRAGEM', 'ENTREGAS', 'ENTREGAS KG',
                 'ENTREGAS VOLUME', 'SAIDA', 'CAPACIDADE PESO', 'PERIMETRO', 'PERNOITE', 'AJUDANTE']
    # Cria lista a pagar para as descrições para usar nos atributos (Ex. id, name, class)
    keys_nome_paga = ['porcentagem', 'horas', 'horasexcede', 'kilometragem', 'entregas', 'entregaskg',
                      'entregasvolume', 'saida', 'capacidade', 'perimetro', 'pernoite', 'ajudante']
    # Cria lista a pagar para os labels dos inputs dos valores das tabelas do cliente
    type_tabela_paga = ['%', 'R$', '%', 'R$', 'R$', 'R$', 'R$', 'R$', 'R$', '%', '%', 'R$']
    # Cria lista a pagar para os inputs com os valores das tabelas do cliente
    values_tabela_paga = [valorporcentagempaga, valorhorapaga, 100, valorkmpaga, valorentrega_paga,
                          valorentregakg_paga, valorentregavolume_paga, valorsaidapaga, valorcapacidadepaga,
                          porceperimetropaga, 0, valorajudantepaga]
    # Cria lista a pagar para os labels dos inputs dos valores da minuta
    type_minuta_paga = ['R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN']
    # Cria lista a pagar para os inputs com os valores daminuta
    values_minuta_paga = [totalvalornotas['totalvalor'], minimohoras, excedehoras, totalkm, totalquantidadenotas,
                          totalpesonotas['totalpeso'], totalvolumenotas['totalvolume'], None, None, 0, 0,
                          ajudantes_paga]
    # Cria dict com os switchs a receber desligados
    switch_recebe = {}
    for item in keys_nome_recebe:
        switch_recebe[item] = False
    # Cria dict com os switchs a pagar desligados
    switch_paga = {}
    for item in keys_nome_paga:
        switch_paga[item] = False
    # Altera os switchs a receber para ligados conforme valores das tabelas dos cliente
    if valortaxaexpedicao:
        switch_recebe['taxaexpedicao'] = True
    if phkescrecebe[0:1] == '1':
        switch_recebe['porcentagem'] = True
    if phkescrecebe[1:2] == '1':
        switch_recebe['horas'] = True
        switch_recebe['horasexcede'] = True
    if phkescrecebe[2:3] == '1':
        switch_recebe['kilometragem'] = True
    if phkescrecebe[3:4] == '1':
        switch_recebe['entregas'] = True
        switch_recebe['entregaskg'] = True
        switch_recebe['entregasvolume'] = True
    if phkescrecebe[4:5] == '1':
        switch_recebe['saida'] = True
    if phkescrecebe[5:6] == '1':
        switch_recebe['capacidade'] = True
    if tabelaperimetro:
        if porceperimetrorecebe != 0:
            switch_recebe['perimetro'] = True
    if ajudantes_da_minuta:
        switch_recebe['ajudante'] = True
    if ajudantes_paga > 0:
        switch_paga['ajudante'] = True
    # Altera os switchs a pagar para ligados conforme valores das tabelas dos cliente
    if motorista_da_minuta:
        if motorista_da_minuta[0].TipoPgto != 'MENSALISTA':
            if phkescpaga[0:1] == '1':
                switch_paga['porcentagem'] = True
            if phkescpaga[1:2] == '1':
                switch_paga['horas'] = True
                switch_paga['horasexcede'] = True
            if phkescpaga[2:3] == '1':
                switch_paga['kilometragem'] = True
            if phkescpaga[3:4] == '1':
                switch_paga['entregas'] = True
                switch_paga['entregaskg'] = True
                switch_paga['entregasvolume'] = True
            if phkescpaga[4:5] == '1':
                switch_paga['saida'] = True
            if phkescpaga[5:6] == '1':
                switch_paga['capacidade'] = True
            if tabelaperimetro:
                if porceperimetropaga != 0:
                    switch_paga['perimetro'] = True
    # Cria as chaves para o dict
    for item in keys_recebe:
        tabela_recebe_e_paga[item] = {}
    # Configura os valores a receber das chaves do dict
    for index, item in enumerate(keys_recebe):
        # Coluna 2 Recebe - Switch
        tabela_recebe_e_paga[str(item)]['id_swr'] = 'sw-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['name_swr'] = 'switch'
        tabela_recebe_e_paga[str(item)]['checked_swr'] = switch_recebe.get('%s' % keys_nome_recebe[index])
        tabela_recebe_e_paga[str(item)]['value_swr'] = 'sw-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['class_swr'] = 'switch switch--shadow change-%s-recebe' % keys_nome_recebe[
            index]
        tabela_recebe_e_paga[str(item)]['type_swr'] = 'checkbox'
        # Coluna 3 Recebe - tipo moeda ou porcentagem
        tabela_recebe_e_paga[str(item)]['type_tabela_recebe'] = type_tabela_recebe[index]
        # Columa 3 Recebe - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_tr'] = 'ta-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['name_tr'] = 'tabela-recebe'
        tabela_recebe_e_paga[str(item)]['value_tr'] = values_tabela_recebe[index]
        tabela_recebe_e_paga[str(item)]['class_tr'] = 'demonstrativo-input change-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['type_tr'] = 'number'
        tabela_recebe_e_paga[str(item)]['step_tr'] = '0.01'
        # Coluna 4 Recebe - tipo moeda ou tempo ou unidade ou kg
        tabela_recebe_e_paga[str(item)]['type_minuta_recebe'] = type_minuta_recebe[index]
        # Columa 4 Recebe - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_mr'] = 'mi-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['name_mr'] = 'minuta-recebe'
        tabela_recebe_e_paga[str(item)]['value_mr'] = values_minuta_recebe[index]
        tabela_recebe_e_paga[str(item)]['class_mr'] = 'demonstrativo-input change-%s-recebe' % keys_nome_recebe[index]
        if isinstance(values_minuta_recebe[index], time):
            tabela_recebe_e_paga[str(item)]['type_mr'] = 'time'
        else:
            tabela_recebe_e_paga[str(item)]['type_mr'] = 'number'
            tabela_recebe_e_paga[str(item)]['step_mr'] = '0.01'
        # Coluna 5 Recebe - totais
        tabela_recebe_e_paga[str(item)]['id_tor'] = 'to-%s-recebe' % keys_nome_recebe[index]
        # Coluna 5 Recebe - totais input hidden
        tabela_recebe_e_paga[str(item)]['id_hir'] = 'hi-%s-recebe' % keys_nome_recebe[index]
    # Configura os valores a pagar das chaves do dict
    for index, item in enumerate(keys_paga):
        # Coluna 2 Paga - Switch
        tabela_recebe_e_paga[str(item)]['id_swp'] = 'sw-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['name_swp'] = 'switch'
        tabela_recebe_e_paga[str(item)]['checked_swp'] = switch_paga.get('%s' % keys_nome_paga[index])
        tabela_recebe_e_paga[str(item)]['value_swp'] = 'sw-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['class_swp'] = 'switch switch--shadow change-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['type_swp'] = 'checkbox'
        # Coluna 3 Paga - tipo moeda ou porcentagem
        tabela_recebe_e_paga[str(item)]['type_tabela_paga'] = type_tabela_paga[index]
        # Columa 3 Paga - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_tp'] = 'ta-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['name_tp'] = 'tabela-paga'
        tabela_recebe_e_paga[str(item)]['value_tp'] = values_tabela_paga[index]
        tabela_recebe_e_paga[str(item)]['class_tp'] = 'demonstrativo-input change-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['type_tp'] = 'number'
        tabela_recebe_e_paga[str(item)]['step_tp'] = '0.01'
        # Coluna 4 Paga - tipo moeda ou tempo ou unidade ou kg
        tabela_recebe_e_paga[str(item)]['type_minuta_paga'] = type_minuta_paga[index]
        # Columa 4 Paga - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_mp'] = 'mi-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['name_mp'] = 'minuta-paga'
        tabela_recebe_e_paga[str(item)]['value_mp'] = values_minuta_paga[index]
        tabela_recebe_e_paga[str(item)]['class_mp'] = 'demonstrativo-input change-%s-paga' % keys_nome_paga[index]
        if isinstance(values_minuta_paga[index], time):
            tabela_recebe_e_paga[str(item)]['type_mp'] = 'time'
        else:
            tabela_recebe_e_paga[str(item)]['type_mp'] = 'number'
            tabela_recebe_e_paga[str(item)]['step_mp'] = '0.01'
        # Coluna 5 Paga - totais
        tabela_recebe_e_paga[str(item)]['id_top'] = 'to-%s-paga' % keys_nome_paga[index]
        # Coluna 5 Paga - totais input hidden
        tabela_recebe_e_paga[str(item)]['id_hip'] = 'hi-%s-paga' % keys_nome_paga[index]
    # Cria contexto para enviar ao template
    contexto = {
        'tabela_recebe_e_paga': tabela_recebe_e_paga,
        'minuta': minuta,
        'motorista_da_minuta': motorista_da_minuta,
        'ajudantes_da_minuta': ajudantes_da_minuta,
        'total_de_ajudantes': total_de_ajudantes,
        'itens_paga_motorista': itens_paga_motorista,
        'soma_paga_motorista': soma_paga_motorista,
        'veiculo': veiculo,
        'tabela': tabelacliente,
        'tabelaveiculo': tabelaveiculo,
        'formkminicial': formkminicial,
        'formkmfinal': formkmfinal,
        'formhorafinal': formhorafinal,
        'formsaidaextraajudante': formsaidaextraajudante,
        'formhoracobra': formhoracobra,
        'formhoraexcede': formhoraexcede,
        'formcomentarios': formcomentarios,
        'despesas': despesas,
        'itensminuta': itensminuta,
        'notas_minuta': notas_minuta,
        'notas_minuta_guia': notas_minuta_guia,
        'notas_perimetro': notas_perimetro,
        'notas_bairro': notas_bairro,
        'totalvalornotas': totalvalornotas,
        'totalpesonotas': totalpesonotas,
        'totalvolumenotas': totalvolumenotas,
        'totalquantidadenotas': totalquantidadenotas,
        'valortaxaexpedicao': valortaxaexpedicao,
        'valorporcentagemrecebe': valorporcentagemrecebe,
        'valorporcentagempaga': valorporcentagempaga,
        'valorhorarecebe': valorhorarecebe,
        'valorhorapaga': valorhorapaga,
        'minimohoras': minimohoras,
        'totalhoras': totalhoras,
        'excedehoras': excedehoras,
        'valorkmrecebe': valorkmrecebe,
        'valorkmpaga': valorkmpaga,
        'minimokm': minimokm,
        'inicialkm': inicialkm,
        'finalkm': finalkm,
        'totalkm': totalkm,
        'valorentrega_recebe': valorentrega_recebe,
        'valorentregakg_recebe': valorentregakg_recebe,
        'valorentregavolume_recebe': valorentregavolume_recebe,
        'valorentrega_paga': valorentrega_paga,
        'valorentregakg_paga': valorentregakg_paga,
        'valorentregavolume_paga': valorentregavolume_paga,
        'minimoentrega': minimoentrega,
        'valorsaidarecebe': valorsaidarecebe,
        'valorsaidapaga': valorsaidapaga,
        'valorcapacidaderecebe': valorcapacidaderecebe,
        'valorcapacidadepaga': valorcapacidadepaga,
        'porceperimetrorecebe': porceperimetrorecebe,
        'porceperimetropaga': porceperimetropaga,
        'porcesegurorecebe': porcesegurorecebe,
        'porcepernoite': porcepernoite,
        'valorajudanterecebe': valorajudanterecebe,
        'valorajudantepaga': valorajudantepaga,
        'minuta_itens_fechada': minuta_itens_fechada,
        'numero_saidas_do_ajudante': numero_saidas_do_ajudante,
    }
    return render(request, 'minutas/consultaminuta.html', contexto)


def minuta(request, idminuta):
    s_minuta = MinutaSelecionada(idminuta).__dict__
    minuta = Minuta.objects.filter(idMinuta=idminuta)
    minutaform = get_object_or_404(minuta, idMinuta=idminuta)
    form_veiculo_solicitado = FormEditaVeiculoSolicitado(instance=minutaform)
    form_hora_final = CadastraMinutaHoraFinal(instance=minutaform)
    form_km_inicial = CadastraMinutaKMInicial(instance=minutaform)
    form_km_final = CadastraMinutaKMFinal(instance=minutaform)
    contexto = {
        's_minuta': s_minuta, 'form_veiculo_solicitado': form_veiculo_solicitado,
        'form_hora_final': form_hora_final, 'form_km_inicial': form_km_inicial, 'form_km_final': form_km_final}
    return render(request, 'minutas/minuta.html', contexto)


def criaminuta(request):
    # Numero inicial da minuta no sistema
    numerominuta = 2021
    if request.method == 'POST':
        form = CadastraMinuta(request.POST)
    else:
        minuta = Minuta.objects.all()
        if minuta:
            numerominuta = Minuta.objects.values('Minuta')
            a = []
            for x in numerominuta:
                a.append(x.get('Minuta'))
            numerominuta = max(a) + 1
        form = CadastraMinuta(initial={'Minuta': numerominuta})
    return salva_form(request, form, 'minutas/criaminuta.html', numerominuta)


def editaminuta(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == 'POST':
        form = CadastraMinuta(request.POST, instance=minuta)
    else:
        form = CadastraMinuta(instance=minuta)
    return salva_form(request, form, 'minutas/editaminuta.html', idmin)


def imprimeminuta(request, idmin):
    if request.user.is_authenticated:
        minuta = Minuta.objects.get(idMinuta=idmin)
        contato = FoneContatoCliente.objects.filter(idCliente=minuta.idCliente)
        veiculo = ''
        if minuta.idVeiculo_id:
            veiculo = Veiculo.objects.get(idVeiculo=minuta.idVeiculo_id)
        colaboradores = MinutaColaboradores.objects.filter(idMinuta=idmin)
        motorista = ''
        ajudante = ''
        if colaboradores:
            minutacolaboradores = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='MOTORISTA')
            motorista = [item.idPessoal for item in minutacolaboradores]
            motorista = motorista[0]
            ajudante = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='AJUDANTE')
        response = HttpResponse(content_type='application/pdf')
        buffer = BytesIO()
        # Create the PDF object, using the BytesIO object as its "file."
        pdf = canvas.Canvas(buffer)
        # Draw things on the PDF. Here's where the PDF generation happens.
        # See the ReportLab documentation for the full list of functionality.

        pdf.roundRect(convertemp(10), convertemp(10), convertemp(190), convertemp(277), 10)
        # ----
        # development
        pdf.drawImage('website/static/website/img/transportadora.jpg', convertemp(12), convertemp(265),
                      convertemp(40),convertemp(20))
        # production
        # pdf.drawImage('efetiva/site/public/static/website/img/transportadora.jpg', convertemp(12), convertemp(265),
                    #   convertemp(40), convertemp(20))
        pdf.setFont("Times-Bold", 18)
        pdf.drawString(convertemp(56), convertemp(279), 'TRANSEFETIVA TRANSPORTE - EIRELLI - ME')
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(convertemp(57), convertemp(273), 'RUA GUARATINGUETÁ, 276 - MOOCA - SÃO PAULO - SP - CEP 03112-080')
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(convertemp(70), convertemp(268), '(11) 2305-0582 - (11) 2305-0583 - WHATSAPP (11) 94167-0583')
        pdf.drawString(convertemp(67), convertemp(263), 'e-mail: transefetiva@terra.com.br - '
                                                        'operacional.efetiva@terra.com.br')
        pdf.line(convertemp(10), convertemp(260), convertemp(200), convertemp(260))
        # ----
        pdf.setFillColor(HexColor("#FFFFFF"))
        pdf.setStrokeColor(HexColor("#FFFFFF"))
        pdf.rect(convertemp(10), convertemp(254.1), convertemp(190), convertemp(5.6), fill=1, stroke=1)
        pdf.setStrokeColor(HexColor("#000000"))
        pdf.setFillColor(HexColor("#000000"))
        # ----
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(convertemp(10), convertemp(255.8), 'ORDEM DE SERVIÇO Nº: ' + str(minuta.Minuta))
        pdf.drawRightString(convertemp(200), convertemp(255.8), 'DATA: ' + minuta.DataMinuta.strftime("%d/%m/%Y"))
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(10), convertemp(249), convertemp(95), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(57.5), convertemp(250.3), 'DADOS DO CLIENTE')
        # ----
        pdf.setFont("Times-Roman", 8)
        pdf.drawString(convertemp(11), convertemp(246), 'CLIENTE: ' + str(minuta.idCliente.Nome))
        endereco = minuta.idCliente.Endereco + ' - ' + minuta.idCliente.Bairro
        if len(endereco) > 45:
            pdf.drawString(convertemp(11), convertemp(242), 'ENDEREÇO: ' + endereco[0:45] + '...')
        else:
            pdf.drawString(convertemp(11), convertemp(242),
                           'ENDEREÇO: ' + minuta.idCliente.Endereco + ' - ' + minuta.idCliente.Bairro)
        pdf.drawString(convertemp(27), convertemp(238),
                       minuta.idCliente.Cidade + ' - ' + minuta.idCliente.Estado + ' - ' + minuta.idCliente.CEP)
        pdf.drawString(convertemp(11), convertemp(234), 'INSCRIÇÃO CNPJ:' + minuta.idCliente.CNPJ)
        pdf.drawString(convertemp(11), convertemp(230), 'INSCRIÇÃO ESTADUAL: ' + minuta.idCliente.IE)
        if contato:
            pdf.drawString(convertemp(11), convertemp(226), 'CONTATO: ' + contato[0].Contato)
            pdf.drawString(convertemp(11), convertemp(222), 'TELEFONE: ' + contato[0].Fone)
        # ----
        pdf.line(convertemp(105), convertemp(249), convertemp(105), convertemp(217))
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(105), convertemp(249), convertemp(95), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(152.5), convertemp(250.3), 'DADOS DO SERVIÇO SOLICITADO')
        # ----
        pdf.setFont("Times-Roman", 8)
        y = 250
        if minuta.idCategoriaVeiculo:
            y -= 4
            pdf.drawString(convertemp(106), convertemp(y), 'VEÍCULO: {}'.format(minuta.idCategoriaVeiculo))
            if veiculo:
                pdf.drawRightString(convertemp(199), convertemp(y), 'PLACA: {}'.format(veiculo))
        if motorista:
            y -= 4
            pdf.drawString(convertemp(106), convertemp(y), 'MOTORISTA: {}'.format(motorista))
        if ajudante:
            if ajudante.count() == 1:
                y -= 4
                pdf.drawString(convertemp(106), convertemp(y), 'AJUDANTE: {}'.format(ajudante[0].idPessoal))
            else:
                for x in range(ajudante.count()):
                    y -= 4
                    if x == 0:
                        pdf.drawString(convertemp(106), convertemp(y), str(ajudante.count()) + ' AJUDANTES: ' + str(
                                       ajudante[x].idPessoal))
                    else:
                        pdf.drawString(convertemp(126), convertemp(y), str(ajudante[x].idPessoal))
        if minuta.KMInicial:
            y -= 4
            pdf.drawString(convertemp(106), convertemp(y), 'KM Inicial: ' + str(minuta.KMInicial))
        y -= 4
        pdf.drawString(convertemp(106), convertemp(y), 'HORA INICIAL: ' + minuta.HoraInicial.strftime("%H:%M"))
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(10), convertemp(212), convertemp(95), convertemp(5),
                 fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(57.5), convertemp(213.3), 'DESCRIÇÃO DO SERVIÇO EXECUTADO')
        # ----
        pdf.line(convertemp(105), convertemp(212), convertemp(105), convertemp(172))
        # TODO Excluido custo operacional da minuta 18/09/2020
        # pdf.setFont("Times-Roman", 10)
        # pdf.setFillColor(HexColor("#c1c1c1"))
        # pdf.rect(convertemp(105), convertemp(212), convertemp(95), convertemp(5), fill=1)
        # pdf.setFillColor(HexColor("#000000"))
        # pdf.drawCentredString(convertemp(152.5), convertemp(213.3), 'CUSTO OPERACIONAL')
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(10), convertemp(167), convertemp(190), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(105), convertemp(168.3), 'DESCRIÇÃO DOS SERVIÇOS')
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(10), convertemp(87), convertemp(190), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(105), convertemp(88.3), 'LOCAIS DE ENTREGAS E COLETAS')
        pdf.setFont("Times-Roman", 8)
        entregacoleta = ''
        if minuta.Entrega and minuta.Coleta:
            entregacoleta = 'ENTREGA: ' + minuta.Entrega + ' - COLETA: ' + minuta.Coleta
        elif minuta.Entrega:
            entregacoleta = 'ENTREGA: ' + minuta.Entrega
        elif minuta.Coleta:
            entregacoleta = 'COLETA: ' + minuta.Coleta
        if len(entregacoleta) > 115:
            wrap_entcol = wrap(entregacoleta, width=115)
            y = 87.4
            for linha in range(len(wrap_entcol)):
                if linha == 4:
                    break
                y -= 3
                pdf.drawString(convertemp(11), convertemp(y), wrap_entcol[linha])
        else:
            pdf.drawString(convertemp(11), convertemp(84.4), entregacoleta)
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.setFillColor(HexColor("#c1c1c1"))
        pdf.rect(convertemp(10), convertemp(69), convertemp(190), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(105), convertemp(70.3), 'OBSERVAÇÕES')
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
        pdf.rect(convertemp(10), convertemp(51), convertemp(190), convertemp(5), fill=1)
        pdf.setFillColor(HexColor("#000000"))
        pdf.drawCentredString(convertemp(105), convertemp(52.3), 'KILOMETRAGEM')
        pdf.setFont("Times-Roman", 12)
        pdf.drawString(convertemp(11), convertemp(45.5), 'KM INICIAL: ')
        pdf.drawString(convertemp(106), convertemp(45.5), 'KM FINAL: ')
        # ----
        pdf.line(convertemp(10), convertemp(43), convertemp(200), convertemp(43))
        # ----
        pdf.roundRect(convertemp(12), convertemp(12), convertemp(101), convertemp(19), 3)
        pdf.setFont("Times-Roman", 7)
        textominuta = 'A TRANSEFETIVA TRANSPORTE - EIRELI - ME, só se responsabilizará pela mercadoria que o\ncliente' \
                      ' pagar seguro antes da mesma ser carregada. A responsabilidade da mercadoria e demais en-\ncargos' \
                      ' nela contida é unicamente do cliente. É de responsábilidade do cliente MULTAS DE TRAN-\nSITO e' \
                      ' outros encargos que podem ser cobrados, devido as restrições de horário e locais de entrega.\n' \
                      'Reconheço estar de pleno acordo com o serviço executado e dos dados informados, não tendo' \
                      ' recla-\nmações posteriores à assinatura deste documento.'
        textobject = pdf.beginText(convertemp(13), convertemp(28))
        for line in textominuta.splitlines(False):
            textobject.textLine(line.rstrip())
        pdf.drawText(textobject)
        # ----
        pdf.setFont("Times-Roman", 10)
        pdf.line(convertemp(118), convertemp(15), convertemp(194), convertemp(15))
        pdf.drawString(convertemp(118), convertemp(12), 'DATA, ASSINATURA E CARIMBO DO CLIENTE')
        # Close the PDF object cleanly.
        pdf.setTitle('Minuta.pdf')
        pdf.showPage()
        pdf.save()
        # Get the value of the BytesIO buffer and write it to the response.
        buffer.seek(0)
        pdf = buffer.getvalue()
        buffer.close()
        response.write(pdf)
        return response
    else:
        return redirect('consultaminuta', idmin)


def fecha_minuta(request, idmin):
    """
    FUNÇÃO PARA INSERIR NA TABELA "MINUTAITENS" OS ITENS DE COBRANÇA E PAGAMENTO DA MINUTA.
    CHAMA A FUNÇÃO exclui_minuta_itens PARA APAGAR ITENS QUE ESTIVER COM VALOR 0.
    ALTERA O STATUS DA MINUTA PARA "FECHADA"
    RETORNA A PAGINA CONSULTA DA MINUTA

    :param request: request
    :param idmin: int :return:
    """
    keys_recebe = ['TAXA DE EXPEDIÇÃO', 'SEGURO', 'PORCENTAGEM DA NOTA', 'HORAS', 'HORAS EXCEDENTE', 'KILOMETRAGEM',
                   'ENTREGAS', 'ENTREGAS KG', 'ENTREGAS VOLUME', 'SAIDA', 'CAPACIDADE PESO', 'PERIMETRO', 'PERNOITE',
                   'AJUDANTE', 'DESCONTO']
    keys_nome_recebe = ['taxaexpedicao', 'seguro', 'porcentagem', 'horas', 'horasexcede', 'kilometragem', 'entregas',
                        'entregaskg', 'entregasvolume', 'saida', 'capacidade', 'perimetro', 'pernoite', 'ajudante',
                        'desconto']
    type_tabela_recebe = ['R$', '%', '%', 'R$', '%', 'R$', 'R$', 'R$', 'R$', 'R$', 'R$', '%', '%', 'R$', 'R$']
    type_minuta_recebe = [None, 'R$', 'R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN', None]
    keys_paga = ['PORCENTAGEM DA NOTA', 'HORAS', 'HORAS EXCEDENTE', 'KILOMETRAGEM', 'ENTREGAS', 'ENTREGAS KG',
                 'ENTREGAS VOLUME', 'SAIDA', 'CAPACIDADE PESO', 'PERIMETRO', 'PERNOITE', 'AJUDANTE']
    keys_nome_paga = ['porcentagem', 'horas', 'horasexcede', 'kilometragem', 'entregas', 'entregaskg',
                      'entregasvolume', 'saida', 'capacidade', 'perimetro', 'pernoite', 'ajudante']
    type_tabela_paga = ['%', 'R$', '%', 'R$', 'R$', 'R$', 'R$', 'R$', 'R$', '%', '%', 'R$']
    type_minuta_paga = ['R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN']
    dados_switch = request.POST.getlist('switch')
    dados_tabela_recebe = request.POST.getlist('tabela-recebe')
    dados_minuta_recebe = request.POST.getlist('minuta-recebe')
    dados_minuta_recebe.insert(0, None)
    dados_minuta_recebe.insert(9, None)
    dados_minuta_recebe.insert(10, None)
    dados_minuta_recebe.insert(14, None)
    dados_valor_recebe = request.POST.getlist('valor-recebe')
    for index, itens in enumerate(keys_nome_recebe):
        switch_name = 'sw-%s-recebe' % itens
        if switch_name in dados_switch:
            if dados_valor_recebe != 0:
                if (type_tabela_recebe[index] == 'R$') and (type_minuta_recebe[index] is None):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index], 0, 0, 0,
                                     dados_tabela_recebe[index], '00:00', idmin)
                if (type_tabela_recebe[index] == '%') and (type_minuta_recebe[index] == 'R$'):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index], 0,
                                     dados_tabela_recebe[index], 0, dados_minuta_recebe[index], '00:00', idmin)
                if (type_tabela_recebe[index] == 'R$') and (type_minuta_recebe[index] == 'HS'):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index], 0, 0, 0,
                                     dados_tabela_recebe[index], dados_minuta_recebe[index], idmin)
                if (type_tabela_recebe[index] == '%') and (type_minuta_recebe[index] == 'HS'):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index], 0,
                                     dados_tabela_recebe[index], 0, 0, dados_minuta_recebe[index], idmin)
                if (type_tabela_recebe[index] == 'R$') and (type_minuta_recebe[index] == 'UN'):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index],
                                     dados_minuta_recebe[index], 0, 0, dados_tabela_recebe[index], '00:00', idmin)
                if (type_tabela_recebe[index] == 'R$') and (type_minuta_recebe[index] == 'KG'):
                    salvaminutaitens(keys_recebe[index], 'RECEBE', 'R', dados_valor_recebe[index], 0, 0,
                                     dados_minuta_recebe[index], dados_tabela_recebe[index], '00:00', idmin)
    dados_tabela_paga = request.POST.getlist('tabela-paga')
    dados_minuta_paga = request.POST.getlist('minuta-paga')
    dados_minuta_paga.insert(7, None)
    dados_minuta_paga.insert(8, None)
    dados_valor_paga = request.POST.getlist('valor-paga')
    for index, itens in enumerate(keys_nome_paga):
        switch_name = 'sw-%s-paga' % itens
        if switch_name in dados_switch:
            if dados_valor_paga != 0:
                if (type_tabela_paga[index] == 'R$') and (type_minuta_paga[index] is None):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], 0, 0, 0,
                                     dados_tabela_paga[index], '00:00', idmin)
                if (type_tabela_paga[index] == '%') and (type_minuta_paga[index] == 'R$'):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], 0,
                                     dados_tabela_paga[index], 0, dados_minuta_paga[index], '00:00', idmin)
                if (type_tabela_paga[index] == 'R$') and (type_minuta_paga[index] == 'HS'):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], 0, 0, 0,
                                     dados_tabela_paga[index], dados_minuta_paga[index], idmin)
                if (type_tabela_paga[index] == '%') and (type_minuta_paga[index] == 'HS'):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], 0,
                                     dados_tabela_paga[index], 0, 0, dados_minuta_paga[index], idmin)
                if (type_tabela_paga[index] == 'R$') and (type_minuta_paga[index] == 'UN'):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], dados_minuta_paga[
                        index], 0, 0, dados_tabela_paga[index], '00:00', idmin)
                if (type_tabela_paga[index] == 'R$') and (type_minuta_paga[index] == 'KG'):
                    salvaminutaitens(keys_paga[index], 'PAGA', 'P', dados_valor_paga[index], 0, 0,
                                     dados_minuta_paga[index], dados_tabela_paga[index], '00:00', idmin)
    dados_descricao_despesa_recebe = request.POST.getlist('descricao-despesa-recebe')
    dados_valor_despesa_recebe = request.POST.getlist('valor-despesa-recebe')
    for index, itens in enumerate(dados_descricao_despesa_recebe, start=0):
        float(dados_valor_despesa_recebe[index].replace(',', '.'))
        salvaminutaitens(dados_descricao_despesa_recebe[index], 'DESPESA', 'R',
                         float(dados_valor_despesa_recebe[index].replace(',', '.')), 0, 0.00, 0.00, 0.00, '00:00', idmin)
    dados_descricao_despesa_paga = request.POST.getlist('descricao-despesa-paga')
    dados_valor_despesa_paga = request.POST.getlist('valor-despesa-paga')
    for index, itens in enumerate(dados_descricao_despesa_paga, start=0):
        float(dados_valor_despesa_paga[index].replace(',', '.'))
        salvaminutaitens(dados_descricao_despesa_paga[index], 'REEMBOLSO', 'P',
                         float(dados_valor_despesa_paga[index].replace(',', '.')), 0, 0.00, 0.00, 0.00, '00:00', idmin)
    minuta_itens = MinutaItens.objects.filter(idMinuta_id=idmin)
    for itens in minuta_itens:
        if itens.Valor == 0:
            excluiminutaitens(itens.idMinutaItens)
        altera_status_minuta('FECHADA', idmin)
    valor_minuta = MinutaItens.objects.filter(idMinuta=idmin, RecebePaga='R').aggregate(totalminuta=Sum('Valor'))
    cria_minuta_fatura(valor_minuta['totalminuta'], idmin)
    return redirect('consultaminuta', idmin)


def estorna_minuta(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if minuta.StatusMinuta == 'ABERTA':
        pass
    elif minuta.StatusMinuta == 'CONCLUIDA':
        altera_status_minuta('ABERTA', idmin)
    elif minuta.StatusMinuta == 'FECHADA':
        altera_status_minuta('ABERTA', idmin)
        itens_minuta_recebe_excluir = MinutaItens.objects.filter(idMinuta=idmin).filter(TipoItens='RECEBE')
        for itens in itens_minuta_recebe_excluir:
            excluiminutaitens(itens.idMinutaItens)
        itens_minuta_paga_excluir = MinutaItens.objects.filter(idMinuta=idmin).filter(RecebePaga='P')
        for itens in itens_minuta_paga_excluir:
            excluiminutaitens(itens.idMinutaItens)
    return redirect('consultaminuta', idmin)


def conclui_minuta(request, idmin):
    # if request.user.is_authenticated():
    altera_status_minuta('CONCLUIDA', idmin)
    return redirect('consultaminuta', idmin)


def criaminutamotorista(request):
    if request.method == 'POST':
        idminuta = request.POST.get('idMinuta')
        form = CadastraMinutaMotorista(request.POST)
        # Altera field idVeiculo conforme motorista escolhido
        veiculo = Veiculo.objects.filter(Motorista=request.POST.get('idPessoal'))
        if veiculo.count() == 1:
            idveiculo = ''
            for x in veiculo:
                idveiculo = x.idVeiculo
            km_inicial = kmfinal_veiculo(idveiculo)
            if km_inicial:
                minuta = get_object_or_404(Minuta, idMinuta=idminuta)
                obj = Minuta()
                obj.idMinuta = minuta.idMinuta
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
                obj.idVeiculo_id = idveiculo
                obj.save()
    else:
        idminuta = request.GET.get('idminuta')
        form = CadastraMinutaMotorista(
            initial={'idMinuta': idminuta, 'Cargo': 'MOTORISTA'})
    return salva_form(request, form, 'minutas/criaminutamotorista.html',
                      idminuta)


def excluiminutamotorista(request, idmincol):
    motoristaminuta = get_object_or_404(MinutaColaboradores, idMinutaColaboradores=idmincol)
    # cliente = Cliente.objects.get(Nome=tabelacapacidade.idCliente)
    data = dict()
    if request.method == "POST":
        motoristaminuta.delete()
        # Altera field idVeiculo para null
        minuta = get_object_or_404(Minuta, idMinuta=motoristaminuta.idMinuta_id)
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
        obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
        obj.idCliente = minuta.idCliente
        obj.idVeiculo_id = None
        obj.save()
        return redirect('consultaminuta', motoristaminuta.idMinuta_id)
    else:
        context = {'motoristaminuta': motoristaminuta}
        data['html_form'] = render_to_string(
            'minutas/excluiminutamotorista.html', context, request=request)
    return JsonResponse(data)


def criaminutaajudante(request):
    if request.method == 'POST':
        idminuta = request.POST.get('idMinuta')
        form = CadastraMinutaAjudante(request.POST)
    else:
        idminuta = request.GET.get('idminuta')
        form = CadastraMinutaAjudante(initial={'idMinuta': idminuta, 'Cargo': 'AJUDANTE'})
    return salva_form(request, form, 'minutas/criaminutaajudante.html',
                      idminuta)


def excluiminutaajudante(request, idmincol):
    ajudanteminuta = get_object_or_404(MinutaColaboradores,
                                       idMinutaColaboradores=idmincol)
    data = dict()
    if request.method == "POST":
        ajudanteminuta.delete()
        return redirect('consultaminuta', ajudanteminuta.idMinuta_id)
    else:
        context = {'ajudanteminuta': ajudanteminuta}
        data['html_form'] = render_to_string(
            'minutas/excluiminutaajudante.html', context, request=request)
    return JsonResponse(data)


def editaminutaveiculo(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == 'POST':
        form = CadastraMinutaVeiculo(request.POST)
        if form.is_valid():
            km_inicial = kmfinal_veiculo(form.cleaned_data['Veiculo'])
            if not km_inicial:
                km_inicial = 0
            obj = Minuta()
            obj.idMinuta = form.cleaned_data['idMinuta']
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
            obj.idVeiculo_id = form.cleaned_data['Veiculo']
            obj.save()
    else:
        form = CadastraMinutaVeiculo(initial={'idMinuta': idmin, 'Veiculo': minuta.idVeiculo_id})
    return salva_form(request, form, 'minutas/editaminutaveiculo.html', idmin)


def editaminutakminicial(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == 'POST':
        form = CadastraMinutaKMInicial(request.POST, instance=minuta)
    else:
        form = CadastraMinutaKMInicial(instance=minuta)
    return salva_form(request, form, 'minutas/consultaminuta.html', idmin)


def editaminutakmfinal(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == 'POST':
        form = CadastraMinutaKMFinal(request.POST, instance=minuta)
    else:
        form = CadastraMinutaKMFinal(instance=minuta)
    return salva_form(request, form, 'minutas/consultaminuta.html', idmin)


def editaminutahorafinal(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if request.method == 'POST':
        form = CadastraMinutaHoraFinal(request.POST, instance=minuta)
    else:
        form = CadastraMinutaHoraFinal(instance=minuta)
    return salva_form(request, form, 'minutas/consultaminuta.html', idmin)


def criaminutadespesa(request):
    if float(request.POST.get('Valor')) > 0.00:
        if request.method == 'POST':
            descricao = request.POST.get('Descricao')
            idminuta = request.POST.get('idMinuta')
            despesa = buscaminutadespesa(descricao, idminuta)
            if despesa:
                idminutaitem = \
                    list(despesa.values('idMinutaItens')[0].values())[0]
                minutaitens = get_object_or_404(MinutaItens,
                                                idMinutaItens=idminutaitem)
                form = CadastraMinutaDespesa(request.POST,
                                             instance=minutaitens)
            else:
                form = CadastraMinutaDespesa(request.POST)
            return salva_form(request, form, 'minutas/colsultaminuta.html',
                              idminuta)
    return redirect('consultaminuta', request.POST.get('idMinuta'))


def buscaminutadespesa(descricao, idminuta):
    buscadespesa = MinutaItens.objects.filter(Descricao=descricao,
                                              idMinuta=idminuta)
    return buscadespesa


def excluiminutadespesa(request, idmindes):
    despesaminuta = get_object_or_404(MinutaItens, idMinutaItens=idmindes)
    data = dict()
    if request.method == "POST":
        despesaminuta.delete()
        return redirect('consultaminuta', despesaminuta.idMinuta_id)
    else:
        context = {'despesaminuta': despesaminuta}
        data['html_form'] = render_to_string(
            'minutas/excluiminutadespesa.html', context, request=request)
    return JsonResponse(data)


def criaminutaentrega(request):
    if request.method == 'POST':
        idminuta = request.POST.get('idMinuta')
        form = CadastraMinutaNota(idminuta, request.POST)
    else:
        idminuta = request.GET.get('idminuta')
        form = CadastraMinutaNota(idminuta, initial={'idMinuta': idminuta})
    return salva_form(request, form, 'minutas/criaminutaentrega.html', idminuta)


def editaminutaentrega(request, idminent):
    notaminuta = get_object_or_404(MinutaNotas, idMinutaNotas=idminent)
    data = dict()
    if request.method == 'POST':
        form = CadastraMinutaNota(notaminuta.idMinuta_id, request.POST, instance=notaminuta)
        if form.is_valid():
            form.save()
        return redirect('consultaminuta', notaminuta.idMinuta_id)
    else:
        form = CadastraMinutaNota(notaminuta.idMinuta_id, instance=notaminuta)
        context = {'form': form, 'numerominuta': request.GET.get('idminuta'), 'idminent': idminent}
        data['html_form'] = render_to_string('minutas/editaminutaentrega.html', context, request=request)
    return JsonResponse(data)


def excluiminutaentrega(request, idminent):
    notaminuta = get_object_or_404(MinutaNotas, idMinutaNotas=idminent)
    data = dict()
    if request.method == "POST":
        notaminuta.delete()
        return redirect('consultaminuta', notaminuta.idMinuta_id)
    else:
        context = {'notaminuta': notaminuta}
        data['html_form'] = render_to_string('minutas/excluiminutaentrega.html', context, request=request)
    return JsonResponse(data)


def buscaminutaentrega(request):
    nota_guia = MinutaNotas.objects.filter(idMinuta_id=request.GET.get('id_minuta'), Nota=request.GET.get('nota_guia'))
    nota_guia_nome = list(nota_guia.values('Nome')[0].values())[0]
    nota_guia_cidade = list(nota_guia.values('Cidade')[0].values())[0]
    nota_guia_estado = list(nota_guia.values('Estado')[0].values())[0]
    data = {'nota_guia_nome': nota_guia_nome, 'nota_guia_cidade': nota_guia_cidade,
            'nota_guia_estado': nota_guia_estado}
    return JsonResponse(data)


def filtraminutaveiculo(request):
    data = dict()
    propriedade = request.GET.get('propriedade')
    idminutamotoristacolaboradores = MinutaColaboradores.objects.filter(
        idMinutaColaboradores=request.GET.get('idminutacolaboradores'))
    idmotorista = idminutamotoristacolaboradores.values_list('idPessoal_id')[0]
    veiculo = ''
    if propriedade == '1':
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat('Marca', Value(' - '), 'Modelo', Value(' - '),
                           'Placa')).filter(Motorista=idmotorista)
    elif propriedade == '2':
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat('Marca', Value(' - '), 'Modelo', Value(' - '),
                           'Placa')).filter(Motorista=17)
    elif propriedade == '3':
        veiculo = Veiculo.objects.annotate(
            Veiculo=Concat('Marca', Value(' - '), 'Modelo', Value(' - '),
                           'Placa')).all()
    listaveiculo = []
    for x in veiculo:
        listaveiculo.append(x)
    context = {'listaveiculo': listaveiculo}
    data['html_form'] = render_to_string(
        'minutas/editaminutaveiculolista.html', context, request=request)
    return JsonResponse(data)


def criaminutaparametrodespesa(request):
    # data = dict()
    # if request.method == 'POST':
    #     try:
    #         arquivo_json = open('', 'r')
    #         dados_json = json.load(arquivo_json)
    #         arquivo_json.close()
    #         despesas = dados_json['Despesa']['Descricao']
    #         if request.POST.get('Despesa') in despesas:
    #             pass
    #         else:
    #             despesas.append(request.POST.get('Despesa').upper())
    #             try:
    #                 arquivo_json = open('', 'w')
    #                 dados_json['Despesa']['Descricao'] = despesas
    #                 dados_json = json.dumps(dados_json, indent=4,
    #                                         sort_keys=True)
    #                 arquivo_json.write(dados_json)
    #                 arquivo_json.close()
    #             except Exception as erro:
    #                 print(erro)
    #     except Exception as erro:
    #         print(erro)
    #     return redirect('consultaminuta', request.POST.get('idMinuta'))
    # else:
    #     form = CadastraMinutaParametroDespesa(
    #         initial={'idMinuta': request.GET.get('idminuta')})
    # context = {'form': form}
    # data['html_form'] = render_to_string(
    #     'minutas/criaminutaparametrodespesa.html', context, request=request)
    # return JsonResponse(data)
    # TODO removido arquivo parametro, criado banco de dados, remover view
    pass


def edita_comentario(request, idmin):
    minuta = Minuta.objects.get(idMinuta=idmin)
    form = ''
    if request.method == 'POST':
        form = CadastraComentarioMinuta(request.POST, instance=minuta)
    return salva_form(request, form, 'minutas/consultaminuta.html', idmin)


def salva_form(request, form, template_name, idmin):
    data = dict()
    numerominuta = 0
    numeroidminuta = idmin
    if template_name != 'minutas/editaminutaveiculo.html':
        numeroidminuta = form.instance
    if request.method == 'POST':
        if form.is_valid():
            data['form_is_valid'] = True
            if template_name != 'minutas/editaminutaveiculo.html':
                form.save()
            if template_name == 'minutas/criaminuta.html':
                return redirect('consultaminuta', numeroidminuta.idMinuta)
            else:
                return redirect('consultaminuta', idmin)
        else:
            return redirect('consultaminuta', idmin)
    context = {'form': form, 'numerominuta': numerominuta, 'numeroidminuta': numeroidminuta}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)


def exclui_minuta(request, idminuta):
    minuta = Minuta.objects.filter(idMinuta=idminuta)
    minuta.delete()
    return redirect('index_minuta')







def atualiza_form_pg(request):
    print(request.POST)
    print(request.GET)


def gera_pagamentos(request):
    prepara_itens(request)
    data = dict()
    data['html_idminuta'] = request.POST.get('idminuta')
    return JsonResponse(data)


def estorna_pagamentos(request):
    c_idminuta = request.GET.get('idMinuta')
    estorna_paga(c_idminuta)
    data = dict()
    data['html_idminuta'] = request.GET.get('idMinuta')
    return JsonResponse(data)


def adiciona_minuta(request):
    c_form = FormMinuta
    c_idobj = None
    c_url = '/minutas/adicionaminuta/'
    c_view = 'adiciona_minuta'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def filtra_minuta(request):
    c_filtro = request.GET.get('Filtro')
    c_filtro_consulta = request.GET.get('FiltroConsulta')
    c_meses = request.GET.get('Meses')
    c_anos = request.GET.get('Anos')
    data = filtra_consulta(request, c_filtro, c_filtro_consulta, c_meses, c_anos)
    return data


def concluir_minuta(request):
    c_idminuta = request.GET.get('idMinuta')
    data = novo_status_minuta(request, c_idminuta, 'CONCLUIDA')
    return data


def edita_minuta(request):
    c_form = FormMinuta
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/editaminuta/'
    c_view = 'edita_minuta'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_minuta_saida_extra_ajudante(request, idminuta):
    minutanotas = MinutaNotas.objects.filter(idMinuta=idminuta)
    for itens in minutanotas:
        obj = itens
        obj.ExtraValorAjudante = request.POST.get('ExtraValorAjudante')
        obj.save(update_fields=['ExtraValorAjudante'])
    return redirect('consultaminuta', idminuta)


def edita_minuta_veiculo_solicitado(request):
    c_form = FormEditaVeiculoSolicitado
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/editaveiculosolicitado/'
    c_view = 'edita_minuta_veiculo_solicitado'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def edita_minuta_veiculo_escolhido(request):
    c_form = FormEditaVeiculoEscolhido
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/editaveiculoescolhido/'
    c_view = 'edita_minuta_veiculo_escolhido'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def filtra_minuta_veiculo_escolhido(request):
    idpessoal = request.GET.get('idPessoal')
    opcao = request.GET.get('Filtro')
    lista_veiculos = filtra_veiculo(idpessoal, opcao)
    data = html_filtro_veiculo(request, lista_veiculos)
    return data


def insere_ajudante(request):
    c_form = FormInsereColaborador
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/insereajudante/'
    c_view = 'insere_ajudante'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def insere_motorista(request):
    c_form = FormInsereColaborador
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/inseremotorista/'
    c_view = 'insere_motorista'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def remove_minuta_colaborador(request):
    c_idobj = request.GET.get('idMinutaColaboradores')
    c_idminuta = request.GET.get('idMinuta')
    c_cargo = request.GET.get('Cargo')
    data = remove_colaborador(request, c_idobj, c_idminuta, c_cargo)
    data = retorna_json(data)
    return data


def edita_minuta_hora_final(request):
    c_idminuta = request.POST.get('idMinuta')
    c_horafinal = request.POST.get('HoraFinal')
    data = edita_hora_final(request, c_idminuta, c_horafinal)
    return data


def edita_minuta_km_inicial(request):
    c_idminuta = request.POST.get('idMinuta')
    c_kminicial = request.POST.get('KMInicial')
    data = edita_km_inicial(request, c_idminuta, c_kminicial)
    return data


def edita_minuta_km_final(request):
    c_idminuta = request.POST.get('idMinuta')
    c_kmfinal = request.POST.get('KMFinal')
    data = edita_km_final(request, c_idminuta, c_kmfinal)
    return data


def edita_minuta_coleta_entrega_obs(request):
    c_form = FormColetaEntregaObs
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/editacoletaentregaobs/'
    c_view = 'edita_minuta_coleta_entrega_obs'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def insere_minuta_despesa(request):
    c_form = FormInsereDespesa
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/inseredespesa/'
    c_view = 'insere_minuta_despesa'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def remove_minuta_despesa(request):
    c_idobj = request.GET.get('idMinutaItens')
    c_idminuta = request.GET.get('idMinuta')
    data = remove_despessa(request, c_idobj, c_idminuta)
    data = retorna_json(data)
    return data


def insere_minuta_entrega(request):
    c_form = FormInsereEntrega
    c_idobj = None
    if request.method == 'GET':
        c_idobj = request.GET.get('idobj')
    elif request.method == 'POST':
        c_idobj = request.POST.get('idMinuta')
    c_url = '/minutas/insereentrega/'
    c_view = 'insere_minuta_entrega'
    data = forn_minuta(request, c_form, c_idobj, c_url, c_view)
    return data


def remove_minuta_entrega(request):
    c_idobj = request.GET.get('idMinutaNotas')
    c_idminuta = request.GET.get('idMinuta')
    data = remove_entrega(request, c_idobj, c_idminuta)
    data = retorna_json(data)
    return data
