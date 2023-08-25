from django.db import IntegrityError, transaction
from django.db.models import QuerySet

from server.apps.core.exceptions import BaseServiceError
from server.apps.core.utils import hash_password
from server.apps.issues.models import Issue

from .models import User


class UserService:
    """Service for working with users."""

    class UserNotFoundError(BaseServiceError):
        """User with specified email does not exist."""

    class UserAlreadyExistError(BaseServiceError):
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
    def get_user_info(cls, user_id: int) -> dict[str, str | QuerySet[Issue]]:
        """Get user by id."""
        user = cls.get_or_error(user_id)

        return {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'issues': user.issues_assigned_to.select_related('release'),
        }

    @classmethod
    def create(
        cls,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        is_admin: bool = False,
    ) -> None:
        """Create new user."""
        hashed_password = hash_password(password=password, email=email)
        try:
            with transaction.atomic():
                User.objects.create(
                    email=email,
                    password=hashed_password,
                    is_admin=is_admin,
                    first_name=first_name,
                    last_name=last_name,
                )
        except IntegrityError:
            raise cls.UserAlreadyExistError()

    @classmethod
    def update(cls, user: User, **kwargs) -> None:
        """Update existing user."""
        for key, value in kwargs.items():
            setattr(user, key, value)

        try:
            user.save()
        except IntegrityError as exc:
            raise cls.UserAlreadyExistError() from exc

    @classmethod
    def get_assigned_issues(cls, user: User) -> dict[str, QuerySet[Issue]]:
        """Get issues assigned to authenticated user."""
        return {'issues': user.issues_assigned_to.select_related('release')}
