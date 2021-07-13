# Generated by Django 3.1.3 on 2021-07-12 18:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('veiculos', '0001_initial'),
        ('clientes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Orcamento',
            fields=[
                ('idOrcamento', models.AutoField(primary_key=True, serialize=False)),
                ('DataOrcamento', models.DateField(default=0)),
                ('Solicitante', models.CharField(max_length=60)),
                ('Contato', models.CharField(blank=True, max_length=40, null=True)),
                ('Email', models.EmailField(max_length=50)),
                ('Telefone', models.CharField(max_length=25)),
                ('ValorTabela', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Valor', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Destino', models.CharField(blank=True, max_length=30, null=True)),
                ('KM', models.IntegerField(default=0)),
                ('Perimetro', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Pedagio', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Despesas', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Ajudantes', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('QuantidadeAjudantes', models.IntegerField(default=0)),
                ('TaxaExpedicao', models.DecimalField(decimal_places=2, default=0, max_digits=10)),
                ('Comentario', models.TextField(blank=True, null=True)),
                ('StatusOrcamento', models.CharField(default='CRIADO', max_length=20)),
                ('Cliente', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='clientes.cliente')),
                ('idCategoriaVeiculo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='veiculos.categoriaveiculo')),
                ('idFormaPagamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clientes.formapagamento')),
            ],
            options={
                'db_table': 'Orcamento',
                'ordering': ['DataOrcamento'],
            },
        ),
    ]
