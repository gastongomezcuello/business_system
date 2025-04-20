from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_nested.routers import NestedDefaultRouter
from .views import ClientViewSet, PaymentsViewSet

router = DefaultRouter()
router.register(r"clients", ClientViewSet, basename="clients")

clients_router = NestedDefaultRouter(router, r"clients", lookup="client")
clients_router.register(r"payments", PaymentsViewSet, basename="client-payments")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(clients_router.urls)),
]
