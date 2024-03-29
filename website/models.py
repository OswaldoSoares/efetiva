from django.db import models


class Parametros(models.Model):
    idParametro = models.AutoField(primary_key=True)
    Chave = models.CharField(max_length=100)
    Valor = models.CharField(max_length=100)

    class Meta:
        db_table = 'parametros'
        ordering = ['Chave']

    def save(self, *args, **kwargs):
        self.Chave = self.Chave.upper()
        self.Valor = self.Valor.upper()

        super(Parametros, self).save(*args, **kwargs)

    objects = models.Manager()


class FileUpload(models.Model):
    idFileUpload = models.AutoField(primary_key=True)
    DescricaoUpload = models.CharField(max_length=50)
    uploadFile = models.FileField(upload_to='upload_files/')
    DateUpload = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'fileupload'
        ordering = ['DescricaoUpload']

    def save(self, *args, **kwargs):
        self.DescricaoUpload = self.DescricaoUpload.upper()

        super(FileUpload, self).save(*args, **kwargs)

    objects = models.Manager()
