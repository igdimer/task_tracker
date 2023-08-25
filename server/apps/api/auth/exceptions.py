from rest_framework import status

from ..exceptions import CustomApiError


class InvalidPasswordError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Invalid password was provided.'


class RefreshTokenFailError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_406_NOT_ACCEPTABLE
    default_detail = 'Attempt to refresh token failed.'
