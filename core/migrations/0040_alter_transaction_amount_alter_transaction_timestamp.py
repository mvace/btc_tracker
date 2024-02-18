# Generated by Django 4.2.7 on 2024-02-17 07:39

import datetime
from decimal import Decimal
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0039_alter_transaction_amount_alter_transaction_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=8, max_digits=32, validators=[django.core.validators.MinValueValidator(Decimal('0.00019')), django.core.validators.MaxValueValidator(Decimal('100000'))]),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 18, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2024, 2, 13, 0, 0, tzinfo=datetime.timezone.utc))]),
        ),
    ]
