from django.contrib import admin
from .models import Budget, CreditNote, Invoice, Receipt, DeliveryNote


class DocumentAdmin(admin.ModelAdmin):
    list_display = ("document_type", "document_number", "date")
    search_fields = ("document_number",)
    list_filter = ("document_type", "date")


@admin.register(Budget)
class BudgetAdmin(DocumentAdmin):
    list_display = ("document_number", "date", "valid_until", "observations")


@admin.register(CreditNote)
class CreditNoteAdmin(DocumentAdmin):
    list_display = ("document_number", "date", "observations")


@admin.register(Invoice)
class InvoiceAdmin(DocumentAdmin):
    list_display = ("document_number", "date")


@admin.register(Receipt)
class ReceiptAdmin(DocumentAdmin):
    list_display = ("document_number", "date")


@admin.register(DeliveryNote)
class DeliveryNoteAdmin(DocumentAdmin):
    list_display = ("document_number", "date", "recipient", "shipping_address")
