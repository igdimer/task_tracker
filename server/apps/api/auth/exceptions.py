from rest_framework import status

from ..exceptions import CustomApiError


class UserAlreadyExistError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'User with specified email already exists in database.'


class InvalidPasswordError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Invalid password was provided.'


class RefreshTokenFailError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Attempt to refresh token failed.'
