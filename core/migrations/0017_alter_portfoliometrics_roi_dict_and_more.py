# Generated by Django 4.2.7 on 2023-12-04 15:37

import datetime
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0016_alter_portfoliometrics_average_price_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='portfoliometrics',
            name='roi_dict',
            field=models.JSONField(default=dict),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 4, 15, 37, 57, 773485, tzinfo=datetime.timezone.utc))]),
        ),
    ]
