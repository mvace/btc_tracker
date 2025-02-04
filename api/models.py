from django.db import models


class BTCUSDHourly(models.Model):
    date_time_unix = models.BigIntegerField()
    date_time = models.DateTimeField()
    high = models.FloatField()
    low = models.FloatField()
    open = models.FloatField()
    close = models.FloatField()
    volumefrom = models.FloatField()
    volumeto = models.FloatField()
