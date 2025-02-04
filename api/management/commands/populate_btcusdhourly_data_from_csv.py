from django.core.management.base import BaseCommand
import csv
import os
from datetime import datetime, timezone
from dotenv import load_dotenv
from api.models import BTCUSDHourly

load_dotenv()

csv_file_path = os.getenv("CSV_FILE_PATH")
csv_file_path = os.path.abspath(csv_file_path)


class Command(BaseCommand):
    help = "This command populates BTCUSDHourly data from csv file."

    def handle(self, *args, **options):
        with open(csv_file_path, newline="") as csvfile:
            reader = csv.DictReader(csvfile)

            for row in reader:
                date_time_unix = int(row["time"])
                date_time = datetime.fromtimestamp(date_time_unix, timezone.utc)
                high_price = float(row["high"])
                low_price = float(row["low"])
                open_price = float(row["open"])
                close_price = float(row["close"])
                volumefrom = float(row["volumefrom"])
                volumeto = float(row["volumeto"])

                BTCUSDHourly.objects.create(
                    date_time_unix=date_time_unix,
                    date_time=date_time,
                    high=high_price,
                    low=low_price,
                    open=open_price,
                    close=close_price,
                    volumefrom=volumefrom,
                    volumeto=volumeto,
                )

                self.stdout.write(self.style.SUCCESS(f"{date_time_unix} - imported"))
        self.stdout.write(
            self.style.SUCCESS("Successfully ran command for data population.")
        )
