from rest_framework import serializers
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users.services import UserService

from .exceptions import UserAlreadyExist


class UserSignUpView(APIView):
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
        access_token = serializers.CharField()
        refresh_token = serializers.CharField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            result = UserService.signup(**serializer.validated_data)
        except UserService.UserAlreadyExist as exc:
            raise UserAlreadyExist() from exc

        data = self.OutputSerializer(result).data
        return Response(data)
