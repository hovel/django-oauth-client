# Generated by Django 3.1.1 on 2020-10-12 04:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0002_usertoken_endpoint'),
    ]

    operations = [
        migrations.AlterField(
            model_name='usertoken',
            name='access_token',
            field=models.CharField(max_length=2048),
        ),
        migrations.AlterField(
            model_name='usertoken',
            name='refresh_token',
            field=models.CharField(blank=True, max_length=512),
        ),
    ]