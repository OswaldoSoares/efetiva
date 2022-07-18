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
    LinhaDigitavel = models.CharField(max_length=47, blank=True, null=True)
    LinhaDigitavelSP = models.CharField(max_length=48, blank=True, null=True)
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


class Despesas(models.Model):
    id_Despesa = models.AutoField(primary_key=True)
    Cedente = models.CharField(max_length=200)
    Categoria = models.CharField(max_length=100, blank=True)
    SubCategoria = models.CharField(max_length=100, blank=True)
    Descricao = models.TextField(blank=True)
    Valor = models.DecimalField(decimal_places=2, max_digits=8, default=0)
    Vencimento = models.DateField(default=0)
    DataPgto = models.DateField(default=0)
    ValorPago = models.DecimalField(decimal_places=2, max_digits=8, default=0)

    class Meta:
        db_table = "despesas"

    def __str__(self):
        return str(self.id_Despesa)

    def save(self, *args, **kwargs):
        self.Cedente = self.Cedente.upper()
        self.Categoria = self.Categoria.upper()
        self.SubCategoria = self.SubCategoria.upper()
        self.Descricao = self.Descricao.upper()

        super(Despesas, self).save(*args, **kwargs)

    objects = models.Manager()


class Categorias(models.Model):
    idCategoria = models.AutoField(primary_key=True)
    Categoria = models.CharField(max_length=100)

    class Meta:
        db_table = "despesas_categoria"

    def __str__(self):
        return str(self.Categoria)

    def save(self, *args, **kwargs):
        self.Categoria = self.Categoria.upper()

        super(Categorias, self).save(*args, **kwargs)

    objects = models.Manager()


class SubCategorias(models.Model):
    idSubCategoria = models.AutoField(primary_key=True)
    SubCategoria = models.CharField(max_length=100)
    idCategoria = models.ForeignKey(Categorias, on_delete=models.CASCADE)

    class Meta:
        db_table = "despesas_subcategoria"

    def __str__(self):
        return str(self.SubCategoria)

    def save(self, *args, **kwargs):
        self.SubCategoria = self.SubCategoria.upper()

        super(SubCategorias, self).save(*args, **kwargs)

    objects = models.Manager()
