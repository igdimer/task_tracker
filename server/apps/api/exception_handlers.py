import logging

from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def custom_api_exception_handler(exc: Exception, context) -> Response:
    """Modify exception handler."""
    response = exception_handler(exc, context)

    if isinstance(exc, ValidationError):
        response.data = {
            'detail': exc,
        }

    if response is None:
        response = Response(
            {'detail': 'Internal Server Error'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
        logger.exception(exc)

    return response
