from django.db import models


class Store(models.Model):
    VAT_CONDITIONS = [
        ("responsable_inscripto", "Responsable inscripto"),
        ("monotributista", "Monotributista"),
    ]

    vat_condition = models.CharField(
        max_length=50, choices=VAT_CONDITIONS, default="responsable_inscripto"
    )
    models.PositiveIntegerField(unique=True)
    store_number = models.CharField(
        max_length=4, null=True, unique=True, editable=False
    )
    address = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=50)
    name = models.CharField(max_length=100)
    gross_income_id = models.CharField(max_length=20, blank=True, null=True)
    cuit = models.CharField(max_length=20)
    cbu = models.CharField(max_length=22)
    start_date = models.DateField(null=True, blank=True)

    def save(self, *args, **kwargs):

        if not self.store_number:
            self.store_number = self.generate_store_number()
        super().save(*args, **kwargs)

    def generate_store_number(self):
        last_store = Store.objects.all().order_by("-store_number").first()
        last_number = int(last_store.store_number) if last_store else 0
        return last_number + 1

    def formatted_store_number(self):
        return str(self.store_number).zfill(4)
