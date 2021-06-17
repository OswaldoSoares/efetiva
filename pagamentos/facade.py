import calendar
import datetime
from decimal import Decimal

from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Sum, Max, Min, F, ExpressionWrapper, DecimalField
from django.http import JsonResponse
from django.template.loader import render_to_string

from minutas.models import MinutaColaboradores, MinutaItens
from pagamentos.models import Recibo
from pessoas import facade
from pessoas.forms import CadastraContraCheque, CadastraContraChequeItens, CadastraVale
from pessoas.models import ContraCheque, ContraChequeItens, CartaoPonto, Salario, Vales

meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO',
         'NOVEMBRO', 'DEZEMBRO']

dias = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']



def cria_contexto_pagamentos():
    formvales = CadastraVale()
    contexto = {'formvales': formvales}
    return contexto


def create_context(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    folha = {}
    referencia = {'MesReferencia': mesreferencia, 'AnoReferencia': anoreferencia}
    totalsalario = 0.00
    totalfolha = 0.00
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia)-1]
    for itens in mensalistas:
        folha[itens.Nome] = {'Salario': '0,00', 'Liquido': '0,00', 'ContraCheque': False, 'CartaoPonto': False,
                             'idPessoal': itens.idPessoal}
        salario = get_salario(itens.idPessoal)
        totalsalario += float(salario[0].Salario)
        folha[itens.Nome]['Salario'] = salario[0].Salario
        contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, itens.idPessoal)
        if contracheque:
            totais = saldo_contracheque(contracheque[0].idContraCheque)
            folha[itens.Nome]['Liquido'] = totais['Liquido']
            totalfolha += float(totais['Liquido'])
        if busca_contracheque(mes, anoreferencia, itens.idPessoal):
            folha[itens.Nome]['ContraCheque'] = True
        if busca_cartaoponto_referencia(mesreferencia, anoreferencia, itens.idPessoal):
            folha[itens.Nome]['CartaoPonto'] = True
    totalsalario = '{0:.2f}'.format(totalsalario).replace('.', ',')
    totalfolha = '{0:.2f}'.format(totalfolha).replace('.', ',')
    contexto = {'folha': folha, 'referencia': referencia, 'totalsalario': totalsalario, 'totalfolha': totalfolha}
    return contexto


def create_context_formcontracheque():
    formcontracheque = CadastraContraCheque()
    contexto = {'formcontracheque': formcontracheque}
    return contexto


def create_context_avulso():
    periodo = get_periodo_pagamento_avulsos()
    saldo = get_saldo_pagamento_avulso(periodo['DataInicial'], periodo['DataFinal'])
    contexto = {'periodo': periodo, 'saldo': saldo}
    return contexto


def get_periodo_pagamento_avulsos():
    periodo = MinutaColaboradores.objects.filter(Pago=False).exclude(idPessoal__TipoPgto='MENSALISTA').aggregate(
        DataInicial=Min('idMinuta__DataMinuta'), DataFinal=Max('idMinuta__DataMinuta'))
    periodo['DataInicial'] = periodo['DataInicial'].strftime('%Y-%m-%d')
    periodo['DataFinal'] = periodo['DataFinal'].strftime('%Y-%m-%d')
    return periodo


