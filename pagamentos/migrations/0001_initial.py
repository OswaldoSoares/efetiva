# Generated by Django 3.1.3 on 2021-07-22 21:56

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('pessoas', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Recibo',
            fields=[
                ('idRecibo', models.AutoField(primary_key=True, serialize=False)),
                ('Recibo', models.IntegerField()),
                ('DataRecibo', models.DateField(default=0)),
                ('ValorRecibo', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('StatusRecibo', models.CharField(default='ABERTA', max_length=6)),
                ('DataPagamento', models.DateField(default='2020-01-01')),
                ('Comentario', models.TextField(blank=True, null=True)),
                ('idPessoal', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='pessoas.pessoal')),
            ],
            options={
                'db_table': 'Recibo',
            },
        ),
    ]
