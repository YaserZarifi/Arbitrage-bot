from django.db import models

class PriceData(models.Model):
    currency_pair = models.CharField(max_length=20)
    binance_price = models.DecimalField(max_digits=20, decimal_places=8)
    gateio_price = models.DecimalField(max_digits=20, decimal_places=8)
    price_difference_percent = models.DecimalField(max_digits=8, decimal_places=4)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.currency_pair} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
