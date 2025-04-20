from django.shortcuts import render
from django.conf import settings


from django.contrib.auth.models import User

from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from dj_rest_auth.registration.serializers import VerifyEmailSerializer

from allauth.account.views import ConfirmEmailView


class EmailVerification(APIView, ConfirmEmailView):

    def get(self, request, *args, **kwargs):
        key = kwargs.get("key")
        return render(
            request,
            "registration/verify_email.html",
            context={"key": key, "BASE_URL": settings.BASE_URL},
        )

    def post(self, request, *args, **kwargs):
        serializer = VerifyEmailSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.kwargs["key"] = serializer.validated_data["key"]
        confirmation = self.get_object()
        confirmation.confirm(self.request)
        return Response(
            {"detail": "Email address has been verified."},
            status=status.HTTP_200_OK,
        )
