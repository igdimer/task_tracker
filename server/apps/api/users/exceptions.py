from rest_framework import status

from ..exceptions import CustomApiError


class UniqueUserConstraintError(CustomApiError):  # noqa: D101
    status_code = status.HTTP_409_CONFLICT
    default_detail = 'User with provided email already exists.'
