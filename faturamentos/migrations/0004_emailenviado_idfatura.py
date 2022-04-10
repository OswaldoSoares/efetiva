# Generated by Django 3.1.3 on 2022-04-10 15:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0003_emailenviado'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailenviado',
            name='idFatura',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='faturamentos.fatura'),
            preserve_default=False,
        ),
    ]
