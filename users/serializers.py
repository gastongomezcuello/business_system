from rest_framework import serializers

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db.utils import IntegrityError

from dj_rest_auth.registration.serializers import RegisterSerializer

from allauth.account.adapter import get_adapter
from allauth.account.utils import setup_user_email

from django.utils.translation import gettext_lazy as _

from .models import CustomUser


class CustomUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = "__all__"


class CustomRegisterSerializer(RegisterSerializer):
    # username = serializers.CharField(required=True)

    first_name = serializers.CharField(
        max_length=30,
        required=True,
    )
    last_name = serializers.CharField(
        max_length=30,
        required=True,
    )

    def validate_email(self, email):

        if CustomUser.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                _(
                    "An account already exists with this email address. Please sign in to that "
                )
            )
        return email

    def get_cleaned_data(self):
        return {
            "username": self.validated_data.get("username", ""),
            "password1": self.validated_data.get("password1", ""),
            "email": self.validated_data.get("email", ""),
            "first_name": self.validated_data.get("first_name", ""),
            "last_name": self.validated_data.get("last_name", ""),
        }

    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user = adapter.save_user(request, user, self, commit=False)
        if "password1" in self.cleaned_data:
            try:
                adapter.clean_password(self.cleaned_data["password1"], user=user)
            except DjangoValidationError as exc:
                raise serializers.ValidationError(
                    detail=serializers.as_serializer_error(exc)
                )
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]

        try:
            user.save()
        except IntegrityError:
            raise serializers.ValidationError(
                {
                    "email": _(
                        "An account already exists with this email address. Please sign in to that "
                    )
                }
            )

        self.custom_signup(request, user)
        setup_user_email(request, user, [])
        return user
