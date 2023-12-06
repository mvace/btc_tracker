# Generated by Django 4.2.7 on 2023-12-06 07:15

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0021_portfoliometrics_max_roi_portfoliometrics_min_roi_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='portfoliometrics',
            name='BTC_amount',
            field=models.IntegerField(null=True),
        ),
        migrations.AddField(
            model_name='portfoliometrics',
            name='USD_invested',
            field=models.IntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 6, 7, 15, 30, 171438, tzinfo=datetime.timezone.utc))]),
        ),
    ]
