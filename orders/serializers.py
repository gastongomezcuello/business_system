from rest_framework import serializers
from django.utils.translation import gettext_lazy as _

from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = "__all__"
        read_only_fields = ("order",)

    def validate_order(self, order):
        if order.status == "confirmed":
            raise serializers.ValidationError(
                _("Not allowed to modify a confirmed order.")
            )

        return order


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = "__all__"
        read_only_fields = (
            "seller",
            "subtotal",
            "total",
            "created_at",
            "status",
            "stock_status",
        )

    def create(self, validated_data):
        request = self.context.get("request")
        if request and "seller" not in validated_data:
            validated_data["seller"] = request.user
        return super().create(validated_data)

    def update(self, instance, validated_data):
        if instance.status == "confirmed":
            raise serializers.ValidationError(
                _("Not allowed to modify a confirmed order.")
            )
        return super().update(instance, validated_data)
