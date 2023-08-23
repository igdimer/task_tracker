from rest_framework import status

from ..exceptions import CustomApiError


class ReleaseNotBelongToProject(CustomApiError):  # noqa: D101
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = 'Release does not belong provided project.'
