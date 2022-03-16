from datetime import date
import os
import re
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from clientes.models import EMailContatoCliente
from faturamentos.models import Fatura
from minutas.models import Minuta
from website.models import FileUpload


class FaturaSelecionada:
    def __init__(self, v_idfatura):
        fatura = Fatura.objects.get(idFatura=v_idfatura)
        self.idfatura = fatura.idFatura
        self.fatura = fatura.Fatura
        self.data_fatura = fatura.DataFatura
        self.valor_fatura = fatura.ValorFatura
        self.vencimento_fatura = fatura.VencimentoFatura
        self.status_fatura = fatura.StatusFatura
        self.valor_pagamento = fatura.ValorPagamento
        self.data_pagamento = fatura.DataPagamento
        self.comentario = fatura.Comentario
        self.minutas_fatura = MinutasFatura(v_idfatura).minutas
        self.total_minutas = len(self.minutas_fatura)
        self.notas_fatura = NotasFatura(self.fatura).notas
        self.boletos_fatura = BoletosFatura(self.fatura).boletos
        self.file_fatura = FileFatura(self.fatura).file
        self.cliente_fatura = ClienteFatura(v_idfatura).cliente
        self.email_fatura = ClienteEmail(self.cliente_fatura).email
        self.dias_vencimento = DiasVencimento(self.vencimento_fatura).dias


class MinutasFatura:
    def __init__(self, v_idfatura):
        self.minutas = self.get_minutas(v_idfatura)

    @staticmethod
    def get_minutas(v_idfatura):
        minutas = Minuta.objects.filter(idFatura=v_idfatura)
        lista = [{'idMinuta': itens.idMinuta, 'Minuta': itens.Minuta, 'idCliente': itens.idCliente} for itens in minutas]
        return lista


class NotasFatura:
    def __init__(self, v_fatura):
        self.notas = self.get_notas(v_fatura)

    @staticmethod
    def get_notas(v_fatura):
        notas = FileUpload.objects.filter(DescricaoUpload__startswith=f'FATURA_{str(v_fatura).zfill(6)}_NF')
        return notas


class BoletosFatura:
    def __init__(self, v_fatura):
        self.boletos = self.get_boletos(v_fatura)

    @staticmethod
    def get_boletos(v_fatura):
        boletos = FileUpload.objects.filter(DescricaoUpload__startswith=f'FATURA_{str(v_fatura).zfill(6)}_BOLETO')
        return boletos


class FileFatura:
    def __init__(self, v_fatura):
        self.file = self.get_file(v_fatura)

    @staticmethod
    def get_file(v_fatura):
        file = FileUpload.objects.filter(DescricaoUpload=f'FATURA_{str(v_fatura).zfill(6)}_FATURA.PDF')
        return file


class ClienteFatura:
    def __init__(self, v_idfatura):
        self.cliente = self.get_cliente(v_idfatura)

    @staticmethod
    def get_cliente(v_idfatura):
        minutas = Minuta.objects.filter(idFatura=v_idfatura)
        cliente = minutas[0].idCliente
        return cliente

class ClienteEmail:
    def __init__(self, cliente):
        self.email = self.get_email(cliente)

    @staticmethod
    def get_email(cliente):
        email = EMailContatoCliente.objects.filter(idCliente_id=cliente, RecebeFatura=1)
        lista = [itens.EMail for itens in email]
        return lista


class DiasVencimento:
    def __init__(self, vencimento):
        self.dias = self.get_dias(vencimento)

    @staticmethod
    def get_dias(vencimento):
        dias = vencimento - date.today()
        return dias.days


def get_fatura(v_idfatura):
    fatura = Fatura.objects.filter(idFatura=v_idfatura)
    lista = [{'idfatura': itens.idFatura, 'fatura': itens.Fatura, 'datafatura': itens.DataFatura, 'valorfatura': itens.ValorFatura, 'vencimentofatura': itens.VencimentoFatura, 'statusfatura': itens.StatusFatura, 'datapagamento': itens.DataPagamento, 'valorpagamento': itens.ValorPagamento, 'comentario': itens.Comentario} for itens in fatura]
    return lista


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return


