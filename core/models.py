# Standard library imports
from datetime import datetime, timedelta
from decimal import Decimal
import os

# Related third-party imports
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.db.models import DecimalField, ExpressionWrapper, F, Min, Sum
from django.db.models.functions import Coalesce
from django.utils import timezone
import requests
from dotenv import load_dotenv

# Local application/library specific imports
from .utils import get_current_price

# Load environment variables from the .env file
load_dotenv()

# Get the current price of the asset from a utility function
current_price = get_current_price()


class DailyClosePrice(models.Model):
    # Timestamp for the daily close (assumed to be in Unix time format)
    daily_timestamp = models.IntegerField(null=True, blank=True)
    # The closing price of the asset for the day
    close_price = models.DecimalField(
        max_digits=16, decimal_places=8, null=True, blank=True
    )


# Define minimum and maximum allowable transaction amounts
MIN_AMOUNT = Decimal("0.0002")
MAX_AMOUNT = Decimal("100000")


class Transaction(models.Model):
    # Get the timestamp of the last daily close price to set as limit for transactions
    last_daily_close_price = DailyClosePrice.objects.last().daily_timestamp
    limit_value = datetime.utcfromtimestamp(last_daily_close_price)
    limit_value = limit_value.replace(tzinfo=timezone.utc)

    # Link each transaction to a portfolio
    portfolio = models.ForeignKey(
        "Portfolio", on_delete=models.CASCADE, related_name="transactions"
    )

    # Timestamp of the transaction. Validators ensure it falls within an acceptable range
    timestamp = models.DateTimeField(
        validators=[
            MinValueValidator(
                datetime(year=2010, month=7, day=18, tzinfo=timezone.utc)
            ),
            MaxValueValidator(limit_value=limit_value),
        ]
    )
    timestamp_unix = models.IntegerField(
        null=True, blank=True
    )  # Unix timestamp equivalent
    daily_timestamp = models.IntegerField(
        null=True, blank=True
    )  # Daily timestamp for aggregation
    amount = models.DecimalField(
        max_digits=32,
        decimal_places=8,
        validators=[MinValueValidator(MIN_AMOUNT), MaxValueValidator(MAX_AMOUNT)],
    )  # Amount of asset transacted
    price = models.DecimalField(
        max_digits=32, decimal_places=8, null=True, blank=True
    )  # Transaction price
    initial_value = models.DecimalField(
        max_digits=32, decimal_places=8, null=True, blank=True
    )  # Initial value of the transaction

    def get_current_value(self):
        # Calculate the current value of the transaction based on the current price of the asset
        return current_price * self.amount

    def save(self, *args, **kwargs):
        # Adjust the timestamp for the transaction and calculate Unix timestamp and daily timestamp
        self.timestamp = self.timestamp - timedelta(hours=1)
        self.timestamp_unix = int(self.timestamp.timestamp())
        self.timestamp = self.timestamp.replace(minute=0, second=0, microsecond=0)
        self.daily_timestamp = int(self.timestamp.replace(hour=0).timestamp())

        # Fetch the price of the asset at the transaction time from an external API
        endpoint = "https://min-api.cryptocompare.com/data/v2/histohour"
        params = {
            "fsym": "BTC",  # From symbol (Bitcoin)
            "tsym": "USD",  # To symbol (US Dollar)
            "limit": 1,
            "toTs": self.timestamp_unix,
            "api_key": str(os.getenv("CRYPTOCOMPARE_API_KEY")),
        }
        response = requests.get(endpoint, params=params)
        data = response.json()
        price = data["Data"]["Data"][1]["close"]
        self.price = Decimal(price)

        # Calculate the initial value of the transaction
        self.initial_value = self.amount * self.price

        # Call the parent class's save method to handle the actual saving
        super().save(*args, **kwargs)

        # Update the portfolio metrics after saving the transaction
        self.portfolio.update_metrics()

    def __str__(self):
        return f"ID: {self.id}"


