from django.contrib import admin
from .models import Transaction, Portfolio, DailyClosePrice, PortfolioMetrics

# Register your models here.
admin.site.register(Transaction)
admin.site.register(Portfolio)
admin.site.register(DailyClosePrice)
admin.site.register(PortfolioMetrics)
