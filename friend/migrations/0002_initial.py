# Generated by Django 4.1.6 on 2023-04-07 08:25

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('friend', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='friend',
            name='requestID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='request', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='friend',
            name='responseID',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='response', to=settings.AUTH_USER_MODEL),
        ),
    ]
