# Generated by Django 3.0.3 on 2020-08-21 18:59

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('veiculos', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Cliente',
            fields=[
                ('idCliente', models.AutoField(primary_key=True, serialize=False)),
                ('Fantasia', models.CharField(max_length=20)),
                ('Nome', models.CharField(max_length=50)),
                ('Endereco', models.CharField(blank=True, max_length=35)),
                ('Bairro', models.CharField(blank=True, max_length=20)),
                ('CEP', models.CharField(blank=True, max_length=9)),
                ('Cidade', models.CharField(blank=True, default='SÃO PAULO', max_length=25)),
                ('Estado', models.CharField(blank=True, default='SP', max_length=2)),
                ('CNPJ', models.CharField(blank=True, max_length=18)),
                ('IE', models.CharField(blank=True, max_length=15)),
                ('Site', models.CharField(blank=True, max_length=40)),
            ],
            options={
                'db_table': 'Cliente',
                'ordering': ['Fantasia'],
            },
        ),
        migrations.CreateModel(
            name='FormaPagamento',
            fields=[
                ('idFormaPagamento', models.AutoField(primary_key=True, serialize=False)),
                ('Forma', models.CharField(max_length=10)),
                ('Dias', models.IntegerField(default=1)),
            ],
            options={
                'db_table': 'FormaPagamento',
                'ordering': ['Forma', 'Dias'],
            },
        ),
        migrations.CreateModel(
            name='TabelaVeiculo',
            fields=[
                ('idTabelaVeiculo', models.AutoField(primary_key=True, serialize=False)),
                ('PorcentagemCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('PorcentagemPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('HoraCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('HoraPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('HoraMinimo', models.TimeField(default=0)),
                ('KMCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('KMPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('KMMinimo', models.IntegerField(default=0)),
                ('EntregaCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('EntregaPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('EntregaMinimo', models.IntegerField(default=0)),
                ('SaidaCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('SaidaPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('idCategoriaVeiculo', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='veiculos.CategoriaVeiculo')),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'TabelaVeiculo',
                'ordering': ['idCategoriaVeiculo'],
            },
        ),
        migrations.CreateModel(
            name='TabelaPerimetro',
            fields=[
                ('idTabelaPerimetro', models.AutoField(primary_key=True, serialize=False)),
                ('PerimetroInicial', models.IntegerField(default=0)),
                ('PerimetroFinal', models.IntegerField(default=1)),
                ('PerimetroCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('PerimetroPaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'TabelaPerimetro',
                'ordering': ['idTabelaPerimetro'],
            },
        ),
        migrations.CreateModel(
            name='TabelaCapacidade',
            fields=[
                ('idTabelaCapacidade', models.AutoField(primary_key=True, serialize=False)),
                ('CapacidadeInicial', models.IntegerField(default=0)),
                ('CapacidadeFinal', models.IntegerField(default=1)),
                ('CapacidadeCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('CapacidadePaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'TabelaCapacidade',
                'ordering': ['idTabelaCapacidade'],
            },
        ),
        migrations.CreateModel(
            name='Tabela',
            fields=[
                ('idTabela', models.AutoField(primary_key=True, serialize=False)),
                ('Comissao', models.DecimalField(decimal_places=2, default=0, max_digits=5)),
                ('TaxaExpedicao', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('AjudanteCobra', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('AjudantePaga', models.DecimalField(decimal_places=2, default=0, max_digits=8)),
                ('idCliente', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
                ('idFormaPagamento', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='clientes.FormaPagamento', verbose_name='FORMA DE PAGAMENTO')),
            ],
            options={
                'db_table': 'Tabela',
            },
        ),
        migrations.CreateModel(
            name='FoneContatoCliente',
            fields=[
                ('idFoneContatoCliente', models.AutoField(primary_key=True, serialize=False)),
                ('Contato', models.CharField(max_length=25)),
                ('TipoFone', models.CharField(max_length=15)),
                ('Fone', models.CharField(max_length=30)),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'FoneContatoCliente',
                'ordering': ['Contato'],
            },
        ),
        migrations.CreateModel(
            name='EMailContatoCliente',
            fields=[
                ('idEmailContatoCliente', models.AutoField(primary_key=True, serialize=False)),
                ('Contato', models.CharField(max_length=25)),
                ('EMail', models.CharField(max_length=50)),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'EmailContatoCliente',
                'ordering': ['Contato'],
            },
        ),
        migrations.CreateModel(
            name='Cobranca',
            fields=[
                ('idCobranca', models.AutoField(primary_key=True, serialize=False)),
                ('Nome', models.CharField(max_length=50)),
                ('Endereco', models.CharField(blank=True, max_length=35)),
                ('Bairro', models.CharField(blank=True, max_length=20)),
                ('CEP', models.CharField(blank=True, max_length=9)),
                ('Cidade', models.CharField(blank=True, default='SÃO PAULO', max_length=25)),
                ('Estado', models.CharField(blank=True, default='SP', max_length=2)),
                ('CNPJ', models.CharField(blank=True, max_length=18)),
                ('IE', models.CharField(blank=True, max_length=15)),
                ('idCliente', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='clientes.Cliente')),
            ],
            options={
                'db_table': 'Cobranca',
                'ordering': ['Nome'],
            },
        ),
    ]
