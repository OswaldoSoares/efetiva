# Generated by Django 3.1.3 on 2022-08-31 21:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('romaneios', '0009_auto_20220818_1653'),
    ]

    operations = [
        migrations.AlterField(
            model_name='notasclientes',
            name='Informa',
            field=models.CharField(blank=True, max_length=300, null=True),
        ),
    ]
