# flake8: noqa
from rest_framework import status

from ..exceptions import CustomApiError

#
# class ProjectAlreadyExist(CustomApiError):  # noqa: D101
#     status_code = status.HTTP_409_CONFLICT
#     default_detail = 'Project with some of provided fields already exists.'
