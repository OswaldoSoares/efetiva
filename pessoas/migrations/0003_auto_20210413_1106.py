# Generated by Django 3.1.3 on 2021-04-13 14:06

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('pessoas', '0002_contracheque_pago'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='contrachequeitens',
            name='idContraCheque',
        ),
        migrations.DeleteModel(
            name='ContraCheque',
        ),
        migrations.DeleteModel(
            name='ContraChequeItens',
        ),
    ]
