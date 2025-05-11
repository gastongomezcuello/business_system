from django.db import models
from django.utils.translation import gettext_lazy as _

from django.core.exceptions import ValidationError

from clients.models import Client
from users.models import CustomUser
from products.models import Product


class Order(models.Model):
    client = models.ForeignKey(Client, on_delete=models.CASCADE)
    seller = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    subtotal = models.DecimalField(
        max_digits=10, decimal_places=2, blank=True, null=True
    )
    total = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    status = models.CharField(max_length=50, default="pending")
    stock_status = models.CharField(max_length=50, default="pending")

    def __str__(self):
        return f"Pedido #{self.id} - Cliente: {self.client.name}"

    def save(self, *args, **kwargs):

        if self.pk and self.status == "confirmed":
            raise ValidationError(_("Not allowed to modify a confirmed order."))

        super().save(*args, **kwargs)

    def confirm_order(self):
        if self.status != "confirmed":
            self.status = "confirmed"
            self.subtotal = self.calculate_subtotal()
            self.total = self.calculate_total()
            self.save()

    def calculate_subtotal(self):
        return sum(item.subtotal() for item in self.items.all())

    def calculate_total(self):
        return sum(item.total() for item in self.items.all())

    def vat_total(self):
        return sum(
            (item.subtotal() * item.product.get_vat_value() / 100)
            for item in self.items.all()
        )


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    returned_quantity = models.PositiveIntegerField(default=0)

    def save(self, *args, **kwargs):
        if self.pk:
            original = OrderItem.objects.get(pk=self.pk)
            if self.order != original.order:
                raise ValidationError(_("Cannot change the order of an existing item."))
        super().save(*args, **kwargs)

    def subtotal(self):
        return self.product.price * self.quantity

    def total(self):
        return self.product.final_price * self.quantity

    def available_for_return(self):
        return self.quantity - self.returned_quantity

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) - Available for return: {self.available_for_return()}"
