# Generated by Django 3.1.1 on 2021-04-29 12:56

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth_client', '0018_auto_20210429_1140'),
    ]

    operations = [
        migrations.RenameField(
            model_name='provider',
            old_name='provider',
            new_name='preset',
        ),
        migrations.RenameField(
            model_name='usertoken',
            old_name='provider',
            new_name='preset',
        ),
        migrations.AlterUniqueTogether(
            name='usertoken',
            unique_together={('user', 'preset', 'provider_part', 'integration'), ('user', 'preset', 'provider_part', 'endpoint')},
        ),
    ]