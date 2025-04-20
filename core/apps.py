# core/apps.py
from django.apps import AppConfig
from django.contrib import admin
from django.http import HttpResponseForbidden


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    # def ready(self):
    #     # Personalizar el login del admin
    #     def custom_admin_login(request):
    #         if not request.user.is_superuser:
    #             return HttpResponseForbidden("Acceso denegado")
    #         return admin.site.login(request)

    #     admin.site.login = custom_admin_login
