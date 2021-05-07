import calendar
import datetime
from decimal import Decimal

from django.db.models import Sum
from django.http import JsonResponse
from django.template.loader import render_to_string

from minutas.models import MinutaColaboradores
from pessoas import facade
from pessoas.forms import CadastraContraCheque, CadastraContraChequeItens
from pessoas.models import ContraCheque, ContraChequeItens, CartaoPonto, Salario

meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO',
         'NOVEMBRO', 'DEZEMBRO']

dias = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']


def create_context(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    folha = {}
    referencia = {'MesReferencia': mesreferencia, 'AnoReferencia': anoreferencia}
    totalfolha = 0.00
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia)-1]
    for itens in mensalistas:
        folha[itens.Nome] = {'Salario': '0,00', 'Liquido': '0,00', 'ContraCheque': False, 'CartaoPonto': False,
                             'idPessoal': itens.idPessoal}
        salario = get_salario(itens.idPessoal)
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
    totalfolha = '{0:.2f}'.format(totalfolha).replace('.', ',')
    contexto = {'folha': folha, 'referencia': referencia, 'totalfolha': totalfolha}
    return contexto


def create_context_formcontracheque():
    formcontracheque = CadastraContraCheque()
    contexto = {'formcontracheque': formcontracheque}
    return contexto


def create_folha(mesreferencia, anoreferencia):
    mensalistas = lista_mensaalista_ativos()
    for itens in mensalistas:
        create_contracheque(mesreferencia, anoreferencia, '0.00', itens.idPessoal)
        create_cartaoponto(mesreferencia, anoreferencia, itens.idPessoal)


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
                create_contracheque_itens('Salario', salario[0].Salario, 'C', obj.idContraCheque)


def create_contracheque_itens(descricao, valor, registro, idcontracheque):
    if float(valor) > 0:
        if not busca_contrachequeitens(idcontracheque, descricao, registro):
            obj = ContraChequeItens()
            obj.Descricao = descricao
            obj.Valor = valor
            obj.Registro = registro
            obj.idContraCheque_id = idcontracheque
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
    contrachequeitens = ContraChequeItens.objects.get(idContraCheque=idcontracheque, Descricao=descricao,
                                                      Registro=registro)
    return contrachequeitens


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


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


def seleciona_folha(request, mesreferencia, anoreferencia):
    data = dict()
    contexto = create_context(mesreferencia, anoreferencia)
    data['html_folha'] = render_to_string('pagamentos/folhapgto.html', contexto, request=request)
    c_return = JsonResponse(data)
    return c_return


def seleciona_contracheque(request, mesreferencia, anoreferencia, idpessoal):
    data = dict()
    if mesreferencia in meses:
        mes = mesreferencia
    else:
        mes = meses[int(mesreferencia)-1]
    contracheque = ContraCheque.objects.filter(MesReferencia=mes, AnoReferencia=anoreferencia, idPessoal=idpessoal)
    contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque).order_by(
        'Registro')
    totais = saldo_contracheque(contracheque[0].idContraCheque)
    tem_adiantamento = False
    if busca_contrachequeitens(contracheque[0].idContraCheque, 'ADIANTAMENTO', 'D'):
        tem_adiantamento = True
    formcontrachequeitens = CadastraContraChequeItens()
    context = {'qs_contracheque': contracheque, 'qs_contrachequeitens': contrachequeitens, 'tem_adiantamento':
               tem_adiantamento, 'totais': totais}
    contextform = {'formcontrachequeitens': formcontrachequeitens, 'contracheque': contracheque}
    if busca_contrachequeitens(contracheque[0].idContraCheque, 'ADIANTAMENTO', 'D'):
        data['html_adiantamento'] = True
    else:
        data['html_adiantamento'] = False
    data['html_contracheque'] = render_to_string('pagamentos/contracheque.html', context, request=request)
    data['html_formccadianta'] = render_to_string('pagamentos/contrachequeadianta.html', contextform, request=request)
    data['html_formccitens'] = render_to_string('pagamentos/contrachequeitens.html', contextform, request=request)
    data['html_cartaoponto'] = seleciona_cartaoponto(mesreferencia,  anoreferencia, idpessoal)
    c_return = JsonResponse(data)
    return c_return


def seleciona_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mesreferencia = meses.index(mesreferencia)+1
    dia = '{}-{}-{}'.format(anoreferencia, mesreferencia, 1)
    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
    referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
    diafinal = '{}-{}-{}'.format(anoreferencia, mesreferencia, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, '%Y-%m-%d')
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    context = {'cartaoponto': cartaoponto}
    return render_to_string('pagamentos/cartaoponto.html', context)


def atualiza_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    if mesreferencia in meses:
        mesreferencia = meses.index(mesreferencia)+1
    dia = '{}-{}-{}'.format(anoreferencia, mesreferencia, 1)
    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
    referencia = calendar.monthrange(int(anoreferencia), int(mesreferencia))
    diafinal = '{}-{}-{}'.format(anoreferencia, mesreferencia, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, '%Y-%m-%d')
    minutas = MinutaColaboradores.objects.filter(idPessoal=idpessoal,
                                                 idMinuta_id__DataMinuta__range=(dia, diafinal)).order_by(
                                                 'idMinuta_id__DataMinuta').values('idMinuta_id__DataMinuta',
                                                                                   'idMinuta_id__HoraInicial',
                                                                                   'idMinuta_id__HoraFinal',
                                                                                   'idPessoal')
    totalextra = datetime.timedelta(hours=0, minutes=0)
    for x in minutas:
        cartaoponto = CartaoPonto.objects.get(Dia=x['idMinuta_id__DataMinuta'], idPessoal_id=x['idPessoal'])
        obj = cartaoponto
        horasaida = datetime.datetime.strptime('17:00:00', '%H:%M:%S').time()
        tdsaida = datetime.timedelta(hours=horasaida.hour, minutes=horasaida.minute)
        tdfinal = datetime.timedelta(hours=x['idMinuta_id__HoraFinal'].hour, minutes=x['idMinuta_id__HoraFinal'].minute)
        if tdfinal > tdsaida:
            totalextra += tdfinal-tdsaida
        if x['idMinuta_id__HoraFinal'] != obj.Saida:
            if x['idMinuta_id__HoraFinal'] > horasaida:
                obj.Saida = x['idMinuta_id__HoraFinal']
                obj.save(update_fields=['Saida'])
    salario = get_salario(idpessoal)
    valorhoraextra = float(salario[0].Salario)/30/9/60/60*totalextra.seconds
    contracheque = get_contrachequereferencia(mesreferencia, anoreferencia, idpessoal)
    if contracheque:
        contrachequeitens = get_contrachequeitens(contracheque[0].idContraCheque, 'HORA EXTRA', 'C')
        if contrachequeitens:
            altera_contracheque_itens(contrachequeitens, valorhoraextra)
        else:
            if valorhoraextra > 0:
                create_contracheque_itens('HORA EXTRA', valorhoraextra, 'C', contracheque[0].idContraCheque)


def altera_contracheque_itens(contrachequeitens, valorhoraextra):
    if float(valorhoraextra) > 0:
        obj = contrachequeitens
        obj.Valor = valorhoraextra
        obj.save(update_fields=['Valor'])


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
