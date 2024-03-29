# Generated by Django 3.1.3 on 2023-05-26 17:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('romaneios', '0014_notasclientes_emitente'),
    ]

    operations = [
        migrations.AddField(
            model_name='notasclientes',
            name='Bairro_emi',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='notasclientes',
            name='CEP_emi',
            field=models.CharField(blank=True, max_length=8, null=True),
        ),
        migrations.AddField(
            model_name='notasclientes',
            name='Cidade_emi',
            field=models.CharField(default='SÃO PAULO', max_length=30),
        ),
        migrations.AddField(
            model_name='notasclientes',
            name='Endereco_emi',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
        migrations.AddField(
            model_name='notasclientes',
            name='Estado_emi',
            field=models.CharField(default='SP', max_length=2),
        ),
    ]
