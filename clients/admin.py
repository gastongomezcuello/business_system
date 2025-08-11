from django.contrib import admin

from .models import Client, PaymentRecord, Account, IdDocument


class AccountInline(admin.StackedInline):
    model = Account
    can_delete = False
    extra = 0

    def has_add_permission(self, request, obj):

        return obj is not None and hasattr(obj, "account")

    def has_change_permission(self, request, obj=None):
        return self.has_add_permission(request, obj)


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):

    model = Client
    inlines = [AccountInline]


@admin.register(PaymentRecord)
class PaymentRecordAdmin(admin.ModelAdmin):

    model = PaymentRecord


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):

    model = Account


@admin.register(IdDocument)
class IdDocumentAdmin(admin.ModelAdmin):
    model = IdDocument
    list_display = ("number", "kind")
