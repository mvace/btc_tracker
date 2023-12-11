# Generated by Django 4.2.7 on 2023-12-08 12:30

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0024_alter_transaction_initial_value_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=8, max_digits=16, validators=[django.core.validators.MinValueValidator(1e-07), django.core.validators.MaxValueValidator(100000)]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 8, 12, 30, 59, 9237, tzinfo=datetime.timezone.utc))]),
        ),
    ]
