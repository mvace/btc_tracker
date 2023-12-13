from django.core.management.base import BaseCommand
from core.models import DailyClosePrice, Portfolio
import cryptocompare


class Command(BaseCommand):
    help = "This command populates DailyClosePrice model with data from cryptocompare"

    def handle(self, *args, **options):
        data = cryptocompare.get_historical_price_day_all("BTC", "USD")

        for record in data:
            DailyClosePrice.objects.get_or_create(
                daily_timestamp=record["time"],
                close_price=record["close"],
            )

        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            portfolio.update_metrics()

        self.stdout.write(self.style.SUCCESS("Successfully ran your custom command"))
