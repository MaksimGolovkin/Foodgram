from rest_framework import permissions


class IsAuthorOrReadOnly(permissions.BasePermission):
    """Кастомное разрешение на доступ к информации только авторам."""

    def has_object_permission(self, request, view, obj):
        return request.method in permissions.SAFE_METHODS or (
            obj.author == request.user)


class AnonimOrAuthenticatedReadOnly(permissions.BasePermission):
    """Костомное разрешение анонимному или авторизованному пользователю
    только безопасные запросы."""

    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS or (
            request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        return (
            (request.method in permissions.SAFE_METHODS
             and (request.user.is_anonymous
                  or request.user.is_authenticated))
            or request.user.is_superuser
            or request.user.is_staff
        )
