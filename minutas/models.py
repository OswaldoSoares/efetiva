from django.db import models
from pip._vendor.contextlib2 import nullcontext
from clientes.models import Cliente
from faturamentos.models import Fatura
from pessoas.models import Pessoal
from veiculos.models import CategoriaVeiculo, Veiculo
import datetime
from datetime import timedelta


class Minuta(models.Model):
    idMinuta = models.AutoField(primary_key=True)
    Minuta = models.IntegerField()
    DataMinuta = models.DateField(default=0)
    HoraInicial = models.TimeField(default=datetime.time(0))
    HoraFinal = models.TimeField(default=datetime.time(0), blank=True, null=True)
    Coleta = models.TextField(blank=True)
    Entrega = models.TextField(blank=True)
    KMInicial = models.IntegerField(default=0)
    KMFinal = models.IntegerField(default=0)
    Obs = models.TextField(blank=True)
    StatusMinuta = models.CharField(max_length=10, default='ABERTA')
    Valor = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    Comentarios = models.TextField(default='', blank=True)
    idCliente = models.ForeignKey(Cliente, on_delete=models.PROTECT)
    idCategoriaVeiculo = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT, blank=True, null=True)
    idVeiculo = models.ForeignKey(Veiculo, on_delete=models.PROTECT, blank=True, null=True)
    idFatura = models.ForeignKey(Fatura, on_delete=models.PROTECT, blank=True, null=True)

    class Meta:
        db_table = 'Minuta'
        ordering = ['Minuta']

    def __str__(self):
        return str(self.Minuta)

    def save(self, *args, **kwargs):
        self.Coleta = self.Coleta.upper()
        self.Entrega = self.Entrega.upper()
        self.Obs = self.Obs.upper()

        super(Minuta, self).save(*args, **kwargs)

    objects = models.Manager()


class MinutaColaboradores(models.Model):
    idMinutaColaboradores = models.AutoField(primary_key=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT)
    idMinuta = models.ForeignKey(Minuta, on_delete=models.CASCADE)
    Cargo = models.CharField(max_length=10)
    Pago = models.BooleanField(default=False)

    class Meta:
        db_table = 'MinutaColaboradores'

    objects = models.Manager()


class MinutaItens(models.Model):
    idMinutaItens = models.AutoField(primary_key=True)
    Descricao = models.CharField(max_length=25)
    TipoItens = models.CharField(max_length=9)
    RecebePaga = models.CharField(max_length=1)
    Valor = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    Quantidade = models.IntegerField(default=0)
    Porcento = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    Peso = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    ValorBase = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    Tempo = models.DurationField(default=0)
    idMinuta = models.ForeignKey(Minuta, on_delete=models.CASCADE)

    class Meta:
        db_table = 'MinutaItens'

    objects = models.Manager()


class MinutaNotas(models.Model):
    idMinutaNotas = models.AutoField(primary_key=True)
    Nota = models.CharField(max_length=10)
    ValorNota = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    Peso = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    Volume = models.IntegerField(default=0)
    Nome =  models.CharField(max_length=60, blank=True, null=True)
    Estado = models.CharField(max_length=2, default='SP')
    Cidade = models.CharField(max_length=30, default='SÃO PAULO')
    Bairro = models.CharField(max_length=255, blank=True, null=True)
    NotaGuia = models.CharField(max_length=10, blank=True, null=True, default='0')
    idMinuta = models.ForeignKey(Minuta, on_delete=models.CASCADE)

    class Meta:
        db_table = 'MinutaNotas'

    def __str__(self):
        return str(self.Nota)

    def save(self, *args, **kwargs):
        self.Nota = self.Nota.upper()
        if self.Nome:
            self.Nome = self.Nome.upper()
        if self.Estado:
            self.Estado = self.Estado.upper()
        if self.Cidade:
            self.Cidade = self.Cidade.upper()
        if self.Bairro:
            self.Bairro = self.Bairro.upper()

        super(MinutaNotas, self).save(*args, **kwargs)

    objects = models.Manager()