def get_saldo_pagamento_avulso(datainicial, datafinal):
    saldo = []
    avulsos = list_avulsos_ativo()
    saldo_total = 0
    saldo_vales = 0
    total_select = 0
    for colaboradores in avulsos:
        colaborador = MinutaColaboradores.objects.filter(idPessoal__Nome=colaboradores.Nome, Pago=False)
        saldo_colaborador = 0
        for index, itens in enumerate(colaborador):
            if itens.Cargo == 'AJUDANTE':
                base_valor = ExpressionWrapper(F('Valor') / F('Quantidade'), output_field=DecimalField())
                ajudante = MinutaItens.objects.values(ValorAjudante=base_valor).filter(
                    TipoItens='PAGA', idMinuta=itens.idMinuta, Descricao='AJUDANTE', idMinuta_id__DataMinuta__range=[
                        datainicial, datafinal])
                if ajudante:
                    saldo_colaborador += ajudante[0]['ValorAjudante']
                    saldo_total += ajudante[0]['ValorAjudante']
            elif itens.Cargo == 'MOTORISTA':
                motorista = MinutaItens.objects.filter(TipoItens='PAGA', idMinuta=itens.idMinuta,
                                                       idMinuta_id__DataMinuta__range=[
                        datainicial, datafinal]).exclude(Descricao='AJUDANTE').aggregate(ValorMotorista=Sum('Valor'))
                if motorista['ValorMotorista']:
                    saldo_colaborador += motorista['ValorMotorista']
                    saldo_total += motorista['ValorMotorista']
        total_vales = calcula_total_vales(colaboradores.idPessoal)
        if not total_vales:
            total_vales = 0
        saldo_vales += total_vales
        dict_vale, saldo_vales_select = get_vales_select(colaboradores.idPessoal, 0)
        total_select += saldo_vales_select
        if saldo_colaborador > 0 or total_vales > 0:
            saldo.append({'Nome': colaboradores.Nome, 'idPessoal': colaboradores.idPessoal, 'Saldo': saldo_colaborador,
                          'ValeSelect': saldo_vales_select, 'ValeTotal': total_vales})
    return saldo, saldo_total, saldo_vales, total_select


def get_vales_select(idpessoal, idcontracheque):
    dict_vale = dict()
    vale = Vales.objects.filter(idPessoal=idpessoal, Pago=False)
    for itens in vale:
        dict_vale['id{}'.format(itens.idVales)] = {'idVales': itens.idVales, 'Data': itens.Data,
                                                   'Descricao': itens.Descricao, 'Valor': itens.Valor, 'Checked': True}
    content_descricao = None
    saldo_vales_select = 0
    for itens in dict_vale:
        if dict_vale[itens]['Descricao'][-9:] == 'PARCELADO':
            if content_descricao == None:
                dict_vale[itens]['Checked'] = True
            if content_descricao == dict_vale[itens]['Descricao'][0:-16]:
                dict_vale[itens]['Checked'] = False
            content_descricao = dict_vale[itens]['Descricao'][0:-16]
        if busca_contracheque_itens_vale(dict_vale[itens]['idVales']):
            dict_vale[itens]['Checked'] = True
        if idcontracheque > 0:
            if dict_vale[itens]['Checked']:
                if not busca_contracheque_itens_vale(dict_vale[itens]['idVales']):
                    create_contracheque_itens_vales(idpessoal, dict_vale[itens]['idVales'], idcontracheque)
        if dict_vale[itens]['Checked']:
            saldo_vales_select += dict_vale[itens]['Valor']
    return dict_vale, saldo_vales_select


def get_vale_id(idvales):
    vale = Vales.objects.get(idVales=idvales)
    return vale


def calcula_total_vales(idpessoal):
    totalvales = Vales.objects.filter(idPessoal=idpessoal, Pago=False).aggregate(ValorTotal=Sum('Valor'))
    return totalvales['ValorTotal']


def seleciona_minutasavulso(datainicial, datafinal, idpessoal):
    data = dict()
    data['html_minutas'] = html_minutasavulso(datainicial, datafinal, idpessoal)
    data['html_valesavulso'] = html_vale(idpessoal, 'avulso', 0)
    c_return = JsonResponse(data)
    return c_return


