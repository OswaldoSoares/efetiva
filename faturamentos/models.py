from django.db import models

class Fatura(models.Model):
    idFatura = models.AutoField(primary_key=True)
    Fatura = models.IntegerField()
    DataFatura = models.DateField(default=0)
    ValorFatura = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    DataPagamento = models.DateField(default=0)
    ValorPagamento = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        db_table = 'Fatura'

    objects = models.Manager()