# Generated by Django 3.1.3 on 2020-12-04 01:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0006_auto_20201203_2215'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fatura',
            name='VencimentoFatura',
            field=models.DateField(default='2020-01-01'),
        ),
    ]
