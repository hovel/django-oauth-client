# Generated by Django 3.1.1 on 2020-11-19 00:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('oauth_client', '0006_usertoken_provider_part'),
    ]

    operations = [
        migrations.AddField(
            model_name='providerpart',
            name='provider',
            field=models.CharField(db_index=True, default='', max_length=50),
            preserve_default=False,
        ),
    ]
