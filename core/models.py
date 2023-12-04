from datetime import timedelta, datetime
import cryptocompare
from django.contrib.auth.models import User
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal
import requests

# Create your models here.
api_key = "71519726c4ebf2d4f41b3687d06386ba7c3a07d41ed4e1db77d2394e6b0fd540"
cryptocompare.cryptocompare._set_api_key_parameter(api_key)


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

        endpoint = "https://min-api.cryptocompare.com/data/v2/histohour"
        params = {
            "fsym": "BTC",  # From symbol (Bitcoin)
            "tsym": "USD",  # To symbol (US Dollar)
            "limit": 1,  # Number of data points (e.g., 24 hours around the target timestamp)
            "toTs": self.timestamp_unix,  # End time for the data request (converted to Unix timestamp)
            "api_key": api_key,
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        price = data["Data"]["Data"][1]["close"]
        self.price = Decimal(price)

        # self.price = Decimal(cryptocompare.get_historical_price_hour("BTC", "USD", limit=1, toTs=self.timestamp[1]["close"])
        self.initial_value = self.amount * self.price

        super().save(*args, **kwargs)

    def __str__(self):
        return f"ID: {self.id}"