def html_minutasavulso(datainicial, datafinal, idpessoal):
    recibo = []
    colaborador = facade.get_pessoal(idpessoal)
    minutas = MinutaColaboradores.objects.filter(idPessoal=idpessoal, Pago=False,
                                                 idMinuta_id__DataMinuta__range=[datainicial, datafinal])
    for index, itens in enumerate(minutas):
        if itens.Cargo == 'AJUDANTE':
            minutaitens = MinutaItens.objects.filter(TipoItens='PAGA', idMinuta=itens.idMinuta, Descricao='AJUDANTE',
                                                     idMinuta_id__DataMinuta__range=[datainicial, datafinal])
            if minutaitens:
                recibo.append({'Data': itens.idMinuta.DataMinuta, 'Minuta': itens.idMinuta.Minuta,
                               'Cliente': itens.idMinuta.idCliente.Fantasia, 'Descricao': minutaitens[0].Descricao,
                               'Valor': minutaitens[0].ValorBase})
        elif itens.Cargo == 'MOTORISTA':
            minutaitens = MinutaItens.objects.filter(TipoItens='PAGA', idMinuta=itens.idMinuta,
                                                     idMinuta_id__DataMinuta__range=[datainicial, datafinal]).exclude(
                Descricao='AJUDANTE')
            for minutas in minutaitens:
                recibo.append({'Data': itens.idMinuta.DataMinuta, 'Minuta': itens.idMinuta.Minuta,
                               'Cliente': itens.idMinuta.idCliente.Fantasia, 'Descricao': minutas.Descricao,
                               'Valor': minutas.Valor})
    context = {'recibo': recibo, 'colaborador': colaborador, 'datainicial': datainicial, 'datafinal': datafinal}
    c_return = render_to_string('pagamentos/minutasavulso.html', context)
    return c_return


def create_folha(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    for itens in mensalistas:
        create_contracheque(mesreferencia, anoreferencia, '0.00', itens.idPessoal)
        create_cartaoponto(mesreferencia, anoreferencia, itens.idPessoal)


def create_pagamento_avulso(datainicial, datafinal, idpessoal, vales):
    minutas = MinutaColaboradores.objects.filter(idMinutaidPessoal=idpessoal, Pago=False,
                                                 idMinuta_id__DataMinuta__range=[datainicial, datafinal])
    total_vales = 0
    for itens in vales:
        vale = Vales.objects.get(idVales=itens[3:-5])
        total_vales += vale.Valor
        obj = vale
        obj.Pago = True
        # obj.save(update_fields=['Pago'])
    recibo = Recibo.objects.annotate(Maior=Max('idRecibo') + 1)
    if not recibo:
        recibo = 1431
    else:
        recibo = recibo.Maior


    pass


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            salario = get_salario(idpessoal)
            if not busca_contracheque(meses[int(mesreferencia)-1], anoreferencia, idpessoal):
                obj = ContraCheque()
                obj.MesReferencia = meses[int(mesreferencia)-1]
                obj.AnoReferencia = anoreferencia
                obj.Valor = valor
                obj.idPessoal_id = idpessoal
                obj.save()
                create_contracheque_itens('SALARIO', salario[0].Salario, '30', 'C', obj.idContraCheque)


def create_contracheque_itens(descricao, valor, referencia, registro, idcontracheque):
    if float(valor) > 0:
        saldo = saldo_contracheque(idcontracheque)
        if int(valor) < int(saldo['Liquido']) or descricao == 'SALARIO':
            if not busca_contrachequeitens(idcontracheque, descricao, registro):
                obj = ContraChequeItens()
                obj.Descricao = descricao
                obj.Valor = valor
                obj.Referencia = referencia
                obj.Registro = registro
                obj.idContraCheque_id = idcontracheque
                obj.save()


def create_contracheque_itens_vales(idcliente, idvale, idcontracheque):
    vale = get_vale_id(idvale)
    if not busca_contracheque_itens_vale(idvale):
        obj = ContraChequeItens()
        if vale.Descricao[-9:] == 'PARCELADO':
            obj.Descricao = vale.Descricao[0:-10]
            obj.Referencia = vale.Descricao[-15:-9]
        else:
            obj.Descricao = vale.Descricao
        obj.Valor = vale.Valor
        obj.Registro = 'D'
        obj.idContraCheque_id = idcontracheque
        obj.Vales_id = idvale
        obj.save()


def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    colaborador = facade.get_pessoal(idpessoal)
    admissao = colaborador[0].DataAdmissao
    if int(anoreferencia) >= admissao.year:
        if int(mesreferencia) >= admissao.month:
            admissao = datetime.datetime(admissao.year, admissao.month, admissao.day)
            if not busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
                referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
                for x in range(1, referencia[1]+1):
                    dia = '{}-{}-{}'.format(anoreferencia, mesreferencia, x)
                    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
                    obj = CartaoPonto()
                    obj.Dia = dia
                    obj.Entrada = '07:00'
                    obj.Saida = '17:00'
                    if dia.weekday() == 5 or dia.weekday() == 6:
                        obj.Ausencia = dias[dia.weekday()]
                    else:
                        obj.Ausencia = ''
                    if dia < admissao:
                        obj.Ausencia = '-------'
                    obj.idPessoal_id = idpessoal
                    obj.save()
                atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal)


