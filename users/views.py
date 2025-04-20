from rest_framework.viewsets import ModelViewSet

from django.contrib.auth import get_user_model
from .serializers import CustomUserSerializer
from core.permissions import IsSuperUser


User = get_user_model()


class UserViewSet(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = CustomUserSerializer

    def get_permissions(self):

        return [IsSuperUser()]
