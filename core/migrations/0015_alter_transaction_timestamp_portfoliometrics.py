# Generated by Django 4.2.7 on 2023-12-04 15:33

import datetime
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_alter_transaction_timestamp'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='timestamp',
            field=models.DateTimeField(validators=[django.core.validators.MinValueValidator(limit_value=datetime.datetime(2010, 7, 17, 0, 0, tzinfo=datetime.timezone.utc)), django.core.validators.MaxValueValidator(limit_value=datetime.datetime(2023, 12, 4, 15, 33, 33, 489697, tzinfo=datetime.timezone.utc))]),
        ),
        migrations.CreateModel(
            name='PortfolioMetrics',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('average_price', models.DecimalField(decimal_places=2, max_digits=20)),
                ('roi_dict', models.JSONField()),
                ('portfolio', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='core.portfolio')),
            ],
        ),
    ]