def cria_vale(data, descricao, valor, parcelas, idpessoal):
    if int(parcelas) > 0:
        for x in range(int(parcelas)):
            obj = Vales()
            obj.Data = data
            if int(parcelas) == 1:
                obj.Descricao = descricao
            else:
                obj.Descricao = '{} {}/{} PARCELADO'.format(descricao, str(x+1).zfill(2), parcelas.zfill(2))
            obj.Valor = float(valor)/int(parcelas)
            obj.idPessoal_id = idpessoal
            obj.save()


def get_contracheque(idpessoal: int):
    contracheque = ContraCheque.objects.filter(idPessoal=idpessoal)
    return contracheque


def get_contrachequeid(idcontracheque: int):
    contracheque = ContraCheque.objects.filter(idContraCheque=idcontracheque)
    return contracheque


def get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia)-1]
    contracheque = ContraCheque.objects.filter(MesReferencia=mes, AnoReferencia=anoreferencia,
                                               idPessoal=idpessoal)
    return contracheque


def get_contrachequeitens(idcontracheque, descricao, registro):
    try:
        contrachequeitens = ContraChequeItens.objects.get(idContraCheque=idcontracheque, Descricao=descricao,
                                                          Registro=registro)
    except ObjectDoesNotExist:
        contrachequeitens = None
    return contrachequeitens


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


def get_cartaopontoid(idcartaoponto):
    cartaoponto = CartaoPonto.objects.get(idCartaoPonto=idcartaoponto)
    return cartaoponto


def busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = meses.index(mesreferencia)+1
    else:
        mes = int(mesreferencia)
    dia = '{}-{}-{}'.format(anoreferencia, mes, 1)
    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
    referencia = calendar.monthrange(int(anoreferencia), mes)
    diafinal = '{}-{}-{}'.format(anoreferencia, mes, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, '%Y-%m-%d')
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    if cartaoponto:
        return cartaoponto


def busca_contracheque(mesreferencia, anoreferencia, idpessoal):
    qs_contracheque = ContraCheque.objects.filter(MesReferencia=mesreferencia, AnoReferencia=anoreferencia,
                                                  idPessoal=idpessoal)
    if qs_contracheque:
        return True


def busca_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=idcontracheque, Descricao=descricao,
                                                         Registro=registro)
    return contrachequeitens


def busca_contracheque_itens_vale(idvale):
    contracheque_itens_vale = ContraChequeItens.objects.filter(Vales_id=idvale)
    if contracheque_itens_vale:
        return True


def busca_adiantamento(idcontracheque):
    if ContraChequeItens.objects.filter(idContraCheque=idcontracheque, Descricao='ADIANTAMENTO', Registro='D'):
        return True
    else:
        return False


def delete_contrachequeitens(idcontracheque, descricao, registro):
    contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=idcontracheque, Descricao=descricao,
                                                         Registro=registro)
    contrachequeitens.delete()


def delete_contracheque_itens_vale(idvale):
    contracheque_itens_vale = ContraChequeItens.objects.filter(Vales_id=idvale)
    print(idvale)
    contracheque_itens_vale.delete()


def seleciona_folha(mesreferencia, anoreferencia):
    data = dict()
    data['html_folha'] = html_folha(mesreferencia, anoreferencia)
    c_return = JsonResponse(data)
    return c_return


