# Generated by Django 4.1.6 on 2023-04-26 16:13

import chat.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chat', '0004_alter_file_options'),
    ]

    operations = [
        migrations.AlterField(
            model_name='file',
            name='instance',
            field=models.FileField(upload_to=chat.models.user_project_directory_path),
        ),
    ]