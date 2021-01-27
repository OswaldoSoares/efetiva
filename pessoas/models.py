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
    Endereco = models.CharField(max_length=35, blank=True)
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
    Foto = models.ImageField(upload_to=get_file_path, null=True, blank=True)

    class Meta:
        db_table = 'Pessoal'
        ordering = ['Nome']

    def __str__(self):
        return (self.Nome)

    def save(self, *args, **kwargs):
        self.Nome = self.Nome.upper()
        self.Endereco = self.Endereco.upper()
        self.Bairro = self.Bairro.upper()
        self.Cidade = self.Cidade.upper()
        self.Estado = self.Estado.upper()

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
        return (self,DocPessoal)

    objects = models.Manager()


class FonePessoal(models.Model):
    idFonePessoal = models.AutoField(primary_key=True)
    TipoFone = models.CharField(max_length=15)
    Fone = models.CharField(max_length=20)
    Contato =models.CharField(max_length=50, blank=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'FonePessoal'
        ordering = ['TipoFone']

    def __str__(self):
        return (self, FonePessoal)

    def save(self, *args, **kwargs):
        self.Contato = self.Contato.upper()

        super(FonePessoal, self).save(*args, **kwargs)

    objects = models.Manager()


class ContaPessoal(models.Model):
    idContaPessoal = models.AutoField(primary_key=True)
    Banco = models.CharField(max_length=20)
    Agencia = models.CharField(max_length=6)
    Conta = models.CharField(max_length=10)
    TipoConta = models.CharField(max_length=8, blank=True)
    Titular = models.CharField(max_length=50, blank=True)
    Documento = models.CharField(max_length=25, blank=True)
    PIX = models.CharField(max_length=20, blank=True)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.CASCADE)

    class Meta:
        db_table = 'ContaPessoal'
        ordering = ['idPessoal', 'Banco', 'Agencia', 'Conta', 'PIX']

    def __str__(self):
        return (self.ContaPessoal)

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
        return (self.HorasTrabalhadas)

    objects = models.Manager()


class Vales(models.Model):
    idVales = models.AutoField(primary_key=True)
    Data = models.DateField()
    Descricao = models.CharField(max_length=100, blank=False)
    Valor = models.DecimalField(decimal_places=2, max_digits=7, default=1.00)
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT, default=1)

    class Meta:
        db_table = 'Vales'
        ordering = ['idPessoal', 'Data', 'Descricao']

    def __str__(self):
        return (self.Vales)

    objects = models.Manager()


class HorasConfig(models.Model):
    idHorasConfig = models.AutoField(primary_key=True)
    Salario = models.DecimalField(decimal_places=2, max_digits=9, default=1.00)
    HorasMensais = models.DurationField()
    idPessoal = models.ForeignKey(Pessoal, on_delete=models.PROTECT, default=1)

    class Meta:
        db_table = 'HorasConfig'
        ordering = ['idPessoal']

    def __str__(self):
        return (self.HorasConfig)

    objects = models.Manager()