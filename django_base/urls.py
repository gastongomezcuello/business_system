from django.contrib import admin
from django.urls import path, include, re_path
from dj_rest_auth.registration.views import ResendEmailVerificationView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from django_base.views import EmailVerification


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/users/", include("users.urls")),
    path("api/clients/", include("clients.urls")),
    path("api/orders/", include("orders.urls")),
    path("api/products/", include("products.urls")),
    path("api/documents/", include("documents.urls")),
    path("dj-rest-auth/", include("dj_rest_auth.urls")),
    path("dj-rest-auth/registration/", include("dj_rest_auth.registration.urls")),
    path(
        "dj-rest-auth/resend-email/",
        ResendEmailVerificationView.as_view(),
        name="rest_resend_email",
    ),
    path("accounts/", include("allauth.urls")),
    re_path(
        r"signup/account-confirm-email/(?P<key>[\s\d\w().+-_',:&]+)/$",
        EmailVerification.as_view(),
        name="account_confirm_email",
    ),
]
