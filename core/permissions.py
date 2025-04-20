from rest_framework.permissions import BasePermission


class ORPermission(BasePermission):

    def __init__(self, *perms):
        self.perms = perms

    def has_permission(self, request, view):
        return any(perm().has_permission(request, view) for perm in self.perms)


class IsSeller(BasePermission):

    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and request.user.is_seller
        )


class IsAdmin(BasePermission):

    def has_permission(self, request, view):

        return bool(
            request.user and request.user.is_authenticated and request.user.is_admin
        )


class IsSuperUser(BasePermission):

    def has_permission(self, request, view):

        return bool(
            request.user and request.user.is_authenticated and request.user.is_superuser
        )
