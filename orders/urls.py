from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_nested.routers import NestedDefaultRouter

from .views import OrderViewSet, OrderItemViewSet

router = DefaultRouter()
router.register("orders", OrderViewSet, basename="orders")

orders_router = NestedDefaultRouter(router, "orders", lookup="order")
orders_router.register("order-items", OrderItemViewSet, basename="order-items")

urlpatterns = [
    path("", include(router.urls)),
    path("", include(orders_router.urls)),
]
