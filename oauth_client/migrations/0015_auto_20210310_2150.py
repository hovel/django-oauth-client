# Generated by Django 3.1.1 on 2021-03-10 21:50

from django.db import migrations


def forward(apps, schema_editor):
    UserToken = apps.get_model('oauth_client', 'UserToken')

    for token in UserToken.objects.filter(integration__isnull=False,
                                          installation=True):
        integration = token.integration
        integration.admin = token.user
        integration.save()


def backward(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0014_integration_admin'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]