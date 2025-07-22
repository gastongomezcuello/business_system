from django.db import models
from django.utils.translation import gettext_lazy as _


class Product(models.Model):
    TAV_CHOICES = [
        (1, 0.0, "No Gravado"),
        (2, 0.0, "Exento"),
        (3, 0.0, "0%"),
        (4, 10.5, "10,50%"),
        (5, 21.0, "21%"),
        (6, 27.0, "27%"),
        (7, 0.0, "Gravado"),
        (8, 5.0, "5%"),
        (9, 2.5, "2,50%"),
    ]

    TAV_CHOICES_DJANGO = [(code, desc) for code, _, desc in TAV_CHOICES]
    TAV_ID_TO_VALUE = {code: value for code, value, _ in TAV_CHOICES}
    TAV_ID_TO_DESC = {code: desc for code, _, desc in TAV_CHOICES}

    code = models.CharField(max_length=255, unique=True)
    bar_code = models.CharField(max_length=255, unique=True, null=True, blank=True)
    group_code = models.CharField(max_length=255, null=True, blank=True)
    group = models.CharField(max_length=255, null=True, blank=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    brand_code = models.CharField(max_length=255, null=True, blank=True)
    brand = models.CharField(max_length=255, null=True, blank=True)
    measure_code = models.CharField(max_length=255, null=True, blank=True)
    measure = models.CharField(max_length=255, null=True, blank=True)
    exempt = models.BooleanField(default=False)
    tax_free = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=2)
    ctm_price_1 = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    ctm_price_2 = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    offer = models.DecimalField(max_digits=1, decimal_places=4, null=True, blank=True)
    tav = models.PositiveSmallIntegerField(choices=TAV_CHOICES_DJANGO, default=5)
    final_price = models.DecimalField(
        max_digits=15, decimal_places=2, null=True, blank=True
    )
    stock = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    def get_vat_value(self):
        return self.TAV_ID_TO_VALUE.get(self.vat, 0.0)

    def get_vat_description(self):
        return self.TAV_ID_TO_DESC.get(self.vat, "Desconocido")

    def save(self, *args, **kwargs):
        if not self.final_price:
            self.final_price = self.price * (1 + self.get_vat_value / 100)
            super().save(*args, **kwargs)

    def adjust_stock(self, quantity, increase=False):
        if increase:
            self.stock += quantity
            self.save()
            return True, _("Stock increased successfully.Available: {}").format(
                self.stock
            )
        else:
            self.stock -= quantity
            self.save()

            if self.stock < 0:
                return False, _("Stock is negative. Available: {}").format(self.stock)
            return True, _("Stock decreased successfully.Available: {}").format(
                self.stock
            )
