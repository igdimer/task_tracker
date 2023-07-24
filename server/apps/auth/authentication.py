import logging

import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.request import Request

from server.apps.users.models import User
from server.apps.users.services import UserService

logger = logging.getLogger(__name__)


class TokenAuthentication(BaseAuthentication):
    """Authentication class with JWT Tokens."""

    def authenticate(self, request: Request) -> tuple[User, None]:
        """User authentication."""
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            raise AuthenticationFailed()

        token = auth_header.split()[1]
        try:
            decoded = jwt.decode(
                token,
                settings.JWT_TOKEN_SECRET,
                algorithms=['HS256'],
            )
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed()

        try:
            user_email = decoded['user_email']
            token_type = decoded['type']
        except KeyError:
            raise AuthenticationFailed()

        try:
            user = UserService.get_by_email(email=user_email)
        except UserService.UserNotFoundError:
            raise AuthenticationFailed()
        except Exception as exc:
            logger.exception(exc)
            raise AuthenticationFailed()

        if token_type != 'access':  # noqa: S105
            raise AuthenticationFailed()

        return user, None

    def authenticate_header(self, request: Request) -> str:
        """Return string for header WWW-Authenticate."""
        return 'Unauthorized'
