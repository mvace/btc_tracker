from datetime import timedelta, datetime
import cryptocompare
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal

# Create your models here.


class DailyClosePrice(models.Model):
    daily_timestamp = models.IntegerField(null=True, blank=True)
    close_price = models.DecimalField(
        max_digits=16, decimal_places=8, null=True, blank=True
    )


class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name}"


class Transaction(models.Model):
    portfolio = models.ForeignKey(
        Portfolio, on_delete=models.CASCADE, related_name="transactions"
    )
    timestamp = models.DateTimeField(
        validators=[
            MinValueValidator(
                limit_value=datetime(year=2010, month=7, day=17, tzinfo=timezone.utc)
            ),
            MaxValueValidator(limit_value=datetime.now(tz=timezone.utc)),
        ]
    )
    timestamp_unix = models.IntegerField(null=True, blank=True)
    daily_timestamp = models.IntegerField(null=True, blank=True)
    amount = models.DecimalField(max_digits=16, decimal_places=8)
    price = models.DecimalField(max_digits=16, decimal_places=8, null=True, blank=True)
    initial_value = models.DecimalField(
        max_digits=16, decimal_places=2, null=True, blank=True
    )

    def get_current_value(self):
        current_price = Decimal(cryptocompare.get_price("BTC", "USD")["BTC"]["USD"])
        return current_price * self.amount

    def save(self, *args, **kwargs):
        self.timestamp = self.timestamp - timedelta(hours=1)
        self.timestamp_unix = int(self.timestamp.timestamp())
        self.timestamp = self.timestamp.replace(minute=0, second=0, microsecond=0)
        self.daily_timestamp = int(self.timestamp.replace(hour=0).timestamp())
        self.price = Decimal(
            cryptocompare.get_historical_price_hour(
                "BTC", "USD", limit=1, toTs=self.timestamp
            )[1]["close"]
        )
        self.initial_value = self.amount * self.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"ID: {self.id}"
