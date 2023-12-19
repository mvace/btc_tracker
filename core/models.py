from datetime import timedelta, datetime
from django.contrib.auth.models import User
from django.db import models
from django.db.models import F, ExpressionWrapper, DecimalField, Sum
from django.core.validators import MaxValueValidator, MinValueValidator
from django.utils import timezone
from decimal import Decimal
import requests

api_key = "71519726c4ebf2d4f41b3687d06386ba7c3a07d41ed4e1db77d2394e6b0fd540"
endpoint = "https://min-api.cryptocompare.com/data/price"

# Parameters for the API request
params = {
    "fsym": "BTC",  # From symbol (Bitcoin)
    "tsyms": "USD",  # To symbol (US Dollar)
    "api_key": api_key,
}
# Making the API request
response = requests.get(endpoint, params=params)
# Parse the JSON response
data = response.json()
# Extract the Bitcoin price in USD
current_price = Decimal(data["USD"])


class DailyClosePrice(models.Model):
    daily_timestamp = models.IntegerField(null=True, blank=True)
    close_price = models.DecimalField(
        max_digits=16, decimal_places=8, null=True, blank=True
    )


class Transaction(models.Model):
    portfolio = models.ForeignKey(
        "Portfolio", on_delete=models.CASCADE, related_name="transactions"
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
    amount = models.DecimalField(
        max_digits=32,
        decimal_places=8,
        validators=[MinValueValidator(0.0000001), MaxValueValidator(100000)],
    )
    price = models.DecimalField(max_digits=32, decimal_places=8, null=True, blank=True)
    initial_value = models.DecimalField(
        max_digits=32, decimal_places=8, null=True, blank=True
    )

    def get_current_value(self):
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

        self.initial_value = self.amount * self.price

        super().save(*args, **kwargs)
        # Update PortfolioMetrics after saving a new transaction
        self.portfolio.update_metrics()

    def __str__(self):
        return f"ID: {self.id}"


class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

    def update_metrics(self):
        metrics, created = PortfolioMetrics.objects.get_or_create(portfolio=self)
        # Fetch all transactions for a specific portfolio, ordered by timestamp
        transactions = Transaction.objects.filter(portfolio__id=self.id).order_by(
            "timestamp"
        )
        # Aggregate transaction datas
        transactions_data = transactions.aggregate(
            BTC_amount=Sum("amount"),
            USD_invested=Sum("initial_value"),
        )
        # Find the start date of the transactions
        start_date = transactions.first().daily_timestamp
        daily_data = DailyClosePrice.objects.filter(daily_timestamp__gte=start_date)

        metrics.roi_dict = {}
        for day in daily_data:
            cumulative_data = transactions.filter(
                timestamp_unix__lte=day.daily_timestamp
            ).aggregate(
                amount_cumulative=Sum("amount") or Decimal("0"),
                value_cumulative=Sum(
                    ExpressionWrapper(
                        F("amount") * F("price"), output_field=DecimalField()
                    )
                ),
                average_price=ExpressionWrapper(
                    F("value_cumulative") / F("amount_cumulative"),
                    output_field=DecimalField(),
                ),
                roi=ExpressionWrapper(
                    ((day.close_price - F("average_price")) / F("average_price")) * 100,
                    output_field=DecimalField(),
                ),
            )
            # Store ROI data for each day
            metrics.roi_dict[day.daily_timestamp] = str(
                cumulative_data["roi"] or Decimal("0")
            )
            roi_values = [(key, float(val)) for key, val in metrics.roi_dict.items()]

            max_roi = max(roi_values, key=lambda x: x[1])
            min_roi = min(roi_values, key=lambda x: x[1])
            metrics.max_roi = max_roi
            metrics.min_roi = min_roi
            metrics.average_price = cumulative_data["average_price"]
            metrics.USD_invested = transactions_data["USD_invested"]
            metrics.BTC_amount = transactions_data["BTC_amount"]
            metrics.save()

    def get_current_value(self):
        current_value = current_price * self.metrics.BTC_amount
        return current_value

    def get_current_roi(self):
        current_value = self.get_current_value()
        roi = (
            (current_value - self.metrics.USD_invested) / self.metrics.USD_invested
        ) * 100

        return roi


class PortfolioMetrics(models.Model):
    portfolio = models.OneToOneField(
        Portfolio, on_delete=models.CASCADE, related_name="metrics"
    )
    average_price = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    roi_dict = models.JSONField(default=dict)
    max_roi = models.JSONField(null=True)
    min_roi = models.JSONField(null=True)
    USD_invested = models.DecimalField(max_digits=32, decimal_places=2, null=True)
    BTC_amount = models.DecimalField(max_digits=32, decimal_places=8, null=True)
