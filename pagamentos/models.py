from django.db import models

from pessoas.models import Pessoal


class Recibo(models.Model):
    idRecibo = models.AutoField(primary_key=True)
    Recibo = models.IntegerField()
    DataRecibo = models.DateField(default=0)
    ValorRecibo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    StatusRecibo = models.CharField(max_length=6, default='ABERTA')
    DataPagamento = models.DateField(default='2020-01-01')
    Comentario = models.TextField(blank=True, null=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT)

    class Meta:
        db_table = 'Recibo'

    objects = models.Manager()
