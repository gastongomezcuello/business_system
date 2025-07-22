from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin
from rest_framework.response import Response
from rest_framework import status
from arca.pdf_generator import generate_pdf


class DocumentViewSet(CreateModelMixin, GenericViewSet):
    queryset = []
    serializer_class = None

    def create(self, request, *args, **kwargs):
        document = request.data
        try:
            pdf_path = generate_pdf(document)
            return Response(
                {"pdf_path": pdf_path, "message": "Documento generado correctamente."},
                status=status.HTTP_201_CREATED,
            )
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response(
                {"error": "Error interno al generar el documento."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
