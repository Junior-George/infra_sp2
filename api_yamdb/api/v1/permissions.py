from rest_framework import permissions


class IsAdmin(permissions.BasePermission):
    """Проверяет является ли пользователь администратором."""
    def has_permission(self, request, view):
        return request.user.is_admin or request.user.is_superuser


class ReadOnly(permissions.BasePermission):
    """Проверяет является ли тип запроса безопасным."""
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class PermissionForReviewComment(permissions.BasePermission):
    def has_permission(self, request, view):
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or obj.author == request.user
            or request.user.is_admin
            or request.user.is_superuser
            or request.user.is_moderator
        )
