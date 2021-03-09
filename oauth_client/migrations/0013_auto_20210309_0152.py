# Generated by Django 3.1.1 on 2021-03-09 01:52

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('oauth_client', '0012_auto_20210308_2308'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='usertoken',
            unique_together={('user', 'provider', 'provider_part', 'endpoint'), ('user', 'provider', 'provider_part', 'integration')},
        ),
    ]