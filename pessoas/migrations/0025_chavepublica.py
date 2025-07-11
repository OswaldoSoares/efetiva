# Generated by Django 3.1.3 on 2025-06-29 20:28

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0024_alter_credencialwebauthn_managers'),
    ]

    operations = [
        migrations.CreateModel(
            name='ChavePublica',
            fields=[
                ('idChavePublica', models.AutoField(primary_key=True, serialize=False)),
                ('chave_publica', models.BinaryField(blank=True, null=True)),
                ('idPessoal', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='pessoas.pessoal')),
            ],
            options={
                'db_table': 'chave_publica',
                'ordering': ['idPessoal'],
            },
        ),
    ]
