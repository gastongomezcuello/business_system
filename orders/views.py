from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status

from django.db import transaction
from django.utils.translation import gettext as _


from .serializers import OrderSerializer, OrderItemSerializer
from core.permissions import IsSeller, IsAdmin, IsSuperUser, ORPermission
from .models import Order, OrderItem


class OrderViewSet(ModelViewSet):
    queryset = Order.objects.all()
    serializer_class = OrderSerializer

    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "list"]:
            return [ORPermission(IsSeller, IsAdmin)]
        elif self.action == "destroy":
            return [IsSuperUser()]
        return super().get_permissions()

    @action(detail=True, methods=["post"], url_path="confirm")
    def confirm_order(self, request, pk=None):

        try:
            order = self.get_object()
            if order.status == "confirmed":
                return Response(
                    {"detail": _("Order already confirmed.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            order.confirm_order()
            serializer = self.get_serializer(order)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({"detail": _(str(e))}, status=status.HTTP_400_BAD_REQUEST)


class OrderItemViewSet(ModelViewSet):
    queryset = OrderItem.objects.all()
    serializer_class = OrderItemSerializer

    def perform_create(self, serializer):
        order = get_object_or_404(Order, pk=self.kwargs["order_pk"])

        if order.status == "confirmed":
            raise ValidationError(_("Not allowed to add items to confirmed order."))

        serializer.save(order=order)

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "list"]:
            return [ORPermission(IsSeller, IsAdmin)]
        elif self.action == "destroy":
            return [IsSuperUser()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request, order_pk=None):

        items_data = request.data.get("items", [])

        if not order_id or not items_data:
            return Response(
                {"detail": _("Missing data")}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            order = Order.objects.get(id=order_pk)

            if order.status == "confirmed":
                return Response(
                    {"detail": _("Not allowed to add items to confirmed orders.")},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            serializer = self.get_serializer(data=items_data, many=True)
            serializer.is_valid(raise_exception=True)

            with transaction.atomic():
                items = [
                    OrderItem(order=order, **validated_data)
                    for validated_data in serializer.validated_data
                ]
                OrderItem.objects.bulk_create(items)
            return Response(
                {"detail": _("Items created.")}, status=status.HTTP_201_CREATED
            )

        except Order.DoesNotExist:
            return Response(
                {"detail": _("Order not found.")}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response({"detail": _(str(e))}, status=status.HTTP_400_BAD_REQUEST)
