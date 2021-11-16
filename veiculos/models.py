from django.db import models
from pessoas.models import Pessoal

class CategoriaVeiculo(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    Categoria = models.CharField(max_length=15)

    class Meta:
        db_table = 'categoriaveiculo'
        ordering = ['Categoria']

    def __str__(self):
        return(self.Categoria)

    def save(self, *args, **kwargs):
        self.Categoria = self.Categoria.upper()

        super(CategoriaVeiculo, self).save(*args, **kwargs)

    objects = models.Manager()


# TODO: Motorista e Proprietário serãofuturamente foreignKey de pessoafrom django.db import
class Veiculo(models.Model):
    idVeiculo = models.AutoField(primary_key=True)
    Marca = models.CharField(max_length=35)
    Modelo = models.CharField(max_length=50)
    Placa = models.CharField(max_length=8)
    Cor = models.CharField(max_length=15, blank=True)
    Ano = models.CharField(max_length=4, blank=True)
    Renavam = models.CharField(max_length=20, blank=True)
    Combustivel = models.CharField(max_length=15, blank=True)
    Rastreador = models.CharField(max_length=15, blank=True)
    RNTRC = models.CharField(max_length=15, blank=True)
    Capacidade = models.DecimalField(max_digits=8, decimal_places=2, blank=True)
    MedidaAltura = models.DecimalField(max_digits=4, decimal_places=2, blank=True)
    MedidaComprimento = models.DecimalField(max_digits=4, decimal_places=2, blank=True)
    MedidaLargura = models.DecimalField(max_digits=4, decimal_places=2, blank=True)
    Proprietario = models.ForeignKey(Pessoal, related_name='PessoalProprietario',on_delete=models.PROTECT)
    Motorista = models.ForeignKey(Pessoal, related_name='PessoalMotorista',on_delete=models.PROTECT)
    Categoria = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)

    class Meta:
        db_table = 'veiculo'
        ordering = ['Placa']

    def __str__(self):
        return(self.Placa)

    def save(self, *args, **kwargs):
        self.Marca = self.Marca.upper()
        self.Modelo = self.Modelo.upper()
        self.Placa = self.Placa.upper()
        self.Cor = self.Cor.upper()
        self.Ano = self.Ano.upper()
        self.Renavam = self.Renavam.upper()

        super(Veiculo, self).save(*args, **kwargs)

    objects = models.Manager()
