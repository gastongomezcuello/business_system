from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    InvoiceViewSet,
    ReceiptViewSet,
    DeliveryNoteViewSet,
    BudgetViewSet,
    CreditNoteViewSet,
    ReturnViewSet,
)

router = DefaultRouter()
router.register(r"invoices", InvoiceViewSet, basename="invoices")
router.register(r"receipts", ReceiptViewSet, basename="receipts")
router.register(r"delivery-notes", DeliveryNoteViewSet, basename="delivery-notes")
router.register(r"budgets", BudgetViewSet, basename="budgets")
router.register(r"credit-notes", CreditNoteViewSet, basename="credit-notes")
router.register(r"returns", ReturnViewSet, basename="returns")

urlpatterns = [
    path("", include(router.urls)),
]
