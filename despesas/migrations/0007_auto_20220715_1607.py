# Generated by Django 3.1.3 on 2022-07-15 19:07

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('despesas', '0006_despesas'),
    ]

    operations = [
        migrations.AddField(
            model_name='despesas',
            name='Descricao',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='despesas',
            name='Categoria',
            field=models.CharField(blank=True, max_length=100),
        ),
        migrations.AlterField(
            model_name='despesas',
            name='SubCategoria',
            field=models.CharField(blank=True, max_length=100),
        ),
    ]
