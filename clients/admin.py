from django.contrib import admin

from .models import Client, PaymentRecord, Account


class AccountInline(admin.StackedInline):

    model = Account


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
