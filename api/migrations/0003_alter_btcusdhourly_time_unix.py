# Generated by Django 4.2.7 on 2025-02-04 07:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_alter_btcusdhourly_time_unix'),
    ]

    operations = [
        migrations.AlterField(
            model_name='btcusdhourly',
            name='time_unix',
            field=models.BigIntegerField(),
        ),
    ]
