# Generated by Django 4.2.7 on 2024-01-25 07:14

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0026_alter_portfoliometrics_btc_amount_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=8, max_digits=32, validators=[django.core.validators.MinValueValidator(1e-08), django.core.validators.MaxValueValidator(100000)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2024, 1, 25, 7, 14, 41, 574942, tzinfo=datetime.timezone.utc))]),
        ),
    ]
