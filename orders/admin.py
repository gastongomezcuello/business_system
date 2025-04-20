from django.contrib import admin

from .models import Order, OrderItem


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):

    model = Order


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):

    model = OrderItem
