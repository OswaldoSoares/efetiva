from io import BytesIO
from textwrap import wrap
from django.db.models import Value, Sum
from django.db.models.functions import Concat
from django.http import JsonResponse, HttpResponse
from django.shortcuts import redirect, get_object_or_404
from django.shortcuts import render
from django.template.loader import render_to_string
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from datetime import datetime, timedelta, time
import json
from clientes.models import FoneContatoCliente, Tabela, TabelaVeiculo, \
    TabelaCapacidade, TabelaPerimetro
from veiculos.models import Veiculo
from .forms import CadastraMinuta, CadastraMinutaMotorista, CadastraMinutaAjudante, CadastraMinutaVeiculo, \
    CadastraMinutaKMInicial,CadastraMinutaKMFinal, CadastraMinutaHoraFinal, CadastraMinutaDespesa, \
    CadastraMinutaParametroDespesa, CadastraMinutaNota
from .models import Minuta, MinutaColaboradores, MinutaItens, MinutaNotas


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
    despesas = ()
    try:
        arquivo_json = open('parametros.json', 'r')
        dados_json = json.load(arquivo_json)
        arquivo_json.close()
        despesas = dados_json['Despesa']['Descricao']
        despesas.sort()
        return despesas
    except:
        return despesas


def salvaminutaitens(Descricao, TipoItens, RecebePaga, Valor, Quantidade, Porcento, Peso, ValorBase, Tempo, idMinuta):
    """
    Função para inserir e atualizar um item da minuta

    :param Descricao:
    :param TipoItens:
    :param RecebePaga:
    :param Valor:
    :param Quantidade:
    :param Porcento:
    :param Tempo:
    :param idMinuta:
    :return:
    """
    minutaitens = MinutaItens.objects.filter(idMinuta=idMinuta,
                                             Descricao=Descricao[0],
                                             RecebePaga=RecebePaga,
                                             TipoItens=TipoItens)
    hora_datetime = datetime.strptime(Tempo, '%H:%M')
    hora_timedelta = timedelta(days=0, hours=hora_datetime.hour,
                               minutes=hora_datetime.minute)
    obj = MinutaItens()
    if minutaitens:
        obj.idMinutaItens = \
            list(minutaitens.values('idMinutaItens')[0].values())[0]
    obj.Descricao = Descricao[0]
    obj.TipoItens = TipoItens
    obj.RecebePaga = RecebePaga
    obj.Valor = Valor[0]
    obj.Quantidade = Quantidade
    obj.Porcento = Porcento
    obj.Peso = Peso
    obj.ValorBase = ValorBase
    obj.Tempo = hora_timedelta
    obj.idMinuta_id = idMinuta
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


def buscaminutaitens(Descricao, TipoItens, RecebePaga, idMinuta):
    pass


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
        obj.Obs = minuta.Obs
        obj.StatusMinuta = novo_status
        obj.idCliente = minuta.idCliente
        obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
        obj.idVeiculo = minuta.idVeiculo
        obj.save()
    return True


def index_minuta(request):
    """
    Função para carregar a página principal do Módulo: Minuta.
    Cria como padrã a QuerySet minuta apenas com as Minutas cujo StatusMinuta é Aberta.
    Caso tenha request GET cria variaveis e QuerySet com as Minutas cujo Status ou minuta
    foi selecionado.
    Cria uma lista 'minuta_status' com as opções de Status para compor o Filtro.
    Cria a QuerySet minutacolaboradores apenas com os Colaboradores cujo Cargo é Motorista.

    :param request:
    :return:
    """
    meu_filtro_minuta = request.GET.get('filtrominuta')
    meu_filtro_status = request.GET.get('filtrostatus')
    if meu_filtro_minuta:
        minuta = Minuta.objects.filter(Minuta=meu_filtro_minuta)
    elif meu_filtro_status:
        minuta = Minuta.objects.filter(StatusMinuta=meu_filtro_status)
    else:
        minuta = Minuta.objects.filter(StatusMinuta='ABERTA')
    minuta_status = Minuta.objects.all().values_list('StatusMinuta', flat=True)
    minuta_status = sorted(list(dict.fromkeys(minuta_status)))
    minutacolaboradores = MinutaColaboradores.objects.filter(Cargo='MOTORISTA')
    return render(request, 'minutas/index.html', {'minuta': minuta,
                                                  'minuta_status': minuta_status,
                                                  'minutacolaboradores': minutacolaboradores})


