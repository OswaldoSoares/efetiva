# Generated by Django 3.1.3 on 2020-12-01 00:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='fatura',
            name='StatusFatura',
            field=models.CharField(default='ABERTA', max_length=6),
        ),
    ]
