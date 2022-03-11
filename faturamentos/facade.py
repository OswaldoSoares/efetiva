import os
from django.http import JsonResponse
from django.template.loader import render_to_string
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
        self.total_notas = len(self.notas_fatura)
        self.boletos_fatura = BoletosFatura(self.fatura).boletos
        self.total_boletos = len(self.boletos_fatura)
        self.cliente_fatura = ClienteFatura(v_idfatura).cliente


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


class ClienteFatura:
    def __init__(self, v_idfatura):
        self.cliente = self.get_cliente(v_idfatura)

    @staticmethod
    def get_cliente(v_idfatura):
        minutas = Minuta.objects.filter(idFatura=v_idfatura)
        cliente = minutas[0].idCliente
        return cliente


def get_fatura(v_idfatura):
    fatura = Fatura.objects.filter(idFatura=v_idfatura)
    lista = [{'idfatura': itens.idFatura, 'fatura': itens.Fatura, 'datafatura': itens.DataFatura, 'valorfatura': itens.ValorFatura, 'vencimentofatura': itens.VencimentoFatura, 'statusfatura': itens.StatusFatura, 'datapagamento': itens.DataPagamento, 'valorpagamento': itens.ValorPagamento, 'comentario': itens.Comentario} for itens in fatura]
    return lista


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return


def salva_arquivo(request, msg, v_idfatura):
    fatura = FaturaSelecionada(v_idfatura).__dict__
    numero_f = fatura['fatura']
    total_n = fatura['total_notas']
    total_b = fatura['total_boletos']
    if request.method == 'POST':
        if request.FILES:
            if request.POST.get('tipo') == 'NOTA':
                v_descricao = f'Fatura_{str(numero_f).zfill(6)}_nf_{str(total_n + 1).zfill(2)}'
            elif request.POST.get('tipo') == 'BOLETO':
                v_descricao = f'Fatura_{str(numero_f).zfill(6)}_boleto_{str(total_b + 1).zfill(2)}'
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
