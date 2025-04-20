from rest_framework_simplejwt.authentication import default_user_authentication_rule
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _


def custom_user_authentication_rule(user):

    if user is None or not user.is_active:
        raise AuthenticationFailed(_("User account is not active or does not exist."))

    if not user.emailaddress_set.filter(verified=True).exists():
        raise AuthenticationFailed(_("Email not verified."))
    return default_user_authentication_rule(user)
