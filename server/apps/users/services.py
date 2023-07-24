import datetime

from django.db import IntegrityError

from server.apps.core.exceptions import BaseServiceError
from server.apps.issues.models import Issue

from .models import User


class UserService:
    """Service for working with users."""

    class UserNotFoundError(BaseServiceError):
        """User with specified email does not exist."""

    class UserAlreadyExist(BaseServiceError):
        """User with provided email already exists."""

    @classmethod
    def get_or_error(cls, user_id: int) -> User:
        """Get user by id or raise exception."""
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise cls.UserNotFoundError()

        return user

    @classmethod
    def get_by_email(cls, email: str) -> User:
        """Get user by email or raise exception."""
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise cls.UserNotFoundError()

        return user

    @classmethod
    def get_by_id(cls, user_id: int) -> dict[str, str | list[dict[str, str | None]]]:
        """Get user by id."""
        user = cls.get_or_error(user_id)

        issues = Issue.objects.filter(assignee=user).select_related('release')

        issues_data = []
        for issue in issues:
            issues_data.append({
                'title': issue.title,
                'code': issue.code,
                'status': issue.status,
                'release': issue.release.version if issue.release else None,
            })

        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'issues': issues_data,
        }

    @classmethod
    def update(cls, user_id: int, **kwargs) -> None:
        """Update existing user."""
        user = cls.get_or_error(user_id)

        for key, value in kwargs.items():
            setattr(user, key, value)

        try:
            user.save()
        except IntegrityError as exc:
            raise cls.UserAlreadyExist() from exc

    @classmethod
    def get_assigned_issues(
        cls,
        user: User,
    ) -> dict[str, list[dict[str, str | datetime.timedelta | None]]]:
        """Get issues assigned to authenticated user."""
        issues = user.my_issues.all().select_related('release')

        issue_data: list[dict[str, str | datetime.timedelta | None]] = []
        for issue in issues:
            issue_data.append({
                'title': issue.title,
                'code': issue.code,
                'status': issue.status,
                'estimated_time': issue.estimated_time,
                'release': issue.release.version if issue.release else None,
            })

        return {'issues': issue_data}
