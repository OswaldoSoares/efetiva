# Generated by Django 3.1.3 on 2022-02-21 12:00

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('minutas', '0004_minutaitens_obs'),
    ]

    operations = [
        migrations.AlterModelTable(
            name='minuta',
            table='minuta',
        ),
        migrations.AlterModelTable(
            name='minutacolaboradores',
            table='minutacolaboradores',
        ),
        migrations.AlterModelTable(
            name='minutaitens',
            table='minutaitens',
        ),
        migrations.AlterModelTable(
            name='minutanotas',
            table='minutanotas',
        ),
    ]
