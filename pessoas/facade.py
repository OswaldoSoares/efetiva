import calendar
import datetime

from django.db.models import Sum
from django.http import JsonResponse
from django.template.loader import render_to_string
from decimal import Decimal

from pessoas.forms import CadastraSalario, CadastraVale, CadastraContraCheque, CadastraContraChequeItens
from pessoas.models import Pessoal, Salario, DocPessoal, FonePessoal, ContaPessoal, Vales, ContraCheque, \
    ContraChequeItens, CartaoPonto


meses = ['JANEIRO', 'FEVEREIRO', 'MARÇO', 'ABRIL', 'MAIO', 'JUNHO', 'JULHO', 'AGOSTO', 'SETEMBRO', 'OUTUBRO',
             'NOVEMBRO', 'DEZEMBRO']
dias = ['SEGUNDA-FEIRA', 'TERÇA-FEIRA', 'QUARTA-FEIRA', 'QUINTA-FEIRA', 'SEXTA-FEIRA', 'SÁBADO', 'DOMINGO']


def create_pessoal_context(idpessoa: int):
    colaborador = get_pessoal(idpessoa)
    docpessoa = get_docpessoal(idpessoa)
    fonepessoa = get_fonepessoal(idpessoa)
    contapessoa = get_contapessoal(idpessoa)
    contracheque = get_contracheque(idpessoa)
    salario = get_salario(idpessoa)
    instance_salario = get_salario(idpessoa).first()
    formsalario = CadastraSalario(instance=instance_salario)
    formvale = CadastraVale()
    formcontracheque = CadastraContraCheque()
    context = {'colaborador': colaborador, 'docpessoa': docpessoa, 'fonepessoa': fonepessoa, 'contapessoa': contapessoa,
               'contracheque': contracheque, 'salario': salario, 'formsalario': formsalario, 'formvale': formvale,
               'formcontracheque': formcontracheque}
    return context


def list_pessoal_all():
    return list(Pessoal.objects.all())


def get_pessoal_all():
    return Pessoal.objects.all()


def get_pessoal(idpessoa: int):
    colaborador = Pessoal.objects.filter(idPessoal=idpessoa)
    return colaborador


def get_docpessoal(idpessoa: int):
    docpessoal = DocPessoal.objects.filter(idPessoal=idpessoa)
    return docpessoal


def get_fonepessoal(idpessoa: int):
    fonepessoal = FonePessoal.objects.filter(idPessoal=idpessoa)
    return fonepessoal


def get_contapessoal(idpessoa: int):
    contapessoal = ContaPessoal.objects.filter(idPessoal=idpessoa)
    return contapessoal


def get_salario(idpessoal: int):
    salario = Salario.objects.filter(idPessoal=idpessoal)
    return salario


def get_contracheque(idpessoal: int):
    contracheque = ContraCheque.objects.filter(idPessoal=idpessoal)
    return contracheque


def get_contrachequeid(idcontracheque: int):
    contracheque = ContraCheque.objects.filter(idContraCheque=idcontracheque)
    return contracheque


def get_contracheque_itens(idcontracheque: int):
    contracheque_itens = ContraChequeItens.objects.filter(idContraCheque_id=idcontracheque).order_by('Registro')
    return contracheque_itens


def save_salario(idpessoal, salario, horasmensais):
    try:
        qs_salario = Salario.objects.get(idPessoal_id=idpessoal)
        obj = Salario(qs_salario)
        obj.idSalario = qs_salario.idSalario
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.idPessoal_id = idpessoal
    except Salario.DoesNotExist:
        obj = Salario()
        obj.Salario = salario
        obj.HorasMensais = horasmensais
        obj.idPessoal_id = idpessoal
    obj.save()


def create_vale(data, descricao, valor, idpessoal):
    obj = Vales()
    obj.Data = data
    obj.Descricao = descricao
    obj.Valor = valor
    obj.idPessoal_id = idpessoal
    obj.save()


def create_contracheque(mesreferencia, anoreferencia, valor, idpessoal):
    salario = get_salario(idpessoal)
    if not busca_contracheque(meses[int(mesreferencia)-1], anoreferencia, idpessoal):
        obj = ContraCheque()
        obj.MesReferencia = meses[int(mesreferencia)-1]
        obj.AnoReferencia = anoreferencia
        obj.Valor = valor
        obj.idPessoal_id = idpessoal
        obj.save()
        create_contracheque_itens('Salario Base', salario[0].Salario, 'C', obj.idContraCheque)


def create_contracheque_itens(descricao, valor, registro, idcontracheque):
    if not busca_contrachequeitens(idcontracheque, descricao, registro):
        obj = ContraChequeItens()
        obj.Descricao = descricao
        obj.Valor = valor
        obj.Registro = registro
        obj.idContraCheque_id = idcontracheque
        if float(valor) > 0:
            obj.save()


def busca_contracheque(mesreferencia, anoreferencia, idpessoal):
    qs_contracheque = ContraCheque.objects.filter(MesReferencia=mesreferencia, AnoReferencia=anoreferencia,
                                                  idPessoal=idpessoal)
    if qs_contracheque:
        return True


def busca_contrachequeitens(idcontracheque, descricao, registro):
    qs_contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=idcontracheque, Descricao=descricao,
                                                            Registro=registro)
    if qs_contrachequeitens:
        return True


