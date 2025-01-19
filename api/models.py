from django.db import models


class BTCUSDHourly(models.Model):
    time = models.BigIntegerField()
    high = models.FloatField()
    low = models.FloatField()
    open = models.FloatField()
    volumefrom = models.FloatField()
    volumeto = models.FloatField()
    close = models.FloatField()

    
