# Generated by Django 3.1.3 on 2021-11-05 14:14

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parametros',
            fields=[
                ('idParametro', models.AutoField(primary_key=True, serialize=False)),
                ('Chave', models.CharField(max_length=100)),
                ('Valor', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'Parametros',
                'ordering': ['Chave'],
            },
        ),
    ]