def seleciona_contracheque(request, mesreferencia, anoreferencia, idpessoal):
    data = dict()
    formcqitens = CadastraContraChequeItens()
    qs_contracheque = ContraCheque.objects.filter(MesReferencia=mesreferencia, AnoReferencia=anoreferencia,
                                                  idPessoal=idpessoal)
    qs_contrachequeitens = ContraChequeItens.objects.filter(idContraCheque=qs_contracheque[0].idContraCheque).order_by(
        'Registro')
    credito = ContraChequeItens.objects.filter(idContraCheque=qs_contracheque[0].idContraCheque,
                                               Registro='C').aggregate(Total=Sum('Valor'))
    debito = ContraChequeItens.objects.filter(idContraCheque=qs_contracheque[0].idContraCheque,
                                              Registro='D').aggregate(Total=Sum('Valor'))
    if not credito['Total']:
        credito['Total'] = Decimal('0.00')
    if not debito['Total']:
        debito['Total'] = Decimal('0.00')
    totais = {'Credito': credito['Total'], 'Debito': debito['Total'], 'Liquido': credito['Total'] - debito['Total']}
    tem_adiantamento = False
    if busca_contrachequeitens(qs_contracheque[0].idContraCheque, 'ADIANTAMENTO', 'D'):
        tem_adiantamento = True
    cartaoponto = busca_cartaoponto_referencia(mesreferencia, anoreferencia, 6)
    context = {'formcqitens': formcqitens, 'qs_contracheque': qs_contracheque, 'qs_contrachequeitens':
               qs_contrachequeitens, 'tem_adiantamento': tem_adiantamento, 'totais': totais, 'cartaoponto': cartaoponto}
    data['html_contracheque'] = render_to_string('pessoas/contracheque.html', context, request=request)
    c_return = JsonResponse(data)
    return c_return


def print_contracheque_context(idcontracheque):
    contracheque = get_contrachequeid(idcontracheque)
    contrachequeitens = get_contracheque_itens(idcontracheque)
    colaborador = get_pessoal(contracheque[0].idPessoal_id)
    credito = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque,
                                               Registro='C').aggregate(Total=Sum('Valor'))
    debito = ContraChequeItens.objects.filter(idContraCheque=contracheque[0].idContraCheque,
                                              Registro='D').aggregate(Total=Sum('Valor'))
    if credito['Total'] == None:
        credito['Total'] = Decimal('0.00')
    if debito['Total'] == None:
        debito['Total'] = Decimal('0.00')
    totais = {'Credito': credito['Total'], 'Debito': debito['Total'], 'Liquido': credito['Total'] - debito['Total']}
    contexto = {'contracheque': contracheque, 'contrachequeitens': contrachequeitens, 'colaborador': colaborador,
                'totais': totais}
    return contexto


def create_cartaoponto(mesreferencia, anoreferencia, idpessoal):
    mes = meses.index(mesreferencia)+1
    referencia = calendar.monthrange(int(anoreferencia), mes)
    for x in range(1, referencia[1]+1):
        dia = '{}-{}-{}'.format(anoreferencia, mes, x)
        dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
        obj = CartaoPonto()
        obj.Dia = dia
        obj.Entrada = '00:00'
        obj.Saida = '00:00'
        if dia.weekday() == 5 or dia.weekday() == 6:
            obj.Ausencia = dias[dia.weekday()]
        else:
            obj.Ausencia = ''
        obj.idPessoal_id = idpessoal
        obj.save()


def busca_cartaoponto_referencia(mesreferencia, anoreferencia, idpessoal):
    mes = meses.index(mesreferencia) + 1
    dia = '{}-{}-{}'.format(anoreferencia, mes, 1)
    dia = datetime.datetime.strptime(dia, '%Y-%m-%d')
    referencia = calendar.monthrange(int(anoreferencia), mes)
    diafinal = '{}-{}-{}'.format(anoreferencia, mes, referencia[1])
    diafinal = datetime.datetime.strptime(diafinal, '%Y-%m-%d')
    cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    if not cartaoponto:
        create_cartaoponto(mesreferencia, anoreferencia, 6)
        cartaoponto = CartaoPonto.objects.filter(Dia__range=[dia, diafinal], idPessoal=idpessoal)
    if cartaoponto:
        return cartaoponto


def altera_status(idpessoal):
    pessoa = Pessoal.objects.get(idPessoal=idpessoal)
    if pessoa.StatusPessoal == True:
        pessoa.StatusPessoal = False
    else:
        pessoa.StatusPessoal = True
    pessoa.save()


def form_pessoa(request, c_form, c_idobj, c_url, c_view, idpessoal):
    data = dict()
    c_instance = None
    if c_view == 'edita_pessoa' or c_view == 'exclui_pessoa':
        if c_idobj:
            c_instance = Pessoal.objects.get(idPessoal=c_idobj)
    if request.method == 'POST':
        form = c_form(request.POST, instance=c_instance)
        if form.is_valid():
            save_id = form.save()
            if c_view == 'cria_pessoa' or c_view == 'edita_pessoa':
                data['save_id'] = save_id.idPessoal
                save_salario(save_id.idPessoal, 0.00, 1)
            else:
                data['save_id'] = save_id.idPessoal_id
        else:
            print(form)
    else:
        form = c_form(instance=c_instance)
    context = {'form': form, 'c_idobj': c_idobj, 'c_url': c_url, 'c_view': c_view, 'idpessoal': idpessoal}
    data['html_form'] = render_to_string('pessoas/formpessoa.html', context, request=request)
    data['c_view'] = c_view
    c_return = JsonResponse(data)
    return c_return
