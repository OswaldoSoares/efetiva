from django.db import models

from pessoas.models import Pessoal


class Recibo(models.Model):
    idRecibo = models.AutoField(primary_key=True)
    Recibo = models.IntegerField()
    DataRecibo = models.DateField(default=0)
    ValorRecibo = models.DecimalField(
        max_digits=10, decimal_places=2, default=0
    )
    StatusRecibo = models.CharField(max_length=6, default="ABERTA")
    DataPagamento = models.DateField(default="2020-01-01")
    Comentario = models.TextField(blank=True, null=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT)

    class Meta:
        db_table = "recibo"

    objects = models.Manager()


class ReciboItens(models.Model):
    idReciboItens = models.AutoField(primary_key=True)
    idMinutaItens = models.ForeignKey(
        "minutas.MinutaItens", on_delete=models.PROTECT
    )
    idRecibo = models.ForeignKey(Recibo, on_delete=models.CASCADE)

    class Meta:
        db_table = "reciboitens"

    objects = models.Manager()


class FolhaPagamento(models.Model):
    idFolhaPagamento = models.AutoField(primary_key=True)
    MesReferencia = models.CharField(max_length=9)
    AnoReferencia = models.IntegerField()
    Valor = models.DecimalField(decimal_places=2, max_digits=9, default=0.00)
    Colaboradores = models.IntegerField()
    Pago = models.BooleanField(default=False)

    class Meta:
        db_table = "folha_pagamento"

    objects = models.Manager()
