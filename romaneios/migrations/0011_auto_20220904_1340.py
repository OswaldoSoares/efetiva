# Generated by Django 3.1.3 on 2022-09-04 16:40

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('minutas', '0006_auto_20220727_1403'),
        ('romaneios', '0010_auto_20220831_1839'),
    ]

    operations = [
        migrations.AddField(
            model_name='romaneios',
            name='Fechado',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='romaneios',
            name='idMinuta',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='minutas.minuta'),
        ),
    ]
