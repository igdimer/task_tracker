from rest_framework import serializers, status
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.services import AuthService
from server.apps.users.services import UserService

from . import exceptions


class SignUpApi(APIView):
    """API for user registration."""

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.signup(**serializer.validated_data)
        except AuthService.UserAlreadyExistError as exc:
            raise exceptions.UserAlreadyExistError() from exc

        data = self.OutputSerializer(result).data
        return Response(data, status=status.HTTP_201_CREATED)


class LoginApi(APIView):
    """API for user log in."""

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.login(**serializer.validated_data)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc
        except AuthService.InvalidPasswordError as exc:
            raise exceptions.InvalidPasswordError() from exc

        data = self.OutputSerializer(result).data
        return Response(data)


class RefreshTokenApi(APIView):
    """API for updating access token by refresh token."""

    class InputSerializer(serializers.Serializer):
        refresh_token = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.refresh_token(**serializer.validated_data)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc
        except AuthService.InvalidRefreshTokenError as exc:
            raise exceptions.RefreshTokenFailError() from exc

        data = self.OutputSerializer(result).data
        return Response(data)
