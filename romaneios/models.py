from clientes.models import Cliente
from django.db import models


class NotasClientes(models.Model):
    idNotasClientes = models.AutoField(primary_key=True)
    DataColeta = models.DateField(default=0)
    LocalColeta = models.CharField(max_length=200)
    NumeroNota = models.CharField(max_length=15, default=0)
    Destinatario = models.CharField(max_length=200, blank=True, null=True)
    Endereco = models.CharField(max_length=200, blank=True, null=True)
    CEP = models.CharField(max_length=8, blank=True, null=True)
    Bairro = models.CharField(max_length=100, blank=True, null=True)
    Cidade = models.CharField(max_length=30, default="SÃO PAULO")
    Estado = models.CharField(max_length=2, default="SP")
    Contato = models.CharField(max_length=150, blank=True, null=True)
    Informa = models.CharField(max_length=150, blank=True, null=True)
    Volume = models.IntegerField(default=0)
    Peso = models.DecimalField(max_digits=9, decimal_places=3, default=0)
    Valor = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    StatusNota = models.CharField(max_length=15)
    Historico = models.TextField(default="", blank=True, null=True)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = "notas_cliente"

    def __str__(self):
        return str(self.idNotasClientes)

    def save(self, *args, **kwargs):
        self.LocalColeta = self.LocalColeta.upper()
        self.NumeroNota = self.NumeroNota.upper()
        self.Destinatario = self.Destinatario.upper()
        self.Endereco = self.Endereco.upper()
        self.Bairro = self.Bairro.upper()
        self.Cidade = self.Cidade.upper()
        self.Estado = self.Estado.upper()
        self.Contato = self.Contato.upper()
        self.Informa = self.Informa.upper()
        self.StatusNota = self.StatusNota.upper()
        self.Historico = self.Historico.upper()

        super(NotasClientes, self).save(*args, **kwargs)

    objects = models.Manager()
