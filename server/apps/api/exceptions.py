from rest_framework.exceptions import APIException


class CustomApiError(APIException):
    """Base API exception class."""
