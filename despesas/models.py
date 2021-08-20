from django.db import models
from veiculos.models import Veiculo


class Abastecimento(models.Model):
    idAbastecimento = models.AutoField(primary_key=True)
    DataAbastecimento = models.DateField(default=0)
    LitrosAbastecidos = models.PositiveIntegerField()
    ValorAbastecido = models.DecimalField(decimal_places=2, max_digits=8)
    ValorCombustivel = models.DecimalField(decimal_places=3, max_digits=6)
    TipoCombustivel = models.CharField(max_length=10)
    idVeiculo = models.ForeignKey(Veiculo, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Despesas_Abastecimento'

    def __str__(self):
        return str(self.idAbastecimento)

    def save(self, *args, **kwargs):
        if self.TipoCombustivel:
            self.TipoCombustivel = self.TipoCombustivel.upper()

        super(Abastecimento, self).save(*args, **kwargs)

    objects = models.Manager()
