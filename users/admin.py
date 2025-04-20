from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Profile


class ProfileInline(admin.StackedInline):
    model = Profile


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    inlines = [ProfileInline]
    fieldsets = UserAdmin.fieldsets + (
        ("Custom Fields", {"fields": ("is_admin", "is_seller")}),
    )
