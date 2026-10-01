from rest_framework import permissions


class IsOrganizerOrReadOnly(permissions.BasePermission):
    """Anyone can read; only organizers (staff users) can create or change sessions."""

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)


class IsOrganizer(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.is_staff)
