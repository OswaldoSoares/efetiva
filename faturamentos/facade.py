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
        self.notas_fatura = NotasFatura(v_idfatura).notas
        self.boletos_fatura = BoletosFatura(v_idfatura).boletos


class MinutasFatura:
    def __init__(self, v_idfatura):
        self.minutas = self.get_minutas(v_idfatura)

    @staticmethod
    def get_minutas(v_idfatura):
        minutas = Minuta.objects.filter(idFatura=v_idfatura)
        lista = [{'idMinuta': itens.idMinuta, 'Minuta': itens.Minuta} for itens in minutas]
        return lista


class NotasFatura:
    def __init__(self, v_idfatura):
        self.notas = self.get_notas(v_idfatura)

    @staticmethod
    def get_notas(v_idfatura):
        notas = FileUpload.objects.filter(DescricaoUpload=f'Fatura_{str(v_idfatura).zfill(6)}_nf')
        return notas


class BoletosFatura:
    def __init__(self, v_idfatura):
        self.boletos = self.get_boletos(v_idfatura)

    @staticmethod
    def get_boletos(v_idfatura):
        boletos = FileUpload.objects.filter(DescricaoUpload=f'Fatura_{str(v_idfatura).zfill(6)}_boleto')
        return boletos


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return


def nome_arquivo_nota(id_fatura):
    v_descricao = f'fatura_{str(id_fatura).zfill(6)}_nf'
    return v_descricao


def delete_arquivo(request, id_fileupload, id_fatura):
    data = dict()
    nota = FileUpload.objects.get(idFileUpload=id_fileupload)
    nota.delete()
    os.remove(nota.uploadFile.path)
    s_fatura = FaturaSelecionada(id_fatura).__dict__
    contexto = {'s_fatura': s_fatura}
    data['html_file'] = render_to_string('faturamentos/fatura_file.html', contexto, request=request)
    return retorna_json(data)


def form_fatura(request, v_form, v_idobj, v_url, v_view):
    data = dict()
    v_instance = None
    form = None
    print(v_url)
    if request.method == 'POST':
        if v_view == 'upload_nota':
            v_descricao = nome_arquivo_nota(v_idobj)
            print(request.FILES['uploadFile'].name)
            ext_file = request.FILES['uploadFile'].name.split(".")[-1]
            name_file = f'{v_descricao}.{ext_file}'
            request.FILES['uploadFile'].name = name_file
            form = v_form(request.POST, request.FILES)
        if form.is_valid():
            print(form)
            # form.save()
    else:
        if v_view == 'upload_nota':
            v_descricao = nome_arquivo_nota(v_idobj)
            form = v_form(instance=v_instance, initial={'DescricaoUpload': v_descricao})
        else:
            form = v_form(instance=v_instance)
    contexto = {'form': form, 'v_idobj': v_idobj, 'v_view': v_view, 'v_url': v_url}
    data['html_form'] = render_to_string('faturamentos/form_fatura.html', contexto, request=request)
    return retorna_json(data)
