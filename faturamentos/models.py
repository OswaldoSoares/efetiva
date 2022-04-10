from django.db import models
from django.utils import timezone


class Fatura(models.Model):
    idFatura = models.AutoField(primary_key=True)
    Fatura = models.IntegerField()
    DataFatura = models.DateField(default=0)
    ValorFatura = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    VencimentoFatura = models.DateField(default="2020-01-01")
    StatusFatura = models.CharField(max_length=6, default="ABERTA")
    ValorPagamento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    DataPagamento = models.DateField(default="2020-01-01")
    Comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = "fatura"

    objects = models.Manager()


class EmailEnviado(models.Model):
    idEmailEnviado = models.AutoField(primary_key=True)
    DataEnviado = models.DateTimeField(default=timezone.now, blank=True)
    EmailsEnviado = models.CharField(max_length=250)
    MensagemAdicional = models.TextField(blank=True, null=True)
    idFatura = models.ForeignKey(Fatura, on_delete=models.CASCADE)

    class Meta:
        db_table = "email_enviado"

    objects = models.Manager()
