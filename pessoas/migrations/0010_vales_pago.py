# Generated by Django 3.1.3 on 2021-06-01 13:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0009_cartaoponto_alteracao'),
    ]

    operations = [
        migrations.AddField(
            model_name='vales',
            name='Pago',
            field=models.BooleanField(default=False),
        ),
    ]
