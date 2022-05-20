import datetime

from django.db import models
from veiculos.models import Veiculo


class Abastecimento(models.Model):
    idAbastecimento = models.AutoField(primary_key=True)
    DataAbastecimento = models.DateField(default=0)
    LitrosAbastecidos = models.PositiveIntegerField()
    ValorAbastecido = models.DecimalField(decimal_places=2, max_digits=8)
    ValorCombustivel = models.DecimalField(decimal_places=3, max_digits=6)
    TipoCombustivel = models.CharField(max_length=10)
    Pago = models.BooleanField(default=False)
    DataPagamento = models.DateField(default=0)
    idVeiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)

    class Meta:
        db_table = "abastecimento"

    def __str__(self):
        return str(self.idAbastecimento)

    def save(self, *args, **kwargs):
        if self.TipoCombustivel:
            self.TipoCombustivel = self.TipoCombustivel.upper()

        super(Abastecimento, self).save(*args, **kwargs)

    objects = models.Manager()


class Multas(models.Model):
    idMulta = models.AutoField(primary_key=True)
    NumeroAIT = models.CharField(max_length=20)
    NumeroDOC = models.CharField(max_length=20, blank=True, null=True)
    DataMulta = models.DateField(default=0)
    HoraMulta = models.TimeField(default=datetime.time(0))
    ValorMulta = models.DecimalField(decimal_places=2, max_digits=9)
    Vencimento = models.DateField(default=0)
    Infracao = models.CharField(max_length=100)
    Local = models.CharField(max_length=240)
    Pago = models.BooleanField(default=False)
    DescontaMotorista = models.BooleanField(default=False)
    DataPagamento = models.DateField(default=0)
    idVeiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)

    class Meta:
        db_table = "multa"

    def __str__(self):
        return str(self.idMulta)

    def save(self, *args, **kwargs):
        self.NumeroAIT = self.NumeroAIT.upper()
        self.NumeroDOC = self.NumeroDOC.upper()
        self.Infracao = self.Infracao.upper()
        self.Local = self.Local.upper()

        super(Multas, self).save(*args, **kwargs)

    objects = models.Manager()
