# Generated by Django 3.1.3 on 2020-12-04 01:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0005_auto_20201203_2210'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatura',
            name='VencimentoFatura',
            field=models.DateField(null=True),
        ),
    ]
