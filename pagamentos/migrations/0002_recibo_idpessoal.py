# Generated by Django 3.1.3 on 2021-11-05 16:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pagamentos', '0001_initial'),
        ('pessoas', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='recibo',
            name='idPessoal',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pessoas.pessoal'),
        ),
    ]
