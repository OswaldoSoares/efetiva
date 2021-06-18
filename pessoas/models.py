from django.db import models
import os


def get_file_path(instance, filename):
    ext = filename.split(".")[-1]
    nomearquivo = str(instance)
    nomearquivo = nomearquivo.lower()
    filename = "%s.%s" % (nomearquivo, ext)

    return os.path.join("pessoas", filename)


class Pessoal(models.Model):
    idPessoal = models.AutoField(primary_key=True)
    Nome = models.CharField(max_length=50)
    Endereco = models.CharField(max_length=60, blank=True)
    Bairro = models.CharField(max_length=20, blank=True)
    CEP = models.CharField(max_length=9, blank=True)
    Cidade = models.CharField(max_length=25, blank=True, default='SÃO PAULO')
    Estado = models.CharField(max_length=2, blank=True, default='SP')
    DataNascimento = models.DateField(blank=True, null=True)
    Mae = models.CharField(max_length=50, blank=True, null=True)
    Pai = models.CharField(max_length=50, blank=True, null=True)
    Categoria = models.CharField(max_length=15)
    TipoPgto = models.CharField(max_length=25, blank=False)
    StatusPessoal = models.BooleanField(default=True)
    DataAdmissao = models.DateField(blank=True, null=True)
    Foto = models.ImageField(upload_to=get_file_path, null=True, blank=True)

    class Meta:
        db_table = 'Pessoal'
        ordering = ['Nome']

    def __str__(self):
        return self.Nome

    def save(self, *args, **kwargs):
        self.Nome = self.Nome.upper()
        self.Endereco = self.Endereco.upper()
        self.Bairro = self.Bairro.upper()
        self.Cidade = self.Cidade.upper()
        self.Estado = self.Estado.upper()
        if self.Mae:
            self.Mae = self.Mae.upper()
        if self.Pai:
            self.Pai = self.Pai.upper()

        super(Pessoal, self).save(*args, **kwargs)

    objects = models.Manager()


class DocPessoal(models.Model):
    idDocPessoal = models.AutoField(primary_key=True)
    TipoDocumento = models.CharField(max_length=25)
    Documento = models.CharField(max_length=25)
    Data = models.DateField(blank=True, null=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'DocPessoal'
        ordering = ['TipoDocumento']

    def __str__(self):
        return self.TipoDocumento

    objects = models.Manager()


class FonePessoal(models.Model):
    idFonePessoal = models.AutoField(primary_key=True)
    TipoFone = models.CharField(max_length=15)
    Fone = models.CharField(max_length=20)
    Contato = models.CharField(max_length=50, blank=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'FonePessoal'
        ordering = ['TipoFone']

    def __str__(self):
        return self.TipoFone

    def save(self, *args, **kwargs):
        self.Contato = self.Contato.upper()

        super(FonePessoal, self).save(*args, **kwargs)

    objects = models.Manager()


class ContaPessoal(models.Model):
    idContaPessoal = models.AutoField(primary_key=True)
    Banco = models.CharField(max_length=20, blank=True)
    Agencia = models.CharField(max_length=6, blank=True)
    Conta = models.CharField(max_length=10, blank=True)
    TipoConta = models.CharField(max_length=8, blank=True)
    Titular = models.CharField(max_length=50, blank=True)
    Documento = models.CharField(max_length=25, blank=True)
    PIX = models.CharField(max_length=50, blank=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ContaPessoal'
        ordering = ['idPessoal', 'Banco', 'Agencia', 'Conta', 'PIX']

    def __str__(self):
        return self.Banco

    def save(self, *args, **kwargs):
        self.Banco = self.Banco.upper()
        self.Agencia = self.Agencia.upper()
        self.Conta = self.Conta.upper()
        self.Titular = self.Titular.upper()
        self.Documento = self.Documento.upper()

        super(ContaPessoal, self).save(*args, **kwargs)

    objects = models.Manager()


class HorasTrabalhadas(models.Model):
    idHorasTrabalhadas = models.AutoField(primary_key=True)
    Data = models.DateField()
    Minuta = models.CharField(max_length=6, blank=False)
    HoraInicial = models.TimeField()
    HoraFinal = models.TimeField()
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'HorasTrabalhadas'
        ordering = ['idPessoal', 'Data', 'Minuta']

    def __str__(self):
        return self.idHorasTrabalhadas

    objects = models.Manager()


class Vales(models.Model):
    idVales = models.AutoField(primary_key=True)
    Data = models.DateField()
    Descricao = models.CharField(max_length=100, blank=False)
    Valor = models.DecimalField(decimal_places=2, max_digits=7, default=1.00)
    Pago = models.BooleanField(default=False)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT, default=1)

    class Meta:
        db_table = 'Vales'
        ordering = ['idPessoal', 'Data', 'Descricao']

    def __str__(self):
        return self.Descricao

    def save(self, *args, **kwargs):
        self.Descricao = self.Descricao.upper()

        super(Vales, self).save(*args, **kwargs)

    objects = models.Manager()


class Salario(models.Model):
    idSalario = models.AutoField(primary_key=True)
    Salario = models.DecimalField(decimal_places=2, max_digits=9, default=1.00)
    HorasMensais = models.DecimalField(decimal_places=2, max_digits=6, default=220.00)
    ValeTransporte = models.DecimalField(decimal_places=2, max_digits=6, default=0.00)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT, default=1)

    class Meta:
        db_table = 'Salario'
        ordering = ['idPessoal']

    def __str__(self):
        return str(self.Salario)

    objects = models.Manager()


class ContraCheque(models.Model):
    idContraCheque = models.AutoField(primary_key=True)
    MesReferencia = models.CharField(max_length=9)
    AnoReferencia = models.IntegerField()
    Valor = models.DecimalField(decimal_places=2, max_digits=9, default=0.00)
    Pago = models.BooleanField(default=False)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ContraCheque'
        ordering = ['-idContraCheque']

    def __str__(self):
        return f'{self.MesReferencia}/{self.AnoReferencia}'

    objects = models.Manager()


class ContraChequeItens(models.Model):
    idContraChequeItens = models.AutoField(primary_key=True)
    Descricao = models.TextField(max_length=50)
    Valor = models.DecimalField(decimal_places=2, max_digits=9, default=0.00)
    Registro = models.CharField(max_length=1)
    Referencia = models.CharField(max_length=7, blank=True)
    Vales_id = models.IntegerField(default=0)
    idContraCheque = models.ForeignKey(ContraCheque, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ContraChequeItens'
        ordering = ['Descricao']

    def __str__(self):
        return self.Descricao

    def save(self, *args, **kwargs):
        self.Descricao = self.Descricao.upper()

        super(ContraChequeItens, self).save(*args, **kwargs)

    objects = models.Manager()


class CartaoPonto(models.Model):
    idCartaoPonto = models.AutoField(primary_key=True)
    Dia = models.DateField()
    Entrada = models.TimeField()
    Saida = models.TimeField()
    Ausencia = models.CharField(max_length=7, blank=True)
    Alteracao = models.CharField(max_length=6, default='ROBOT')
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'CartaoPonto'
        ordering = ['Dia']

    def __str__(self):
        return str(self.idPessoal)

    def save(self, *args, **kwargs):
        if self.Ausencia:
            self.Ausencia = self.Ausencia.upper()

        super(CartaoPonto, self).save(*args, **kwargs)

    objects = models.Manager()
