# Generated by Django 4.2.7 on 2023-11-12 09:14

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_dailycloseprice_alter_transaction_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 11, 12, 9, 14, 25, 624433, tzinfo=datetime.timezone.utc))]),
        ),
    ]
