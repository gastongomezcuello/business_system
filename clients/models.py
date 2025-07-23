from django.db import models
from django.utils.translation import gettext_lazy as _


class IdDocument(models.Model):

    KIND_CHOICES = [
        ("80", "CUIT"),
        ("86", "CUIL"),
        ("96", "DNI"),
        ("89", "LE"),
        ("90", "LC"),
        ("94", "PASSPORT"),
    ]

    kind = models.CharField(
        max_length=50, choices=KIND_CHOICES, default="80", blank=True, null=True
    )
    number = models.CharField(
        max_length=11, unique=True, editable=False, blank=True, null=True
    )

    def __str__(self):
        return f"{self.kind} - {self.number}"


class Client(models.Model):
    VAT_CONDITIONS = [
        ("responsable_inscripto", "Responsable inscripto"),
        ("monotributista", "Monotributista"),
        ("exento", "Exento"),
        ("consumidor_final", "Consumidor final"),
    ]

    vat_condition = models.CharField(
        max_length=50, choices=VAT_CONDITIONS, default="consumidor_final"
    )
    id_data = models.OneToOneField(
        IdDocument,
        on_delete=models.CASCADE,
        related_name="client",
        null=True,
        blank=True,
    )
    code = models.CharField(
        max_length=20, unique=True, editable=False, null=True, blank=True
    )

    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    address = models.TextField()
    city = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    phone_1 = models.CharField(max_length=15)
    phone_2 = models.CharField(max_length=15)
    cellphone = models.CharField(max_length=15, blank=True, null=True)
    cellphone_2 = models.CharField(max_length=15, blank=True, null=True)
    page = models.URLField(blank=True, null=True)
    contact_name = models.CharField(max_length=100, blank=True, null=True)
    representative = models.CharField(max_length=100, blank=True, null=True)
    credit_limit = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    price_level = models.CharField(blank=True, null=True, max_length=50)
    discount = models.DecimalField(
        max_digits=15, decimal_places=2, default=0.00, blank=True, null=True
    )
    observations = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Account(models.Model):
    client = models.OneToOneField(Client, on_delete=models.CASCADE)
    account_number = models.CharField(max_length=20, unique=True, editable=False)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    debt = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    last_payment_date = models.DateTimeField(null=True, blank=True)
    last_update = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{_('Account number')} {self.account_number}"

    def update_balance(self):

        total_paid = sum(self.payments.values_list("amount", flat=True))
        self.balance = self.debt - total_paid
        self.save()

    def add_debt(self, amount):

        self.debt += amount
        self.update_balance()

    def cancel_debt(self):

        self.debt = 0
        self.balance = 0
        self.payments.all().delete()
        self.save()


class PaymentRecord(models.Model):
    account = models.ForeignKey(
        Account, on_delete=models.CASCADE, related_name="payments"
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    method = models.CharField(
        max_length=50,
        choices=[
            ("cash", "Efectivo"),
            ("card", "Tarjeta"),
            ("transfer", "Transferencia"),
        ],
    )
    date = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):

        super().save(*args, **kwargs)
        self.account.update_balance()
