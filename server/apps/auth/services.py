import datetime

import jwt
from django.conf import settings
from django.utils import timezone

from .constants import ACCESS_TOKEN_LIFETIME_DAYS, REFRESH_TOKEN_LIFETIME_DAYS


class AuthService:
    """Authentication service."""

    @classmethod
    def generate_jwt_tokens(cls, email: str) -> dict[str, str]:
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