def envia_email(v_idobj, v_emails, v_texto):
    data = dict()
    s_fatura = FaturaSelecionada(v_idobj)
    emails_to = v_emails
    emails_to = emails_to.replace(' ', '')
    emails_to = emails_to.replace(',', ' ')
    emails_to = emails_to.split()
    contexto = {'numero_fatura': str(s_fatura.fatura).zfill(6), 'texto': v_texto}
    subject = f'Fatura nº {str(s_fatura.fatura).zfill(6)}'
    html_message = render_to_string('faturamentos/emailfatura.html', contexto)
    from_email = 'Transefetiva Transportes <financeiro.efetiva@terra.com.br>'
    to = emails_to
    email = EmailMessage(subject, html_message, from_email, to)
    email.content_subtype = 'html'
    for itens in s_fatura.file_fatura:
        email.attach_file(itens.uploadFile.path)
    for itens in s_fatura.notas_fatura:
        email.attach_file(itens.uploadFile.path)
    for itens in s_fatura.boletos_fatura:
        email.attach_file(itens.uploadFile.path)
    list_check = verifica_emails(emails_to)
    if 0 in list_check:
        data['text_mensagem'] = 'Verifique os e-mails se estão corretos e se estão separados com virgula'
        data['type_mensagem'] = 'ERROR'
    else:
        if email.send():
            data['text_mensagem'] = 'E-Mail enviado com sucesso.'
            data['type_mensagem'] = 'SUCESSO'
        else:
            data['text_mensagem'] = 'Falha ao enviar e-mail, tente novamente'
            data['type_mensagem'] = 'ERROR'
    return retorna_json(data)


def verifica_emails(email_list):
    import re
    regex = '^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$'
    list_check = []
    for itens in email_list:
        if(re.search(regex, itens)):
            list_check.append(1)
        else:
            list_check.append(0)
    return list_check


def nome_arquivo(request, notas, boletos, v_fatura):
    lista_notas = []
    lista_boletos = []
    seguencia = [itens + 1 for itens in range(99)]
    for itens in notas:
        lista_notas.append(int(itens.DescricaoUpload[-2:]))
    lista_notas = sorted(lista_notas)
    for itens in boletos:
        lista_boletos.append(int(itens.DescricaoUpload[-2:]))
    lista_notas = sorted(lista_notas)
    lista_boletos = sorted(lista_boletos)
    proxima_nota = str(list(set(seguencia) - set(lista_notas))[0]).zfill(2)
    proximo_boleto = str(list(set(seguencia) - set(lista_boletos))[0]).zfill(2)
    if request.POST.get('tipo') == 'NOTA':
        descricao = f'Fatura_{str(v_fatura).zfill(6)}_nf_{proxima_nota}'
    elif request.POST.get('tipo') == 'BOLETO':
        descricao = f'Fatura_{str(v_fatura).zfill(6)}_boleto_{proximo_boleto}'
    return descricao


def salva_arquivo(request, msg, v_idfatura):
    fatura = FaturaSelecionada(v_idfatura).__dict__
    if request.method == 'POST':
        if request.FILES:
            v_descricao = nome_arquivo(request, fatura['notas_fatura'], fatura['boletos_fatura'], fatura['fatura'])
            ext_file = request.FILES['uploadFile'].name.split(".")[-1]
            name_file = f'{v_descricao}.{ext_file}'
            request.FILES['uploadFile'].name = name_file
            obj = FileUpload()
            obj.DescricaoUpload = v_descricao
            obj.uploadFile = request.FILES['uploadFile']
            try:
                obj.save()
                msg['text_mensagem'] = 'Arquivo enviado ao servidor com sucesso'
                msg['type_mensagem'] = 'SUCESSO'
            except:
                msg['text_mensagem'] = 'Falha ao salvar seu arquivo, tente novamente'
                msg['type_mensagem'] = 'ERROR'
        else:
            msg['text_mensagem'] = 'Arquivo não selecionado'
            msg['type_mensagem'] = 'ERROR'
    return msg


def delete_arquivo(request, id_fileupload, id_fatura):
    data = dict()
    nota = FileUpload.objects.get(idFileUpload=id_fileupload)
    nota.delete()
    os.remove(nota.uploadFile.path)
    data['idfatura'] = id_fatura
    return retorna_json(data)


def form_fatura(request, v_form, v_idobj, v_url, v_view):
    data = dict()
    v_instance = None
    form = None
    if request.method == 'POST':
        pass
    else:
        form = v_form(instance=v_instance)
    contexto = {'form': form, 'v_idobj': v_idobj, 'v_view': v_view, 'v_url': v_url}
    data['html_form'] = render_to_string('faturamentos/form_fatura.html', contexto, request=request)
    return retorna_json(data)
