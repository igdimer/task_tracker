from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.services import AuthService

from . import exceptions


class SignUpApi(APIView):
    """
    API for user registration.

    To sign up as admin provide field 'secret' equal AUTH_SECRET constant defined in .env file.
    """

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        password = serializers.CharField()
        secret = serializers.CharField(required=False)

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.signup(**serializer.validated_data)
        except AuthService.UserAlreadyExistError as exc:
            raise exceptions.UserAlreadyExistError() from exc
        except AuthService.InvalidAuthSecretError as exc:
            raise exceptions.AdminSetFailError() from exc

        data = self.OutputSerializer(result).data
        return Response(data)


class LoginApi(APIView):
    """API for user log in."""

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        password = serializers.CharField()

    class OutputSerializer(serializers.Serializer):
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    def get(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.login(**serializer.validated_data)
        except AuthService.UserNotFoundError as exc:
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

    def get(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = AuthService.refresh_token(**serializer.validated_data)
        except AuthService.UserNotFoundError as exc:
            raise NotFound() from exc
        except AuthService.InvalidRefreshTokenError as exc:
            raise exceptions.RefreshTokenFailError() from exc

        data = self.OutputSerializer(result).data
        return Response(data)
