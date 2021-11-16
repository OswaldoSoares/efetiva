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
