from rest_framework import serializers


from .models import Document, Invoice


class DocumentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Document
        fields = "__all__"
        read_only_fields = ["document_type", "document_letter", "document_number"]

    def create(self, validated_data):
        request = self.context.get("request")
        if request and "store" not in validated_data:
            validated_data["store"] = request.user.store
        return super().create(validated_data)
