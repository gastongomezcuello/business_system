from rest_framework import serializers


from .models import Client, PaymentRecord, IdDocument


class IdDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = IdDocument
        fields = "__all__"


class ClientSerializer(serializers.ModelSerializer):
    id_data = IdDocumentSerializer()

    class Meta:
        model = Client
        fields = [
            "vat_condition",
            "id_data",
            "name",
            "email",
            "address",
            "phone",
        ]


class PaymentRecordSerializer(serializers.ModelSerializer):

    class Meta:
        model = PaymentRecord
        fields = ["amount", "method", "date", "account"]
        read_only_fields = ["date", "account"]
