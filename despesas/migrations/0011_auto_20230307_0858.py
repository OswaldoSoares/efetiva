# Generated by Django 3.1.3 on 2023-03-07 11:58

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0014_ferias_idaquisitivo'),
        ('despesas', '0010_auto_20220719_0734'),
    ]

    operations = [
        migrations.AddField(
            model_name='multas',
            name='idPessoal',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='pessoas.pessoal'),
        ),
        migrations.AddField(
            model_name='multas',
            name='idVales',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pessoas.vales'),
        ),
    ]
