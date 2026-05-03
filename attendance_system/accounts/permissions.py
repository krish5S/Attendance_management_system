from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Only admin users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsTeacher(BasePermission):
    """Only teacher users."""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'teacher'


class IsAdminOrTeacher(BasePermission):
    """Admin or teacher."""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated and
            request.user.role in ('admin', 'teacher')
        )


class IsAdminOrReadOnly(BasePermission):
    """Admin can write; authenticated users can read."""
    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and request.user.role == 'admin'


class IsOwnerOrAdmin(BasePermission):
    """Object-level: owner or admin only."""
    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # obj must have a `user` or `marked_by` field
        owner = getattr(obj, 'user', None) or getattr(obj, 'marked_by', None)
        return owner == request.user