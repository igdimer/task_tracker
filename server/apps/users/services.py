import hashlib

from django.conf import settings

from server.apps.auth.services import AuthService
from server.apps.core.exceptions import BaseServiceError

from .models import User


class UserService:
    """Service for working with users."""

    class UserAlreadyExist(BaseServiceError):
        """User with specified email already exists in database."""

    @classmethod
    def signup(  # noqa: S107
        cls,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
        secret: str = '',
    ) -> dict[str, str]:
        """Sign up in the system."""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'password': cls._hash_password(password, email),
                'is_admin': True if secret == settings.AUTH_SECRET else False,
            },
        )
        if not created:
            raise cls.UserAlreadyExist()

        return {'email': email, **AuthService.generate_jwt_tokens(email)}

    @classmethod
    def _hash_password(cls, password: str, email: str) -> str:
        """Hash user password to save into database."""
        secret = settings.AUTH_SECRET
        string = secret + password + email
        hashed_password = hashlib.sha256(string.encode())

        return hashed_password.hexdigest()