def consultaminuta(request, idmin):
    if request.method == 'POST':
        print(request.POST)
        # fecha_minuta(request, idmin)
    # Cria queryset obj minuta - motorista - ajudante - ajudante quantidade
    minuta = Minuta.objects.filter(idMinuta=idmin)
    motorista_da_minuta = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='MOTORISTA')
    ajudantes_da_minuta = MinutaColaboradores.objects.filter(idMinuta=idmin, Cargo='AJUDANTE')
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
    valorajudantepaga = list(tabelacliente.values('AjudantePaga')[0].values())[0]
    valorentrega_recebe = list(tabelacliente.values('EntregaCobra')[0].values())[0]
    valorentregakg_recebe = list(tabelacliente.values('EntregaKGCobra')[0].values())[0]
    valorentregavolume_recebe = list(tabelacliente.values('EntregaVolumeCobra')[0].values())[0]
    valorentrega_paga = list(tabelacliente.values('EntregaPaga')[0].values())[0]
    valorentregakg_paga = list(tabelacliente.values('EntregaKGPaga')[0].values())[0]
    valorentregavolume_paga = list(tabelacliente.values('EntregaVolumePaga')[0].values())[0]
    # Cria queryset obj tabela veículo
    tabelaveiculo = TabelaVeiculo.objects.filter(idCliente=idcliente, idCategoriaVeiculo=idcategoriaveiculo)
    inicialkm = list(minuta.values('KMInicial')[0].values())[0]
    finalkm = list(minuta.values('KMFinal')[0].values())[0]
    totalkm = finalkm - inicialkm
    # Cria variaveis zerada
    totalhoras = 0.00
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
    porcesegurorecebe = 1.00
    porceperimetro = 100
    porcepernoite = 100
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
        minimokm = list(tabelaveiculo.values('KMMinimo')[0].values())[0]
        # TODO VALOR DA ENTREGA MUDOU PARA TABELA DE CLIENTE 03/10/2020
        # valorentrega = list(tabelaveiculo.values('EntregaCobra')[0].values())[0]
        # minimoentrega = list(tabelaveiculo.values('EntregaMinimo')[0].values())[0]
        valorsaidarecebe = list(tabelaveiculo.values('SaidaCobra')[0].values())[0]
        valorsaidapaga = list(tabelaveiculo.values('SaidaPaga')[0].values())[0]
        strexedehoras = str(excedehoras)
        # Cria variavel dezhoras para verificar quantidade de digitos da
        # horas excedentes e minimo
        dezhoras = timedelta(days=0, hours=10, minutes=0)
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
    # Cria queryset notas e objs das somas
    notasminuta = MinutaNotas.objects.filter(idMinuta=idmin)
    notas_minuta_guia = MinutaNotas.objects.filter(idMinuta=idmin).exclude(NotaGuia=None)
    totalvalornotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalvalor=Sum('Valor'))
    totalpesonotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalpeso=Sum('Peso'))
    peso = totalpesonotas['totalpeso']
    totalvolumenotas = MinutaNotas.objects.filter(idMinuta=idmin).aggregate(totalvolume=Sum('Volume'))
    totalquantidadenotas = MinutaNotas.objects.filter(idMinuta=idmin).count()
    quantidade_notas_guia = MinutaNotas.objects.filter(idMinuta=idmin).exclude(NotaGuia=None).count()
    # Percorre a tabelacapacidade para localizar o peso
    if tabelacapacidade and peso:
        for x in tabelacapacidade:
            if peso > x.CapacidadeInicial:
                if peso < x.CapacidadeFinal:
                    valorcapacidaderecebe = x.CapacidadeCobra
                    valorcapacidadepaga = x.CapacidadePaga
                    break
    # Percorre a tabelaperimetro para localizar a km
    for x in tabelaperimetro:
        if totalkm > x.PerimetroInicial:
            if totalkm < x.PerimetroFinal:
                porceperimetrorecebe = 100 + x.PerimetroCobra
                porceperimetropaga = 100 + x.PerimetroPaga
                break
    formhoracobra = ''
    formhoraexcede = ''
    despesas = parametrominutadespesa()
    itensminuta = MinutaItens.objects.filter(idMinuta=idmin, TipoItens='DESPESA').order_by('Descricao')
    veiculo = ''
    idveiculo = list(minuta.values('idVeiculo')[0].values())[0]
    if motorista_da_minuta:
        veiculo = Veiculo.objects.filter(idVeiculo=idveiculo)
    minuta_itens_fechada = MinutaItens.objects.filter(idMinuta=idmin).order_by('TipoItens', 'Descricao')
    """
    Criaremos um dict 'tabela_recebe_e_paga' com todas as informações para gerar a tabela de recebimento e 
    pagamento. A tabela será formada por 9 colunas sendo a primeira com as descrições (keys) e as demais divididas em 
    4 para recebimento e 4 para pagamento. 1ª Coluna - switch - 2ª Coluna dados das tabelas - 3ª Coluna dados da 
    minuta - 4ª Coluna para ostotais que serão executados no frontend.
    
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
    values_tabela_recebe = [list(tabelacliente.values('TaxaExpedicao')[0].values())[0], 0.23, valorporcentagemrecebe,
                            valorhorarecebe, 100, list(tabelaveiculo.values('KMCobra')[0].values())[0],
                            valorentrega_recebe, valorentregakg_recebe, valorentregavolume_recebe, valorsaidarecebe,
                            valorcapacidaderecebe, 100, 100, list(tabelacliente.values('AjudanteCobra')[0].values())[
                                0], 0]
    # Cria lista a receber para os labels dos inputs dos valores da minuta
    type_minuta_recebe = [None, 'R$', 'R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN', None]
    # Cria lista a receber para os inputs com os valores daminuta
    values_minuta_recebe = [None, totalvalornotas['totalvalor'], totalvalornotas['totalvalor'], minimohoras,
                            excedehoras, totalkm, totalquantidadenotas, totalpesonotas['totalpeso'],
                            totalvolumenotas['totalvolume'], None, None, 1000, 1000, total_de_ajudantes, None]
    # Cria lista a pagar para a descrições dos itens
    keys_paga = ['PORCENTAGEM DA NOTA', 'HORAS', 'HORAS EXCEDENTE', 'KILOMETRAGEM', 'ENTREGAS', 'ENTREGAS KG',
                 'ENTREGAS VOLUME', 'SAIDA', 'CAPACIDADE PESO', 'PERIMETRO', 'PERNOITE', 'AJUDANTE']
    # Cria lista a pagar para as descrições para usar nos atributos (Ex. id, name, class)
    keys_nome_paga = ['porcentagem', 'horas', 'horasexcede', 'kilometragem', 'entregas', 'entregaskg',
                      'entregasvolume', 'saida', 'capacidade', 'perimetro', 'pernoite', 'ajudante']
    # Cria lista a pagar para os labels dos inputs dos valores das tabelas do cliente
    type_tabela_paga = ['%', 'R$', '%', 'R$', 'R$', 'R$', 'R$', 'R$', 'R$', '%', '%', 'R$']
    # Cria lista a pagar para os inputs com os valores das tabelas do cliente
    values_tabela_paga = [valorporcentagempaga, valorhorapaga, 100, list(tabelaveiculo.values('KMPaga')[0].values())[
        0],valorentrega_paga, valorentregakg_paga, valorentregavolume_paga, valorsaidapaga, valorcapacidadepaga,
                          100, 100, list(tabelacliente.values('AjudantePaga')[0].values())[0]]
    # Cria lista a pagar para os labels dos inputs dos valores da minuta
    type_minuta_paga = ['R$', 'HS', 'HS', 'UN', 'UN', 'KG', 'UN', None, None, 'R$', 'R$', 'UN']
    # Cria lista a pagar para os inputs com os valores daminuta
    values_minuta_paga = [totalvalornotas['totalvalor'], minimohoras, excedehoras, totalkm, totalquantidadenotas,
                          totalpesonotas['totalpeso'], totalvolumenotas['totalvolume'], None, None, 1000, 1000, total_de_ajudantes]
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
        switch_recebe['perimetro'] = True
        switch_paga['perimetro'] = True
    if ajudantes_da_minuta:
        switch_recebe['ajudante'] = True
        switch_paga['ajudante'] = True
    # Altera os switchs a pagar para ligados conforme valores das tabelas dos cliente
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
        tabela_recebe_e_paga[str(item)]['name_tr'] = 'tabela_recebe'
        tabela_recebe_e_paga[str(item)]['value_tr'] = values_tabela_recebe[index]
        tabela_recebe_e_paga[str(item)]['class_tr'] = 'demonstrativo-input change-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['type_tr'] = 'number'
        tabela_recebe_e_paga[str(item)]['step_tr'] = '0.01'
        # Coluna 4 Recebe - tipo moeda ou tempo ou unidade ou kg
        tabela_recebe_e_paga[str(item)]['type_minuta_recebe'] = type_minuta_recebe[index]
        # Columa 4 Recebe - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_mr'] = 'mi-%s-recebe' % keys_nome_recebe[index]
        tabela_recebe_e_paga[str(item)]['name_mr'] = 'minuta_recebe'
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
        tabela_recebe_e_paga[str(item)]['name_tp'] = 'tabela_paga'
        tabela_recebe_e_paga[str(item)]['value_tp'] = values_tabela_paga[index]
        tabela_recebe_e_paga[str(item)]['class_tp'] = 'demonstrativo-input change-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['type_tp'] = 'number'
        tabela_recebe_e_paga[str(item)]['step_tp'] = '0.01'
        # Coluna 4 Paga - tipo moeda ou tempo ou unidade ou kg
        tabela_recebe_e_paga[str(item)]['type_minuta_paga'] = type_minuta_paga[index]
        # Columa 4 Paga - valores das tabelas
        tabela_recebe_e_paga[str(item)]['id_mp'] = 'mi-%s-paga' % keys_nome_paga[index]
        tabela_recebe_e_paga[str(item)]['name_mp'] = 'minuta_paga'
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
        'formhoracobra': formhoracobra,
        'formhoraexcede': formhoraexcede,
        'despesas': despesas,
        'itensminuta': itensminuta,
        'notasminuta': notasminuta,
        'nota_minuta_guia': notas_minuta_guia,
        'totalvalornotas': totalvalornotas,
        'totalpesonotas': totalpesonotas,
        'totalvolumenotas': totalvolumenotas,
        'totalquantidadenotas': totalquantidadenotas,
        'quantidade_notas_guia': quantidade_notas_guia,
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
    }
    return render(request, 'minutas/consultaminuta.html', contexto)


def criaminuta(request):
    # Numero inicial da minuta no sistema
    numerominuta = 7000
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
    minuta = Minuta.objects.get(idMinuta=idmin)
    contato = FoneContatoCliente.objects.filter(idCliente=minuta.idCliente)
    veiculo = ''
    if minuta.idVeiculo_id:
        veiculo = Veiculo.objects.get(idVeiculo=minuta.idVeiculo_id)
    colaboradores = MinutaColaboradores.objects.filter(idMinuta=idmin)
    motorista = ''
    ajudante = ''
    if colaboradores:
        motorista = MinutaColaboradores.objects.get(idMinuta=idmin,
                                                    Cargo='MOTORISTA')
        ajudante = MinutaColaboradores.objects.filter(idMinuta=idmin,
                                                      Cargo='AJUDANTE')
    response = HttpResponse(content_type='application/pdf')
    buffer = BytesIO()
    # Create the PDF object, using the BytesIO object as its "file."
    pdf = canvas.Canvas(buffer)
    # Draw things on the PDF. Here's where the PDF generation happens.
    # See the ReportLab documentation for the full list of functionality.

    # TODO Mostra regua - será excluida
    # pdf.setFont("Helvetica", 6)
    # for x in range(0, 300, 5):
    #     pdf.line(convertemp(0), convertemp(x), convertemp(4), convertemp(x))
    #     pdf.drawString(convertemp(0), convertemp(x), str(x))
    #
    # for x in range(0, 300, 2):
    #     pdf.line(convertemp(207), convertemp(x), convertemp(210), convertemp(x))
    # FIM DA REGUA

    pdf.roundRect(convertemp(10), convertemp(10), convertemp(190),
                  convertemp(277), 10)
    # ----
    pdf.drawImage('website/static/website/img/transportadora.jpg',
                  convertemp(12), convertemp(265), convertemp(40),
                  convertemp(20))
    pdf.setFont("Times-Bold", 18)
    pdf.drawString(convertemp(56), convertemp(279),
                   'TRANSEFETIVA TRANSPORTE - EIRELLI - ME')
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(57), convertemp(273),
                   'RUA GUARATINGUETÁ, 276 - MOOCA - SÃO PAULO - SP - CEP 03112-080')
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(70), convertemp(268),
                   '(11) 2305-0582 - (11) 2305-0583 - WHATSAPP (11) 94167-0583')
    pdf.drawString(convertemp(67), convertemp(263),
                   'e-mail: transefetiva@terra.com.br - operacional.efetiva@terra.com.br')
    pdf.line(convertemp(10), convertemp(260), convertemp(200), convertemp(260))
    # ----
    pdf.setFillColor(HexColor("#FFFFFF"))
    pdf.setStrokeColor(HexColor("#FFFFFF"))
    pdf.rect(convertemp(10), convertemp(254.1), convertemp(190),
             convertemp(5.6), fill=1, stroke=1)
    pdf.setStrokeColor(HexColor("#000000"))
    pdf.setFillColor(HexColor("#000000"))
    # ----
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(10), convertemp(255.8),
                   'ORDEM DE SERVIÇO Nº: ' + str(minuta.Minuta))
    pdf.drawRightString(convertemp(200), convertemp(255.8),
                        'DATA: ' + minuta.DataMinuta.strftime("%d/%m/%Y"))
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(10), convertemp(249), convertemp(95), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(57.5), convertemp(250.3),
                          'DADOS DO CLIENTE')
    # ----
    pdf.setFont("Times-Roman", 8)
    pdf.drawString(convertemp(11), convertemp(246),
                   'CLIENTE: ' + str(minuta.idCliente.Nome))
    endereco = minuta.idCliente.Endereco + ' - ' + minuta.idCliente.Bairro
    if len(endereco) > 45:
        pdf.drawString(convertemp(11), convertemp(242),
                       'ENDEREÇO: ' + endereco[0:45] + '...')
    else:
        pdf.drawString(convertemp(11), convertemp(242),
                       'ENDEREÇO: ' + minuta.idCliente.Endereco + ' - ' + minuta.idCliente.Bairro)
    pdf.drawString(convertemp(27), convertemp(238),
                   minuta.idCliente.Cidade + ' - ' + minuta.idCliente.Estado + ' - ' +
                   minuta.idCliente.CEP)
    pdf.drawString(convertemp(11), convertemp(234),
                   'INSCRIÇÃO CNPJ:' + minuta.idCliente.CNPJ)
    pdf.drawString(convertemp(11), convertemp(230),
                   'INSCRIÇÃO ESTADUAL: ' + minuta.idCliente.IE)
    if contato:
        pdf.drawString(convertemp(11), convertemp(226),
                       'CONTATO: ' + contato[0].Contato)
        pdf.drawString(convertemp(11), convertemp(222),
                       'TELEFONE: ' + contato[0].Fone)
    # ----
    pdf.line(convertemp(105), convertemp(249), convertemp(105),
             convertemp(217))
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(105), convertemp(249), convertemp(95), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(152.5), convertemp(250.3),
                          'DADOS DO SERVIÇO SOLICITADO')
    # ----
    pdf.setFont("Times-Roman", 8)
    y = 250
    if minuta.idCategoriaVeiculo:
        y -= 4
        pdf.drawString(convertemp(106), convertemp(y),
                       'VEÍCULO: ' + str(minuta.idCategoriaVeiculo))
        if veiculo:
            pdf.drawRightString(convertemp(199), convertemp(y),
                                'PLACA: ' + veiculo.Placa)
    if motorista:
        y -= 4
        pdf.drawString(convertemp(106), convertemp(y),
                       'MOTORISTA: ' + str(motorista.idPessoal))
    if ajudante:
        if ajudante.count() == 1:
            y -= 4
            pdf.drawString(convertemp(106), convertemp(y),
                           'AJUDANTE: ' + str(ajudante[0].idPessoal))
        else:
            for x in range(ajudante.count()):
                y -= 4
                if x == 0:
                    pdf.drawString(convertemp(106), convertemp(y),
                                   str(
                                       ajudante.count()) + ' AJUDANTES: ' + str(
                                       ajudante[x].idPessoal))
                else:
                    pdf.drawString(convertemp(126), convertemp(y),
                                   str(ajudante[x].idPessoal))
    if minuta.KMInicial:
        y -= 4
        pdf.drawString(convertemp(106), convertemp(y),
                       'KM Inicial: ' + str(minuta.KMInicial))
    y -= 4
    pdf.drawString(convertemp(106), convertemp(y), 'HORA INICIAL: '
                   + minuta.HoraInicial.strftime("%H:%M"))
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(10), convertemp(212), convertemp(95), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(57.5), convertemp(213.3),
                          'DESCRIÇÃO DO SERVIÇO EXECUTADO')
    # ----
    pdf.line(convertemp(105), convertemp(212), convertemp(105),
             convertemp(172))
    # TODO Excluido custo operacional da minuta 18/09/2020
    # pdf.setFont("Times-Roman", 10)
    # pdf.setFillColor(HexColor("#c1c1c1"))
    # pdf.rect(convertemp(105), convertemp(212), convertemp(95), convertemp(5), fill=1)
    # pdf.setFillColor(HexColor("#000000"))
    # pdf.drawCentredString(convertemp(152.5), convertemp(213.3), 'CUSTO OPERACIONAL')
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(10), convertemp(167), convertemp(190), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(105), convertemp(168.3),
                          'DESCRIÇÃO DOS SERVIÇOS')
    # ----
    pdf.setFont("Times-Roman", 10)
    pdf.setFillColor(HexColor("#c1c1c1"))
    pdf.rect(convertemp(10), convertemp(87), convertemp(190), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(105), convertemp(88.3),
                          'LOCAIS DE ENTREGAS E COLETAS')
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
    pdf.rect(convertemp(10), convertemp(69), convertemp(190), convertemp(5),
             fill=1)
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
    pdf.rect(convertemp(10), convertemp(51), convertemp(190), convertemp(5),
             fill=1)
    pdf.setFillColor(HexColor("#000000"))
    pdf.drawCentredString(convertemp(105), convertemp(52.3), 'KILOMETRAGEM')
    pdf.setFont("Times-Roman", 12)
    pdf.drawString(convertemp(11), convertemp(45.5), 'KM INICIAL: ')
    pdf.drawString(convertemp(106), convertemp(45.5), 'KM FINAL: ')
    # ----
    pdf.line(convertemp(10), convertemp(43), convertemp(200), convertemp(43))
    # ----
    pdf.roundRect(convertemp(12), convertemp(12), convertemp(101),
                  convertemp(19), 3)
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
    pdf.drawString(convertemp(118), convertemp(12),
                   'DATA, ASSINATURA E CARIMBO DO CLIENTE')

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


def fecha_minuta(request, idmin):
    """
    FUNÇÃO PARA INSERIR NA TABELA "MINUTAITENS" OS ITENS DE COBRANÇA E PAGAMENTO DA MINUTA.
    CHAMA A FUNÇÃO exclui_minuta_itens PARA APAGAR ITENS QUE ESTIVER COM VALOR 0.
    ALTERA O STATUS DA MINUTA PARA "FECHADA"
    RETORNA A PAGINA CONSULTA DA MINUTA

    :param request: request
    :param idmin: int :return:
    """
    dados_switch = request.POST.getlist('switch')
    descricao_recebe = request.POST.getlist('descricao-recebe')
    dados_valor_recebe = request.POST.getlist('valor-recebe')
    dados_descricao_paga = request.POST.getlist('descricao-paga')
    dados_valor_paga = request.POST.getlist('valor-paga')
    dados_descricao_despesa_recebe = request.POST.getlist(
        'descricao_despesa-recebe')
    dados_valor_despesa_recebe = request.POST.getlist('valor-despesa-recebe')
    dados_descricao_despesa_paga = request.POST.getlist(
        'descricao-despesa-paga')
    dados_valor_despesa_paga = request.POST.getlist('valor-despesa-paga')
    # print(dados_switch)
    # print(dados_valor_recebe)
    # print(dados_descricao_paga)
    # print(dados_valor_paga)
    # print(dados_descricao_despesa_recebe)
    # print(dados_valor_despesa_recebe)
    # print(dados_descricao_despesa_paga)
    # print(dados_valor_despesa_paga)

    # print(descricao_recebe)
    for itens in descricao_recebe:
        if 'sw-%s-recebe' % itens.lower().replace(' ', '') in dados_switch:
            descricao = itens
            valor = request.POST.get(
                'hi-%s-recebe' % itens.lower().replace(' ', ''))

            # print(descricao, valor)

    # print(request.POST)

    # if 'sw-taxaexpedicao-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[0:1],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[0:1],
    #         0,
    #         0.0,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-seguro-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[1:2],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[1:2],
    #         0,
    #         request.POST.get('tb-seguro-recebe'),
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-porcentagem-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[2:3],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[2:3],
    #         0,
    #         request.POST.get('tb-porcentagem-recebe'),
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-hora-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[3:4],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[3:4],
    #         0,
    #         0.00,
    #         request.POST.get('fa-hora-recebe'),
    #         idmin
    #     )
    # if 'sw-horasexcede-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[4:5],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[4:5],
    #         0,
    #         request.POST.get('fa-horasexcede-recebe'),
    #         request.POST.get('tb-horasexcede-recebe'),
    #         idmin
    #     )
    # if 'sw-km-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[5:6],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[5:6],
    #         request.POST.get('fa-km-recebe'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entrega-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[6:7],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[6:7],
    #         request.POST.get('fa-entrega-recebe'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entregakg-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[7:8],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[7:8],
    #         0,
    #         request.POST.get('fa-entregakg-recebe'),
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entregavolume-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[8:9],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[8:9],
    #         request.POST.get('fa-entregavolume-recebe'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-saida-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[9:10],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[9:10],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-capacidade-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[10:11],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[10:11],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-ajudante-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[11:12],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[11:12],
    #         request.POST.get('fa-ajudante-recebe'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-desconto-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_recebe[12:13],
    #         'RECEBE',
    #         'R',
    #         dados_valor_recebe[12:13],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-porcentagem-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[0:1],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[0:1],
    #         0,
    #         request.POST.get('tb-porcentagem-paga'),
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-hora-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[1:2],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[1:2],
    #         0,
    #         0.00,
    #         request.POST.get('fa-hora-paga'),
    #         idmin
    #     )
    # if 'sw-horasexcede-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[2:3],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[2:3],
    #         0,
    #         request.POST.get('fa-horasexcede-paga'),
    #         request.POST.get('tb-horasexcede-paga'),
    #         idmin
    #     )
    # if 'sw-km-recebe' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[3:4],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[3:4],
    #         request.POST.get('fa-km-paga'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entrega-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[4:5],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[4:5],
    #         request.POST.get('fa-entrega-paga'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entregakg-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[5:6],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[5:6],
    #         0,
    #         request.POST.get('fa-entregakg-paga'),
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-entregavolume-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[6:7],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[6:7],
    #         request.POST.get('fa-entregavolume-paga'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-saida-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[7:8],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[7:8],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-capacidade-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[8:9],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[8:9],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # if 'sw-ajudante-paga' in dados_switch:
    #     salvaminutaitens(
    #         dados_descricao_paga[9:10],
    #         'PAGA',
    #         'P',
    #         dados_valor_paga[9:10],
    #         request.POST.get('fa-ajudante-paga'),
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # for index, x in enumerate(dados_descricao_despesa_recebe, start=0):
    #     salvaminutaitens(
    #         dados_descricao_despesa_recebe[index:index+1],
    #         'DESPESA',
    #         'R',
    #         dados_valor_despesa_recebe[index:index+1],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # for index, x in enumerate(dados_descricao_despesa_paga, start=0):
    #     salvaminutaitens(
    #         dados_descricao_despesa_paga[index:index+1],
    #         'PAGA',
    #         'R',
    #         dados_valor_despesa_paga[index:index+1],
    #         0,
    #         0.00,
    #         '00:00',
    #         idmin
    #     )
    # minuta_itens = MinutaItens.objects.filter(idMinuta_id=idmin)
    # for itens in minuta_itens:
    #     if itens.Valor == 0:
    #         excluiminutaitens(itens.idMinutaItens)
    # altera_status_minuta('FECHADA', idmin)
    return redirect('consultaminuta', idmin)


def estorna_minuta(request, idmin):
    minuta = get_object_or_404(Minuta, idMinuta=idmin)
    if minuta.StatusMinuta == 'ABERTA':
        pass
    elif minuta.StatusMinuta == 'FECHADA':
        altera_status_minuta('ABERTA', idmin)
        itens_minuta_recebe_excluir = MinutaItens.objects.filter(
            idMinuta=idmin).filter(TipoItens='RECEBE')
        for itens in itens_minuta_recebe_excluir:
            excluiminutaitens(itens.idMinutaItens)
        itens_minuta_paga_excluir = MinutaItens.objects.filter(
            idMinuta=idmin).filter(TipoItens='PAGA')
        for itens in itens_minuta_paga_excluir:
            excluiminutaitens(itens.idMinutaItens)
    return redirect('index_minuta')


def criaminutamotorista(request):
    if request.method == 'POST':
        idminuta = request.POST.get('idMinuta')
        form = CadastraMinutaMotorista(request.POST)
        # Altera field idVeiculo conforme motorista escolhido
        veiculo = Veiculo.objects.filter(
            Motorista=request.POST.get('idPessoal'))
        if veiculo.count() == 1:
            minuta = get_object_or_404(Minuta, idMinuta=idminuta)
            obj = Minuta()
            obj.idMinuta = minuta.idMinuta
            obj.Minuta = minuta.Minuta
            obj.DataMinuta = minuta.DataMinuta
            obj.HoraInicial = minuta.HoraInicial
            obj.HoraFinal = minuta.HoraFinal
            obj.Coleta = minuta.Coleta
            obj.Entrega = minuta.Entrega
            obj.Obs = minuta.Obs
            obj.StatusMinuta = minuta.StatusMinuta
            obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
            obj.idCliente = minuta.idCliente
            for x in veiculo:
                idveiculo = x.idVeiculo
            obj.idVeiculo_id = idveiculo
            obj.save()
    else:
        idminuta = request.GET.get('idminuta')
        form = CadastraMinutaMotorista(
            initial={'idMinuta': idminuta, 'Cargo': 'MOTORISTA'})
    return salva_form(request, form, 'minutas/criaminutamotorista.html',
                      idminuta)


def excluiminutamotorista(request, idmincol):
    motoristaminuta = get_object_or_404(MinutaColaboradores,
                                        idMinutaColaboradores=idmincol)
    # cliente = Cliente.objects.get(Nome=tabelacapacidade.idCliente)
    data = dict()
    if request.method == "POST":
        motoristaminuta.delete()
        # Altera field idVeiculo para null
        minuta = get_object_or_404(Minuta,
                                   idMinuta=motoristaminuta.idMinuta_id)
        obj = Minuta()
        obj.idMinuta = minuta.idMinuta
        obj.Minuta = minuta.Minuta
        obj.DataMinuta = minuta.DataMinuta
        obj.HoraInicial = minuta.HoraInicial
        obj.HoraFinal = minuta.HoraFinal
        obj.Coleta = minuta.Coleta
        obj.Entrega = minuta.Entrega
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
        form = CadastraMinutaAjudante(
            initial={'idMinuta': idminuta, 'Cargo': 'AJUDANTE'})
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
            obj = Minuta()
            obj.idMinuta = form.cleaned_data['idMinuta']
            obj.Minuta = minuta.Minuta
            obj.DataMinuta = minuta.DataMinuta
            obj.HoraInicial = minuta.HoraInicial
            obj.HoraFinal = minuta.HoraFinal
            obj.Coleta = minuta.Coleta
            obj.Entrega = minuta.Entrega
            obj.Obs = minuta.Obs
            obj.StatusMinuta = minuta.StatusMinuta
            obj.idCategoriaVeiculo = minuta.idCategoriaVeiculo
            obj.idCliente = minuta.idCliente
            obj.idVeiculo_id = form.cleaned_data['Veiculo']
            obj.save()
    else:
        form = CadastraMinutaVeiculo(
            initial={'idMinuta': idmin, 'Veiculo': minuta.idVeiculo_id})
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
        form = CadastraMinutaNota(request.POST)
    else:
        idminuta = request.GET.get('idminuta')
        form = CadastraMinutaNota(initial={'idMinuta': idminuta})
    return salva_form(request, form, 'minutas/criaminutaentrega.html',
                      idminuta)


def editaminutaentrega(request, idminent):
    notaminuta = get_object_or_404(MinutaNotas, idMinutaNotas=idminent)
    data = dict()
    if request.method == 'POST':
        form = CadastraMinutaNota(request.POST, instance=notaminuta)
        if form.is_valid():
            form.save()
        return redirect('consultaminuta', notaminuta.idMinuta_id)
    else:
        form = CadastraMinutaNota(instance=notaminuta)
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
        data['html_form'] = render_to_string(
            'minutas/excluiminutaentrega.html', context, request=request)
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
    # print(listaveiculo)
    data['html_form'] = render_to_string(
        'minutas/editaminutaveiculolista.html', context, request=request)
    return JsonResponse(data)


def criaminutaparametrodespesa(request):
    data = dict()
    if request.method == 'POST':
        try:
            arquivo_json = open('parametros.json', 'r')
            dados_json = json.load(arquivo_json)
            arquivo_json.close()
            despesas = dados_json['Despesa']['Descricao']
            if request.POST.get('Despesa') in despesas:
                pass
            else:
                despesas.append(request.POST.get('Despesa').upper())
                try:
                    arquivo_json = open('parametros.json', 'w')
                    dados_json['Despesa']['Descricao'] = despesas
                    dados_json = json.dumps(dados_json, indent=4,
                                            sort_keys=True)
                    arquivo_json.write(dados_json)
                    arquivo_json.close()
                except Exception as erro:
                    print(erro)
        except Exception as erro:
            print(erro)
        return redirect('consultaminuta', request.POST.get('idMinuta'))
    else:
        form = CadastraMinutaParametroDespesa(
            initial={'idMinuta': request.GET.get('idminuta')})
    context = {'form': form}
    data['html_form'] = render_to_string(
        'minutas/criaminutaparametrodespesa.html', context, request=request)
    return JsonResponse(data)


def salva_form(request, form, template_name, idmin):
    data = dict()
    numerominuta = 0
    numeroidminuta = form.instance
    print('PO')
    print(numeroidminuta)
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
            return redirect('consultaminuta', idmin, {'formkmfinal', form})
    context = {'form': form, 'numerominuta': numerominuta, 'numeroidminuta': numeroidminuta}
    data['html_form'] = render_to_string(template_name, context, request=request)
    return JsonResponse(data)
