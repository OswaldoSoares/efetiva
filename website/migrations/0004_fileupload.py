# Generated by Django 3.1.3 on 2022-02-22 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('website', '0003_delete_fileupload'),
    ]

    operations = [
        migrations.CreateModel(
            name='FileUpload',
            fields=[
                ('idFileUpload', models.AutoField(primary_key=True, serialize=False)),
                ('Descricao', models.CharField(max_length=50)),
                ('upLoadFile', models.FileField(upload_to='upload_files/')),
                ('DateUpload', models.DateTimeField(auto_now=True)),
            ],
        ),
    ]
