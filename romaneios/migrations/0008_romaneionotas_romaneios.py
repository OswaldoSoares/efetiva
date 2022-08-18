# Generated by Django 3.1.3 on 2022-08-18 16:36

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0008_agenda'),
        ('veiculos', '0002_auto_20220221_0900'),
        ('romaneios', '0007_auto_20220815_1804'),
    ]

    operations = [
        migrations.CreateModel(
            name='Romaneios',
            fields=[
                ('idRomaneio', models.AutoField(primary_key=True, serialize=False)),
                ('Romaneio', models.IntegerField()),
                ('DataRomaneio', models.DateField(default=0)),
                ('idVeiculo', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='veiculos.veiculo')),
                ('idmotorista', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='pessoas.pessoal')),
            ],
            options={
                'db_table': 'romaneios',
            },
        ),
        migrations.CreateModel(
            name='RomaneioNotas',
            fields=[
                ('idRomaneioNotas', models.AutoField(primary_key=True, serialize=False)),
                ('idNotasClientes', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='romaneios.notasclientes')),
                ('idRomaneio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='romaneios.romaneios')),
            ],
            options={
                'db_table': 'romaneio_notas',
            },
        ),
    ]
