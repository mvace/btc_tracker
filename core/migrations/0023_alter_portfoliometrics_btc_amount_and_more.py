# Generated by Django 4.2.7 on 2023-12-06 07:17

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0022_portfoliometrics_btc_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliometrics',
            name='BTC_amount',
            field=models.DecimalField(decimal_places=8, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='portfoliometrics',
            name='USD_invested',
            field=models.DecimalField(decimal_places=2, max_digits=20, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 6, 7, 17, 0, 396095, tzinfo=datetime.timezone.utc))]),
        ),
    ]