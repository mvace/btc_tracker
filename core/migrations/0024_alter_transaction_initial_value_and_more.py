# Generated by Django 4.2.7 on 2023-12-07 15:56

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0023_alter_portfoliometrics_btc_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='initial_value',
            field=models.DecimalField(blank=True, decimal_places=8, max_digits=16, null=True),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 7, 15, 56, 21, 308353, tzinfo=datetime.timezone.utc))]),
        ),
    ]