# Generated by Django 3.1.3 on 2020-12-02 13:59

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Fatura',
            fields=[
                ('idFatura', models.AutoField(primary_key=True, serialize=False)),
                ('Fatura', models.IntegerField()),
                ('DataFatura', models.DateField(default=0)),
                ('ValorFatura', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('VencimentoFatura', models.DateField(default=0)),
                ('StatusFatura', models.CharField(default='ABERTA', max_length=6)),
                ('DataPagamento', models.DateField(default=0)),
                ('ValorPagamento', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Comentario', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'Fatura',
            },
        ),
    ]
