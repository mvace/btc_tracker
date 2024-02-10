from django.core.management.base import BaseCommand
from core.models import DailyClosePrice, Portfolio
import cryptocompare


# How to only
# get latest timestamp
class Command(BaseCommand):
    help = (
        "This command updates DailyClosePrice data with latest data from cryptocompare"
    )

    def handle(self, *args, **options):
        last_ts = DailyClosePrice.objects.last().daily_timestamp
        print(last_ts, type(last_ts))
        data = cryptocompare.get_historical_price_day_from(
            "BTC", "USD", fromTs=last_ts + 1
        )
        print(data)
        self.stdout.write(self.style.SUCCESS("Successfully got data"))

        for record in data:
            DailyClosePrice.objects.get_or_create(
                daily_timestamp=record["time"],
                close_price=record["close"],
            )
            self.stdout.write(self.style.SUCCESS(f'{record["time"]}'))

        portfolios = Portfolio.objects.all()
        for portfolio in portfolios:
            portfolio.update_metrics()
            self.stdout.write(self.style.SUCCESS(f"{portfolio}"))

        self.stdout.write(self.style.SUCCESS("Successfully ran your custom command"))
