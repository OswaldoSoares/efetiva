# Generated by Django 3.1.3 on 2022-02-21 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clientes', '0002_auto_20211105_1305'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='cliente',
            table='cliente',
        ),
        migrations.AlterModelTable(
            name='cobranca',
            table='cobranca',
        ),
        migrations.AlterModelTable(
            name='emailcontatocliente',
            table='emailcontatocliente',
        ),
        migrations.AlterModelTable(
            name='fonecontatocliente',
            table='fonecontatocliente',
        ),
        migrations.AlterModelTable(
            name='formapagamento',
            table='formapagamento',
        ),
        migrations.AlterModelTable(
            name='tabela',
            table='tabela',
        ),
        migrations.AlterModelTable(
            name='tabelacapacidade',
            table='tabelacapacidade',
        ),
        migrations.AlterModelTable(
            name='tabelaperimetro',
            table='tabelaperimetro',
        ),
        migrations.AlterModelTable(
            name='tabelaveiculo',
            table='tabelaveiculo',
        ),
    ]
