from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Check whether user is admin."""

    def has_permission(self, request, view):  # noqa: D102
        return request.user.is_admin


class IsAssignee(BasePermission):
    """Check whether user is assignee of issue."""

    def has_object_permission(self, request, view, obj):  # noqa: D102
        user = request.user
        return obj.assignee == user


class IsAuthor(BasePermission):
    """Check whether user is author of comment or issue."""

    def has_object_permission(self, request, view, obj):  # noqa: D102
        user = request.user
        return obj.author == user


class IsUserProfileOwner(BasePermission):
    """Check whether user is owner of profile."""

    def has_object_permission(self, request, view, obj):  # noqa: D102
        return obj == request.user
