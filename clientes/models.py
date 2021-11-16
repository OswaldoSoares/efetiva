from django.db import models
from veiculos.models import CategoriaVeiculo


class Cliente(models.Model):
    idCliente = models.AutoField(primary_key=True)
    Fantasia = models.CharField(max_length=20, unique=True)
    Nome = models.CharField(max_length=60)
    Endereco = models.CharField(max_length=60, blank=True)
    Bairro = models.CharField(max_length=25, blank=True)
    CEP = models.CharField(max_length=9, blank=True)
    Cidade = models.CharField(max_length=30, blank=True, default='SÃO PAULO')
    Estado = models.CharField(max_length=2, blank=True, default='SP')
    CNPJ = models.CharField(max_length=18, blank=True)
    IE = models.CharField(max_length=15, blank=True)
    Site = models.CharField(max_length=40, blank=True)

    class Meta:
        db_table = 'cliente'
        ordering = ['Fantasia']

    def __str__(self):
        return self.Fantasia

    def save(self, *args, **kwargs):
        self.Fantasia = self.Fantasia.upper()
        self.Nome = self.Nome.upper()
        self.Endereco = self.Endereco.upper()
        self.Bairro = self.Bairro.upper()
        self.Cidade = self.Cidade.upper()
        self.Estado = self.Estado.upper()
        self.Site = self.Site.lower()

        super(Cliente, self).save(*args, **kwargs)

    objects = models.Manager()


class FoneContatoCliente(models.Model):
    idFoneContatoCliente = models.AutoField(primary_key=True)
    Contato = models.CharField(max_length=25)
    TipoFone = models.CharField(max_length=15)
    Fone = models.CharField(max_length=30)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'FoneContatoCliente'
        ordering = ['Contato']

    def __str__(self):
        return '{}/{}'.format(self.Contato, self.TipoFone)

    def save(self, *args, **kwargs):
        self.Contato = self.Contato.upper()
        self.TipoFone = self.TipoFone.upper()

        super(FoneContatoCliente, self).save(*args, **kwargs)

    objects = models.Manager()


class EMailContatoCliente(models.Model):
    idEmailContatoCliente = models.AutoField(primary_key=True)
    Contato = models.CharField(max_length=25)
    EMail = models.CharField(max_length=50)
    RecebeFatura = models.BooleanField(default=False)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'EmailContatoCliente'
        ordering = ['Contato']

    def __str__(self):
        return '{}/{}'.format(self.Contato, self.EMail)

    def save(self, *args, **kwargs):
        self.Contato = self.Contato.upper()
        self.EMail = self.EMail.lower()

        super(EMailContatoCliente, self).save(*args, **kwargs)

    objects = models.Manager()


class Cobranca(models.Model):
    idCobranca = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=50)
    Endereco = models.CharField(max_length=35, blank=True)
    Bairro = models.CharField(max_length=20, blank=True)
    CEP = models.CharField(max_length=9, blank=True)
    Cidade = models.CharField(max_length=25, blank=True, default='SÃO PAULO')
    Estado = models.CharField(max_length=2, blank=True, default='SP')
    CNPJ = models.CharField(max_length=18, blank=True)
    IE = models.CharField(max_length=15, blank=True)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Cobranca'
        ordering = ['Nome']

    def __str__(self):
        return self.Nome

    def save(self, *args, **kwargs):
        self.Nome = self.Nome.upper()
        self.Endereco = self.Endereco.upper()
        self.Bairro = self.Bairro.upper()
        self.Cidade = self.Cidade.upper()
        self.Estado = self.Estado.upper()

        super(Cobranca, self).save(*args, **kwargs)

    objects = models.Manager()


class FormaPagamento(models.Model):
    idFormaPagamento = models.AutoField(primary_key=True)
    Forma = models.CharField(max_length=10)
    Dias = models.IntegerField(default=1)

    class Meta:
        db_table = 'FormaPagamento'
        ordering = ['Forma', 'Dias']

    def __str__(self):
        return self.Forma + ' + ' + str(self.Dias)

    def save(self, *args, **kwargs):
        self.Forma = self.Forma.upper()

        super(FormaPagamento, self).save(*args, **kwargs)

    objects = models.Manager()


class Tabela(models.Model):
    idTabela = models.AutoField(primary_key=True)
    Comissao = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    TaxaExpedicao = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    AjudanteCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    AjudanteCobraHoraExtra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    AjudantePaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    phkescCobra = models.CharField(max_length=8, default='00000000')
    phkescPaga = models.CharField(max_length=8, default='00000000')
    idFormaPagamento = models.ForeignKey(FormaPagamento, on_delete=models.PROTECT, verbose_name='FORMA DE PAGAMENTO')
    idCliente = models.OneToOneField(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'Tabela'

    def __str__(self):
        return str(self.idFormaPagamento)

    objects = models.Manager()


class TabelaVeiculo(models.Model):
    idTabelaVeiculo = models.AutoField(primary_key=True)
    idCategoriaVeiculo = models.ForeignKey(CategoriaVeiculo, on_delete=models.PROTECT)
    PorcentagemCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    PorcentagemPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    HoraCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    HoraPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    HoraMinimo = models.TimeField(default=0)
    KMCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    KMPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    KMMinimo = models.IntegerField(default=0)
    EntregaCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaKGCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaKGPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaVolumeCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaVolumePaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    EntregaMinimo = models.IntegerField(default=0)
    SaidaCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    SaidaPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'TabelaVeiculo'
        ordering = ['idCategoriaVeiculo']

    def __str__(self):
        return str(self.idCategoriaVeiculo)

    objects = models.Manager()


class TabelaCapacidade(models.Model):
    idTabelaCapacidade = models.AutoField(primary_key=True)
    CapacidadeInicial = models.IntegerField(default=0)
    CapacidadeFinal = models.IntegerField(default=1)
    CapacidadeCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    CapacidadePaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'TabelaCapacidade'
        ordering = ['idTabelaCapacidade']

    objects = models.Manager()


class TabelaPerimetro(models.Model):
    idTabelaPerimetro = models.AutoField(primary_key=True)
    PerimetroInicial = models.IntegerField(default=0)
    PerimetroFinal = models.IntegerField(default=1)
    PerimetroCobra = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    PerimetroPaga = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    idCliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)

    class Meta:
        db_table = 'TabelaPerimetro'
        ordering = ['idTabelaPerimetro']

    objects = models.Manager()
