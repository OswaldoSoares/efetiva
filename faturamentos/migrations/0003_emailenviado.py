# Generated by Django 3.1.3 on 2022-04-10 14:49

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('faturamentos', '0002_auto_20220221_0900'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailEnviado',
            fields=[
                ('idEmailEnviado', models.AutoField(primary_key=True, serialize=False)),
                ('DataEnviado', models.DateField(blank=True, default=datetime.datetime.now)),
                ('EmailsEnviado', models.CharField(max_length=250)),
                ('MensagemAdicional', models.TextField(blank=True, null=True)),
            ],
            options={
                'db_table': 'email_enviado',
            },
        ),
    ]