def seleciona_contracheque(mesreferencia, anoreferencia, idpessoal, request):
    data = dict()
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    data['html_folha'] = html_folha(mesreferencia, anoreferencia)
    data['html_minutascontracheque'] = html_minutascontracheque(mesreferencia,  anoreferencia, idpessoal)
    data['html_vales'] = html_vale(idpessoal, 'mensalista', contracheque[0].idContraCheque)
    data['html_formccitens'] = html_formccitens(contracheque, request)
    data['html_formccadianta'] = html_formccadianta(contracheque, request)
    data['html_adiantamento'] = busca_adiantamento(contracheque[0].idContraCheque)
    data['html_contracheque'] = html_contracheque(mesreferencia, anoreferencia, idpessoal)
    data['html_cartaoponto'] = html_cartaoponto(mesreferencia,  anoreferencia, idpessoal)
    c_return = JsonResponse(data)
    return c_return


def seleciona_saldoavulso(datainicial, datafinal):
    data = dict()
    data['html_saldoavulso'] = html_saldoavulso(datainicial, datafinal)
    c_return = JsonResponse(data)
    return c_return


def periodo_cartaoponto(mesreferencia, anoreferencia):
    if mesreferencia in meses:
        mesreferencia = meses.index(mesreferencia)+1
    dia = '{}-{}-{}'.format(anoreferencia, mesreferencia, 1)
    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
    referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
    diafinal = '{}-{}-{}'.format(anoreferencia, mesreferencia, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, '%Y-%m-%d')
    return dia, diafinal


def seleciona_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    context = {'cartaoponto': cartaoponto, 'mesreferencia': mesreferencia, 'anoreferencia': anoreferencia,
               'idpessoal': idpessoal}
    return render_to_string('pagamentos/cartaoponto.html', context)


def seleciona_vales(idpessoal):
    data = dict()
    colaborador = facade.get_pessoal(idpessoal)
    if colaborador[0].TipoPgto == 'MENSALISTA':
        data['html_vales'] = html_vale(idpessoal, 'mensalista', 0)
    else:
        data['html_valesavulso'] = html_vale(idpessoal, 'avulso', 0)
    c_return = JsonResponse(data)
    return c_return


def select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    minutas = MinutaColaboradores.objects.filter(idPessoal=idpessoal,
                                                 idMinuta_id__DataMinuta__range=(dia, diafinal)).order_by(
                                                 'idMinuta_id__DataMinuta').values('idMinuta_id__DataMinuta',
                                                                                   'idMinuta_id__Minuta',
                                                                                   'idMinuta_id__idCliente__Fantasia',
                                                                                   'idMinuta_id__HoraInicial',
                                                                                   'idMinuta_id__HoraFinal',
                                                                                   'idPessoal')
    return minutas


def html_minutascontracheque(mesreferencia, anoreferencia, idpessoal):
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    context = {'minutas': minutas, 'idPessoal': idpessoal}
    c_return = render_to_string('pagamentos/minutascontracheque.html', context)
    return c_return


def atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    for x in minutas:
        cartaoponto = CartaoPonto.objects.get(Dia=x['idMinuta_id__DataMinuta'], idPessoal_id=x['idPessoal'])
        obj = cartaoponto
        horasaida = datetime.datetime.strptime('17:00:00', '%H:%M:%S').time()
        if obj.Alteracao == 'ROBOT' and obj.Ausencia != 'FALTA':
            if x['idMinuta_id__HoraFinal'] != obj.Saida:
                if x['idMinuta_id__HoraFinal'] > horasaida:
                    obj.Saida = x['idMinuta_id__HoraFinal']
                    obj.save(update_fields=['Saida'])
    totalextra = calcula_horas_extras(mesreferencia, anoreferencia, idpessoal)
    calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
    return totalextra


def altera_horario_manual(idcartaoponto, horaentrada, horasaida):
    obj = get_cartaopontoid(idcartaoponto)
    obj.Entrada = horaentrada
    obj.Saida = horasaida
    obj.save(update_fields=['Entrada', 'Saida'])


