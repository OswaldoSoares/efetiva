# Generated by Django 3.1.3 on 2021-01-21 18:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0003_auto_20210119_2007'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaCobra',
        ),
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaKGCobra',
        ),
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaKGPaga',
        ),
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaPaga',
        ),
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaVolumeCobra',
        ),
        migrations.RemoveField(
            model_name='tabela',
            name='EntregaVolumePaga',
        ),
    ]
