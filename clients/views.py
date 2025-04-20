from rest_framework.exceptions import ValidationError
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from .models import Client, PaymentRecord
from .serializers import ClientSerializer, PaymentRecordSerializer
from core.permissions import IsSeller, IsAdmin, IsSuperUser, ORPermission
from django.utils.translation import gettext_lazy as _


class ClientViewSet(ModelViewSet):
    queryset = Client.objects.all()
    serializer_class = ClientSerializer

    def get_permissions(self):
        if self.action == "create":
            return [ORPermission(IsSeller, IsAdmin)]

        elif self.action in ["update", "partial_update"]:
            return [IsAdmin()]
        elif self.action == "destroy":
            return [IsSuperUser()]
        elif self.action == "list":
            return [IsAdmin()]
        return super().get_permissions()


class PaymentsViewSet(ModelViewSet):
    queryset = PaymentRecord.objects.all()
    serializer_class = PaymentRecordSerializer

    def get_permissions(self):
        if self.action == "create":
            return [ORPermission(IsSeller, IsAdmin)]
        elif self.action in ["update", "partial_update"]:
            return [IsAdmin()]
        elif self.action == "destroy":
            return [IsSuperUser()]
        elif self.action == "list":
            return [IsAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        client_id = self.kwargs.get("client_pk")

        client = get_object_or_404(Client, pk=client_id)
        account = getattr(client, "account", None)
        if not account:
            raise ValidationError(_("Client does not have an associated account."))

        serializer.save(account=account)