class Portfolio(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return f"{self.name}"

    def update_metrics(self):
        # This method updates the portfolio's metrics based on its transactions
        # It checks if there are any transactions and aggregates data to calculate metrics like ROI

        # Check if there are any transactions
        if not Transaction.objects.filter(portfolio=self).exists():
            print("No transactions found for this portfolio.")
            return

        # Ensure metrics object exists for the portfolio
        metrics, _ = PortfolioMetrics.objects.get_or_create(portfolio=self)

        # Fetch all transactions for a specific portfolio, ordered by timestamp
        transactions = Transaction.objects.filter(portfolio__id=self.id).order_by(
            "timestamp"
        )
        # Aggregate transaction datas
        transactions_data = transactions.aggregate(
            BTC_amount=Sum("amount"),
            USD_invested=Sum("initial_value"),
            start_date=Coalesce(Min("daily_timestamp"), None),
        )

        if transactions_data["start_date"] is None:
            # No transactions to process
            return

        # Get all the DailyClosePrice instance for after the start date
        daily_data = DailyClosePrice.objects.filter(
            daily_timestamp__gte=transactions_data["start_date"]
        ).order_by("daily_timestamp")

        # Initialize ROI dict
        metrics.roi_dict = {}

        # Pre-fetch all needed transactions
        all_transactions = list(transactions)

        # Pre-compute cumulative amounts and values up to each day
        cumulative_data = {}
        cumulative_amount = 0
        cumulative_value = 0

        for tx in all_transactions:
            cumulative_amount += tx.amount
            cumulative_value += tx.amount * tx.price
            cumulative_data[tx.daily_timestamp] = (cumulative_amount, cumulative_value)

        # Loop through each day's closing price to calculate daily ROI
        for day in daily_data:
            # Find the last transaction before or on this day to get cumulative values
            latest_tx_before_day = max(
                (
                    timestamp
                    for timestamp in cumulative_data.keys()
                    if timestamp <= day.daily_timestamp
                ),
                default=None,
            )

            # Proceed if there's at least one transaction before this day
            if latest_tx_before_day is not None:
                # Get cumulative amount and value from the last relevant transaction
                amount_cumulative, value_cumulative = cumulative_data[
                    latest_tx_before_day
                ]

                # Calculate average price bought until this day (avoid division by zero)
                average_price = (
                    value_cumulative / amount_cumulative
                    if amount_cumulative
                    else Decimal("0")
                )

                # Calculate ROI based on the day's closing price and average price
                roi = (
                    ((day.close_price - average_price) / average_price * 100)
                    if average_price
                    else Decimal("0")
                )

                # Save the calculated ROI for the day in a dictionary
                metrics.roi_dict[day.daily_timestamp] = str(roi)

                roi_values = [
                    (key, float(val)) for key, val in metrics.roi_dict.items()
                ]

                max_roi = max(roi_values, key=lambda x: x[1])
                min_roi = min(roi_values, key=lambda x: x[1])
                metrics.max_roi = max_roi
                metrics.min_roi = min_roi
                metrics.average_price = average_price
                metrics.USD_invested = value_cumulative
                metrics.BTC_amount = amount_cumulative
                metrics.save()

    def get_current_value(self):
        # This method calculates current USD value of the portfolio
        current_value = current_price * self.metrics.BTC_amount
        return current_value

    def get_current_roi(self):
        # This method calculates current ROI of the portfolio
        current_value = self.get_current_value()
        roi = (
            (current_value - self.metrics.USD_invested) / self.metrics.USD_invested
        ) * 100

        return roi


class PortfolioMetrics(models.Model):
    # This model stores various metrics related to a portfolio, such as ROI and investment totals
    portfolio = models.OneToOneField(
        Portfolio, on_delete=models.CASCADE, related_name="metrics"
    )
    average_price = models.DecimalField(
        max_digits=32, decimal_places=2, null=True
    )  # Average purchase price of the asset
    roi_dict = models.JSONField(default=dict)  # Dictionary storing ROI data over time
    max_roi = models.JSONField(null=True)  # Maximum ROI achieved
    min_roi = models.JSONField(null=True)  # Minimum ROI observed
    USD_invested = models.DecimalField(
        max_digits=32, decimal_places=2, null=True
    )  # Total USD invested in the portfolio
    BTC_amount = models.DecimalField(
        max_digits=32, decimal_places=8, null=True
    )  # Total amount of BTC held in the portfolio
