# Generated by Django 3.1.3 on 2020-12-04 01:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0003_remove_fatura_vencimentofatura'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatura',
            name='VencimentoFatura',
            field=models.DateField(default=0),
        ),
    ]
