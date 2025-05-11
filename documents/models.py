from django.db import models
from orders.models import Order
from products.models import Product
from stores.models import Store
from django.core import validators
from arca.arca_client import (
    generate_invoice,
    response_to_arca_json,
    parse_arca_response,
)
from arca.auth import get_token_sign
from arca.qr import dict_to_base64

from collections import defaultdict


class Document(models.Model):
    DOCUMENT_TYPE_CHOICES = [
        ("factura", "Factura"),
        ("remito", "Remito"),
        ("presupuesto", "Presupuesto"),
        ("recibo", "Recibo"),
        ("nota_credito", "Nota de crédito"),
    ]

    LETTER_CHOICES = [
        ("001", "A"),
        ("006", "B"),
        ("011", "C"),
        ("099", "X"),
    ]

    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES)
    document_letter = models.CharField(
        max_length=3, choices=LETTER_CHOICES, default="099"
    )
    document_number = models.CharField(max_length=8, editable=False)
    store = models.ForeignKey(Store, on_delete=models.CASCADE, null=True, blank=True)
    pdf_file = models.FileField(upload_to="documents/pdf/", null=True, blank=True)
    date = models.DateField(auto_now_add=True)
    generated = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.get_document_type_display()} #{self.document_number}"

    def save(self, *args, **kwargs):

        if not self.document_number:
            self.document_number = self.generate_document_number()
        super().save(*args, **kwargs)

    def generate_document_number(self, document_letter=None):

        filters = {"store": self.store}
        if document_letter:
            filters["document_letter"] = document_letter

        last_document = (
            self.__class__.objects.filter(**filters)
            .order_by("-document_number")
            .first()
        )
        last_number = int(last_document.document_number) if last_document else 0
        return last_number + 1

    def formatted_document_number(self):
        return str(self.document_number).zfill(8)

    def generate(self):
        pass

    class Meta:
        abstract = True


class Invoice(Document):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    b64_fiscal_data = models.TextField(null=True, blank=True)
    json_arca_request = models.JSONField(null=True, blank=True)

    def __str__(self):
        return f"Factura #{self.document_number} - Pedido #{self.order.id} - Cliente: {self.order.client.name}"

    def generate(self):
        if self.generated:
            return _("Document already generated. Cannot generate again.")

        token, sign = get_token_sign(
            cert_path=self.store.cert_path,
            key_path=self.store.key_path,
            service="wsfe",
            wsdl_url="https://wsaahomo.afip.gov.ar/ws/services/LoginCms?WSDL",
        )
        auth = {
            "Token": token,
            "Sign": sign,
            "Cuit": self.store.cuit,
        }
        header = {
            "PtoVta": self.store.store_number,
            "CbteTipo": self.document_letter,
        }
        receptor = {
            "Concepto": 1,
            "DocTipo": self.order.client.id_data.kind,
            "DocNro": self.order.client.id_data.number,
            "CbteDesde": self.document_number,
            "CbteHasta": self.document_number,
            "CbteFch": self.date.strftime("%Y%m%d"),
        }
        amounts = {
            "ImpTotal": self.order.total,
            "ImpTotConc": 0,
            "ImpNeto": self.order.subtotal,
            "ImpOpEx": 0,
            "ImpTrib": 0,
            "ImpIVA": self.order.vat_total(),
        }

        tributos = []

        totals_by_vat = defaultdict(lambda: {"base_imponible": 0, "iva": 0})

        for item in self.order.items.all():

            vat_code = item.product.vat
            vat_value = item.product.get_vat_value()

            subtotal = item.subtotal()
            vat_perception = subtotal * (vat_value / 100)

            totals_by_vat[vat_code]["base_imponible"] += subtotal
            totals_by_vat[vat_code]["iva"] += vat_perception

        ivas = [
            {
                "Id": codigo,
                "BaseImp": round(datos["base_imponible"], 2),
                "Importe": round(datos["iva"], 2),
            }
            for codigo, datos in totals_by_vat.items()
            if datos["base_imponible"] > 0
        ]
        response = generate_invoice(
            auth=auth,
            header=header,
            receptor=receptor,
            amounts=amounts,
            tributos=tributos,
            ivas=ivas,
        )

        arca_data = parse_arca_response(response)
        data_to_64 = response_to_arca_json(arca_data, self.order.total)
        self.b64_fiscal_data = dict_to_base64(arca_data)
        self.json_arca_request = arca_data
        self.generated = True

        self.save()

    def save(self, *args, **kwargs):

        if not self.document_type:
            self.document_type = "factura"

        if not self.document_letter:

            if self.store.vat_condition == "monotributista":
                self.document_letter = "011"

            elif self.store.vat_condition == "responsable_inscripto":
                if self.order.client.vat_condition in (
                    "monotributista",
                    "responsable_inscripto",
                ):
                    self.document_letter = "001"
                elif self.order.client.vat_condition in ("exento", "consumidor_final"):
                    self.document_letter = "006"

        super().save(*args, **kwargs)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "document_type",
                    "document_letter",
                    "document_number",
                    "store",
                ],
                name="unique_invoice_document_per_store",
            )
        ]