def altera_contracheque_itens(contrachequeitens, valorhoraextra, referencia):
    if float(valorhoraextra) > 0:
        obj = contrachequeitens
        obj.Valor = valorhoraextra
        obj.Referencia = referencia
        obj.save(update_fields=['Valor', 'Referencia'])


def altera_falta(mesreferencia, anoreferencia, idpessoal, idcartaoponto, request):
    data = dict()
    cartaoponto = CartaoPonto.objects.get(idCartaoPonto=idcartaoponto)
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    obj = cartaoponto
    if obj.Ausencia == 'FALTA':
        obj.Ausencia = ''
        obj.Alteracao = 'ROBOT'
    else:
        obj.Ausencia = 'FALTA'
        obj.Alteracao = 'ROBOT'
    obj.Entrada = '07:00:00'
    obj.Saida = '17:00:00'
    obj.save(update_fields=['Ausencia', 'Alteracao', 'Entrada', 'Saida'])
    calcula_faltas(mesreferencia, anoreferencia, idpessoal)
    atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal)
    calcula_conducao(mesreferencia, anoreferencia, idpessoal)
    data['html_adiantamento'] = busca_adiantamento(contracheque[0].idContraCheque)
    data['html_folha'] = html_folha(mesreferencia, anoreferencia)
    data['html_contracheque'] = html_contracheque(mesreferencia, anoreferencia, idpessoal)
    data['html_cartaoponto'] = html_cartaoponto(mesreferencia, anoreferencia, idpessoal)
    data['html_formccadianta'] = html_formccadianta(contracheque, request)
    data['html_formccitens'] = html_formccitens(contracheque, request)
    data['html_minutascontracheque'] = html_minutascontracheque(mesreferencia, anoreferencia, idpessoal)
    data['html_vales'] = html_vale(idpessoal, 'mensalista', contracheque[0].idContraCheque)
    c_return = JsonResponse(data)
    return c_return


def html_folha(mesreferencia, anoreferencia):
    contexto = create_context(mesreferencia, anoreferencia)
    c_return = render_to_string('pagamentos/folhapgto.html', contexto)
    return c_return


def html_contracheque(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia) - 1]
    contracheque = ContraCheque.objects.filter(MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal)
    contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque).order_by(
        'Registro')
    totais = saldo_contracheque(contracheque[0].idContraCheque)
    context = {'qs_contracheque': contracheque, 'qs_contrachequeitens': contrachequeitens, 'totais': totais,
               'mesreferencia': mesreferencia, 'anoreferencia': anoreferencia}
    c_return = render_to_string('pagamentos/contracheque.html', context)
    return c_return


def html_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    context = {'cartaoponto': cartaoponto, 'mesreferencia': mesreferencia, 'anoreferencia': anoreferencia,
               'idpessoal': idpessoal}
    c_return = render_to_string('pagamentos/cartaoponto.html', context)
    return c_return


def html_vale(idpessoal, tipopgto, idcontracheque):
    dict_vale, saldo_vale_select = get_vales_select(idpessoal, idcontracheque)
    # print(dict_vale)
    # for x in dict_vale.items():
    #     print(x[1]['Descricao'])
    context = {'dict_vale': dict_vale, 'idPessoal': idpessoal, 'TipoPgto': tipopgto, 'idcontracheque': idcontracheque}
    c_return = render_to_string('pagamentos/vale.html', context)
    return c_return


def print_contracheque_context(idcontracheque, mesreferencia, anoreferencia, idpessoal):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = facade.get_contracheque_itens(idcontracheque)
    colaborador = facade.get_pessoal(contracheque[0].idPessoal_id)
    minutas = select_minutas_contracheque(mesreferencia, anoreferencia, idpessoal)
    credito = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque,
                                               Registro='C').aggregate(Total=Sum('Valor'))
    debito = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque,
                                              Registro='D').aggregate(Total=Sum('Valor'))

    if not credito['Total']:
        credito['Total'] = Decimal('0.00')
    if not debito['Total']:
        debito['Total'] = Decimal('0.00')
    totais = {'Credito': credito['Total'], 'Debito': debito['Total'], 'Liquido': credito['Total'] - debito['Total']}
    contexto = {'contracheque': contracheque, 'contrachequeitens': contrachequeitens, 'colaborador': colaborador,
                'totais': totais, 'minutas': minutas}
    return contexto


