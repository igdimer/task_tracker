import datetime
import hashlib

import jwt
from django.conf import settings
from django.utils import timezone

from server.apps.core.exceptions import BaseServiceError
from server.apps.users.models import User
from server.apps.users.services import UserService

from .constants import ACCESS_TOKEN_LIFETIME_DAYS, REFRESH_TOKEN_LIFETIME_DAYS


class AuthService:
    """Service for authentication."""

    class UserAlreadyExistError(BaseServiceError):
        """User with provided email already exists in database."""

    class InvalidPasswordError(BaseServiceError):
        """Invalid password was provided."""

    class InvalidRefreshTokenError(BaseServiceError):
        """Invalid refresh token was provided."""

    @classmethod
    def signup(  # noqa: S107
        cls,
        email: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> dict[str, str]:
        """Sign up in the system."""
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'first_name': first_name,
                'last_name': last_name,
                'password': cls._hash_password(password, email),
            },
        )
        if not created:
            raise cls.UserAlreadyExistError()

        return {'email': email}

    @classmethod
    def login(cls, email: str, password: str) -> dict[str, str]:
        """Log in."""
        user = UserService.get_by_email(email)

        hashed_password = cls._hash_password(password=password, email=email)
        if user.password != hashed_password:
            raise cls.InvalidPasswordError()

        return cls._generate_jwt_tokens(email)

    @classmethod
    def refresh_token(cls, refresh_token: str) -> dict[str, str]:
        """Update access token by refresh token."""
        try:
            decoded = jwt.decode(refresh_token, settings.JWT_TOKEN_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError as exc:
            raise cls.InvalidRefreshTokenError() from exc

        try:
            user_email = decoded['user_email']
            token_type = decoded['type']
        except KeyError as exc:
            raise cls.InvalidRefreshTokenError() from exc

        UserService.get_by_email(user_email)
        if token_type != 'refresh':  # noqa: S105
            raise cls.InvalidRefreshTokenError()

        return cls._generate_jwt_tokens(user_email)

    @classmethod
    def _hash_password(cls, password: str, email: str) -> str:
        """Hash user password to save into database."""
        secret = settings.AUTH_SECRET
        string = secret + password + email
        hashed_password = hashlib.sha256(string.encode())

        return hashed_password.hexdigest()

    @classmethod
    def _generate_jwt_tokens(cls, email: str) -> dict[str, str]:
        """Generate access and refresh tokens."""
        access_exp_time = (timezone.now() + datetime.timedelta(days=ACCESS_TOKEN_LIFETIME_DAYS))
        refresh_exp_time = (timezone.now() + datetime.timedelta(days=REFRESH_TOKEN_LIFETIME_DAYS))

        access_token = jwt.encode(
            {
                'type': 'access',
                'user_email': email,
                'exp': access_exp_time,
            },
            settings.JWT_TOKEN_SECRET,
            algorithm='HS256',
        )
        refresh_token = jwt.encode(
            {
                'type': 'refresh',
                'user_email': email,
                'exp': refresh_exp_time,
            },
            settings.JWT_TOKEN_SECRET,
            algorithm='HS256',
        )

        return {'access_token': access_token, 'refresh_token': refresh_token}
