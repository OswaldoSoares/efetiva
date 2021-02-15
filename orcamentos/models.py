from django.db import models
from veiculos.models import CategoriaVeiculo
from clientes.models import Cliente


class Orcamento(models.Model):
    idOrcamento = models.AutoField(primary_key=True)
    DataOrcamento = models.DateField(default=0)
    Solicitante = models.CharField(max_length=60)
    Contato = models.CharField(max_length=40, blank=True, null=True)
    Email = models.EmailField(max_length=50)
    Telefone = models.CharField(max_length=25)
    ValorTabela = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Destino = models.CharField(max_length=30, blank=True, null=True)
    KM = models.IntegerField(default=0)
    Perimetro = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Pedagio = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Despesas = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Ajudantes = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    QuantidadeAjudantes = models.IntegerField(default=0)
    Comentario = models.TextField(blank=True, null=True)
    Cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, blank=True, null=True)
    idCategoriaVeiculo = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = 'Orcamento'
        ordering = ['DataOrcamento']

    def save(self, *args, **kwargs):
        if self.Solicitante:
            self.Solicitante = self.Solicitante.upper()
        if self.Contato:
            self.Contato = self.Contato.upper()
        if self.Destino:
            self.Destino = self.Destino.upper()
        if self.Comentario:
            self.Comentario = self.Comentario.upper()

        super(Orcamento, self).save(*args, **kwargs)

    objects = models.Manager()
