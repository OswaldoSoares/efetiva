# Generated by Django 3.1.3 on 2021-09-18 22:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0002_vales_idrecibo'),
    ]

    operations = [
        migrations.AddField(
            model_name='pessoal',
            name='DataDemissao',
            field=models.DateField(blank=True, null=True),
        ),
    ]
