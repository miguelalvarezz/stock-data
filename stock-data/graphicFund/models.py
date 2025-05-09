# Create your models here.
from django.db import models

class Fund(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    sector = models.CharField(max_length=100, blank=True)
    return1y = models.FloatField(null=True, blank=True, help_text="Rentabilidad en el último año")
    fees = models.FloatField(null=True, blank=True, help_text="Comisiones anuales")
    benchmark = models.CharField(max_length=100, blank=True)
    volatility = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.symbol} - {self.name}"