class Receipt(Document):
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE)
    payment = models.OneToOneField("clients.PaymentRecord", on_delete=models.CASCADE)

    def __str__(self):
        return f"Recibo #{self.document_number} - Cliente: {self.client.name}"

    def save(self, *args, **kwargs):

        if not self.document_type:
            self.document_type = "recibo"

        if not self.document_letter:
            self.document_letter = "X"

        super().save(*args, **kwargs)


class DeliveryNote(Document):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    products_delivered = models.TextField()
    observations = models.TextField(null=True, blank=True)
    recipient = models.CharField(max_length=255)
    shipping_address = models.CharField(max_length=200)

    def __str__(self):
        return f"Remito #{self.document_number} - Pedido #{self.order.id} - Cliente: {self.order.client.name}"


class Budget(Document):
    observations = models.TextField(null=True, blank=True)
    valid_until = models.DateField()

    def __str__(self):
        return f"Presupuesto #{self.document_number}"


class BudgetItem(models.Model):
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def subtotal(self):
        return self.product.price * self.quantity


class CreditNote(Document):
    invoice = models.OneToOneField(Invoice, on_delete=models.CASCADE)
    observations = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Nota de crédito #{self.document_number} - Factura #{self.invoice.document_number}"

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=[
                    "document_type",
                    "document_letter",
                    "document_number",
                    "store",
                ],
                name="unique_credit_note_document_per_store",
            )
        ]


class Reservation(Document):
    client = models.ForeignKey("clients.Client", on_delete=models.CASCADE)
    reserved_until = models.DateField(
        default=lambda: timezone.now().date() + timezone.timedelta(days=15)
    )
    status = models.CharField(
        max_length=15,
        choices=[
            ("active", "Active"),
            ("expired", "Expired"),
            ("confirmed", "Confirmed"),
            ("cancelled", "Cancelled"),
        ],
        default="active",
    )

    def confirm(self):
        if self.status != "active":
            raise ValidationError("Only active reservations can be confirmed.")

        order = self.create_order()
        self.status = "confirmed"
        self.save()
        return order

    def cancel(self):
        if self.status == "active":
            self.status = "cancelled"
            self.save()

    def is_expired(self):
        return self.reserved_until < timezone.now().date()

    def create_order(self):
        order = Order.objects.create(client=self.client)
        for item in self.items.all():
            OrderItem.objects.create(
                order=order, product=item.product, quantity=item.quantity
            )
        return order

    def __str__(self):
        return f"Reservation #{self.document_number} - Client: {self.client.name}"


class ReservationItem(models.Model):
    reservation = models.ForeignKey(
        Reservation, on_delete=models.CASCADE, related_name="items"
    )
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.product.name} (x{self.quantity}) - Reservation #{self.reservation.document_number}"


class Return(Document):
    order = models.OneToOneField(Order, on_delete=models.CASCADE)
    products_returned = models.TextField()
    observations = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Devolución #{self.document_number} - Pedido #{self.order.id} - Cliente: {self.order.client.name}"
