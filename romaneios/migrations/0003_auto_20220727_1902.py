# Generated by Django 3.1.3 on 2022-07-27 22:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('romaneios', '0002_notasclientes_cep'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notasclientes',
            name='Peso',
            field=models.DecimalField(decimal_places=3, default=0, max_digits=9),
        ),
    ]
