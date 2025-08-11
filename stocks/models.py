from django.db import models
from django.utils.translation import gettext_lazy as _


class StockLocation(models.Model):

    LOCATION_TYPES = [
        ("van", "Camioneta"),
        ("warehouse", "Almacén"),
        ("store", "Sucursal"),
        ("distribution_center", "Centro de distribución"),
    ]

    name = models.CharField(max_length=100, unique=True)

    locattion_type = models.CharField(
        max_length=50, choices=LOCATION_TYPES, default="warehouse"
    )
    address = models.CharField(max_length=255, null=True, blank=True)
    identifier = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):

        if self.identifier:
            return f"{self.name} ({self.identifier})"
        elif self.address:
            return f"{self.name} ({self.address})"
        else:
            return self.name


class Stock(models.Model):
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    stock_location = models.ForeignKey(
        StockLocation, on_delete=models.CASCADE, related_name="stocks"
    )
    quantity = models.DecimalField(_("Quantity"), max_digits=5, decimal_places=2)

    def __str__(self):
        return f"{self.product.name} - {self.stock_location.name} ({self.quantity})"

    class Meta:
        unique_together = ("product", "stock_location")


class StockMovement(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    from_location = models.ForeignKey(
        StockLocation,
        related_name="outgoing",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    to_location = models.ForeignKey(
        StockLocation,
        related_name="incoming",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    note = models.TextField(blank=True, null=True)
