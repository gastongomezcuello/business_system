from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.utils.translation import gettext_lazy as _

from .models import Product
from .serializers import ProductSerializer
from core.permissions import ORPermission, IsAdmin, IsSeller, IsSuperUser


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            return [IsAdmin()]
        elif self.action == "destroy":
            return [IsSuperUser()]
        elif self.action == "list":
            return [IsSeller()]
        return super().get_permissions()

    @action(detail=False, methods=["post"], url_path="bulk-create")
    def bulk_create(self, request):

        products_data = request.data

        if not products_data:
            return Response(
                {"detail": _("No products were provided.")},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            with transaction.atomic():
                products = [Product(**data) for data in products_data]
                Product.objects.bulk_create(products)

            return Response(
                {"detail": _("Products successfully created.")},
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            return Response(
                {"detail": _(str(e))},
                status=status.HTTP_400_BAD_REQUEST,
            )