def html_formccadianta(contracheque, request):
    formcontrachequeitens = CadastraContraChequeItens()
    contextform = {'formcontrachequeitens': formcontrachequeitens, 'contracheque': contracheque}
    c_return = render_to_string('pagamentos/contrachequeadianta.html', contextform, request=request)
    return c_return


def html_formccitens(contracheque, request):
    formcontrachequeitens = CadastraContraChequeItens()
    contextform = {'formcontrachequeitens': formcontrachequeitens, 'contracheque': contracheque}
    c_return = render_to_string('pagamentos/contrachequeitens.html', contextform, request=request)
    return c_return


def html_saldoavulso(datainicial, datafinal):
    saldo, saldototal, saldovales, totalselect = get_saldo_pagamento_avulso(datainicial, datafinal)
    context = {'saldo': saldo, 'saldototal': saldototal, 'saldovales': saldovales,  'totalselect': totalselect,
               'datainicial': datainicial, 'datafinal': datafinal}
    c_return = render_to_string('pagamentos/saldoavulso.html', context)
    return c_return


def calcula_faltas(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    faltas = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal, Ausencia='FALTA').count()
    salario = get_salario(idpessoal)
    desconto = float(salario[0].Salario)/30*int(faltas)*2
    salario = float(salario[0].Salario) - desconto
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    contrachequeitens = get_contrachequeitens(contracheque[0].idContraCheque, 'SALARIO', 'C')
    altera_contracheque_itens(contrachequeitens, salario, '{}d'.format(30-faltas))


def calcula_horas_extras(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalextra = total_horas_extras(mesreferencia, anoreferencia, idpessoal)

    horazero = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraextra = float(salario[0].Salario) / 100 * 150 / 30 / 9 / 60 / 60 * totalextra.seconds
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    if totalextra > horazero:
        if contracheque:
            contrachequeitens = get_contrachequeitens(contracheque[0].idContraCheque, 'HORA EXTRA', 'C')
            if contrachequeitens:
                altera_contracheque_itens(contrachequeitens, valorhoraextra, totalextra)
            else:
                if valorhoraextra > 0:
                    create_contracheque_itens('HORA EXTRA', valorhoraextra,
                                              totalextra.strptime('00:00:00', '%H:%M').time(),
                                              'C', contracheque[0].idContraCheque)
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, 'HORA EXTRA', 'C')
    return totalextra


def total_horas_extras(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    totalextra = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horasaidapadrao = datetime.datetime.strptime('17:00:00', '%H:%M:%S').time()
        horasaidapadrao = datetime.timedelta(hours=horasaidapadrao.hour, minutes=horasaidapadrao.minute)
        horasaidareal = datetime.timedelta(hours=x.Saida.hour, minutes=x.Saida.minute)
        if horasaidareal > horasaidapadrao:
            totalextra += horasaidareal - horasaidapadrao
    return totalextra


def calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    salario = get_salario(idpessoal)
    totalatrazo = total_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
    horazero = datetime.datetime.strptime('00:00:00', '%H:%M:%S').time()
    horazero = datetime.timedelta(hours=horazero.hour, minutes=horazero.minute)
    valorhoraatrazo = float(salario[0].Salario) / 30 / 9 / 60 / 60 * totalatrazo.seconds
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    if totalatrazo > horazero:
        if contracheque:
            contrachequeitens = get_contrachequeitens(contracheque[0].idContraCheque, 'ATRAZO', 'D')
            if contrachequeitens:
                altera_contracheque_itens(contrachequeitens, valorhoraatrazo, totalatrazo)
            else:
                if valorhoraatrazo > 0:
                    create_contracheque_itens('ATRAZO', valorhoraatrazo, totalatrazo, 'D',
                                              contracheque[0].idContraCheque)
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, 'ATRAZO', 'D')
    return totalatrazo


