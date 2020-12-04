from django.db import models


class Fatura(models.Model):
    idFatura = models.AutoField(primary_key=True)
    Fatura = models.IntegerField()
    DataFatura = models.DateField(default=0)
    ValorFatura = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    StatusFatura = models.CharField(max_length=6, default='ABERTA')
    ValorPagamento = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Comentario = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'Fatura'

    objects = models.Manager()
