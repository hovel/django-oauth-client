# Generated by Django 3.1.1 on 2021-03-12 22:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0016_remove_usertoken_installation'),
    ]

    operations = [
        migrations.AddField(
            model_name='integration',
            name='is_installed',
            field=models.BooleanField(default=False),
        ),
    ]