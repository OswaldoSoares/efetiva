from django.http import JsonResponse
from django.template.loader import render_to_string
from faturamentos.models import Fatura
from minutas.models import Minuta


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


class MinutasFatura:
    def __init__(self, v_idfatura):
        self.minutas = self.get_minutas(v_idfatura)

    @staticmethod
    def get_minutas(v_idfatura):
        minutas = Minuta.objects.filter(idFatura=v_idfatura)
        lista = [{'idMinuta': itens.idMinuta, 'Minuta': itens.Minuta} for itens in minutas]
        return lista


def retorna_json(data):
    c_return = JsonResponse(data)
    return c_return