def total_horas_atrazo(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    totalatrazo = datetime.timedelta(hours=0, minutes=0)
    for x in cartaoponto:
        horaentradapadrao = datetime.datetime.strptime('07:00:00', '%H:%M:%S').time()
        horaentradapadrao = datetime.timedelta(hours=horaentradapadrao.hour, minutes=horaentradapadrao.minute)
        horaentradareal = datetime.timedelta(hours=x.Entrada.hour, minutes=x.Entrada.minute)
        if horaentradareal > horaentradapadrao:
            totalatrazo += horaentradareal - horaentradapadrao
    return totalatrazo


def calcula_conducao(mesreferencia, anoreferencia, idpessoal):
    dia, diafinal = periodo_cartaoponto(mesreferencia, anoreferencia)
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal, Ausencia='').count()
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    valorconducao = 8.80
    valetransporte = float(cartaoponto)*float(valorconducao)
    if cartaoponto > 0:
        if contracheque:
            contrachequeitens = get_contrachequeitens(contracheque[0].idContraCheque, 'VALE TRANSPORTE', 'C')
            if contrachequeitens:
                altera_contracheque_itens(contrachequeitens, valetransporte, '{}d'.format(cartaoponto))
                print(cartaoponto)
            else:
                if valetransporte > 0:
                    create_contracheque_itens('VALE TRANSPORTE', valetransporte, '{}d'.format(cartaoponto), 'C',
                                              contracheque[0].idContraCheque)
    else:
        delete_contrachequeitens(contracheque[0].idContraCheque, 'VALE TRANSPORTE', 'C')
    return valetransporte


def saldo_contracheque(idcontracheque):
    credito = ContraChequeItens.objects.filter(idContraCheque=idcontracheque,
                                               Registro='C').aggregate(Total=Sum('Valor'))
    debito = ContraChequeItens.objects.filter(idContraCheque=idcontracheque,
                                              Registro='D').aggregate(Total=Sum('Valor'))
    if not credito['Total']:
        credito['Total'] = Decimal('0.00')
    if not debito['Total']:
        debito['Total'] = Decimal('0.00')
    totais = {'Credito': credito['Total'], 'Debito': debito['Total'], 'Liquido': credito['Total'] - debito['Total']}
    return totais


def lista_mensaalista_ativos():
    return facade.get_pessoal_mensalista_ativo()


def list_avulsos_ativo():
    return facade.get_pessoal_nao_mensalista_ativo()


def form_pagamento(request, c_form, c_idobj, c_url, c_view, idcartaoponto, mesreferencia, anoreferencia, idpessoal):
    data = dict()
    c_instance = None
    if c_view == 'edita_cartaoponto':
        if c_idobj:
            c_instance = CartaoPonto.objects.get(idCartaoPonto=c_idobj)
    if request.method == 'POST':
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            form.save()
        calcula_horas_extras(mesreferencia, anoreferencia, idpessoal)
        calcula_horas_atrazo(mesreferencia, anoreferencia, idpessoal)
        contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
        data['html_adiantamento'] = busca_adiantamento(contracheque[0].idContraCheque)
        data['html_folha'] = html_folha(mesreferencia, anoreferencia)
        data['html_contracheque'] = html_contracheque(mesreferencia, anoreferencia, idpessoal)
        data['html_cartaoponto'] = html_cartaoponto(mesreferencia, anoreferencia, idpessoal)
        data['html_formccadianta'] = html_formccadianta(contracheque, request)
        data['html_formccitens'] = html_formccitens(contracheque, request)
        data['html_minutascontracheque'] = html_minutascontracheque(mesreferencia, anoreferencia, idpessoal)
        data['html_vales'] = html_vale(idpessoal, 'mensalista', contracheque[0].idContraCheque)
    else:
        form = c_form(instance=c_instance)
    context = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view, 'idcartaoponto': idcartaoponto,
               'idcategoriaveiculo': request.GET.get('idcategoriaveiculo')}
    data['html_form'] = render_to_string('pagamentos/formpagamento.html', context, request=request)
    c_return = JsonResponse(data)
    return c_return
