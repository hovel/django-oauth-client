# Generated by Django 3.2.5 on 2021-07-31 22:25
from django.conf import settings
from django.db import migrations


def forward(apps, schema_editor):
    Integration = apps.get_model('oauth_client', 'Integration')
    app_url = getattr(settings, 'APP_URL', '')
    if app_url:
        Integration.objects.filter(app_url='').update(app_url=app_url)


def backward(apps, schema_editor):
    Integration = apps.get_model('oauth_client', 'Integration')
    app_url = getattr(settings, 'APP_URL', '')
    if app_url:
        Integration.objects.filter(app_url=app_url).update(app_url='')


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0028_integration_app_url'),
    ]

    operations = [
        migrations.RunPython(forward, backward)
    ]