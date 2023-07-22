from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.authentication import TokenAuthentication
from server.apps.users.services import UserService

from ..utils import inline_serializer
from . import exceptions


class UserDetailApi(APIView):
    """API for getting user."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        is_admin = serializers.BooleanField()
        issues = serializers.ListField(
            child=inline_serializer(fields={
                'code': serializers.CharField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'release': serializers.CharField(),
            }),
        )

    def get(self, request: Request, user_id: int) -> Response:  # noqa: D102
        try:
            user = UserService.get_by_id(user_id)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(user).data
        return Response(data)


class UserUpdateApi(APIView):
    """API for updating user profile data."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField(required=False)
        first_name = serializers.CharField(required=False)
        last_name = serializers.CharField(required=False)

        def validate(self, attrs):
            """Validate at least one necessary field was provided."""
            if not attrs:
                raise ValidationError('No necessary fields were passed.')

            return attrs

    def patch(self, request: Request, user_id: int) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            UserService.update(user_id=user_id, **serializer.validated_data)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc
        except UserService.UserAlreadyExist as exc:
            raise exceptions.UniqueUserConstraintError() from exc

        return Response({})


class UserGetAssignedIssuesApi(APIView):
    """API for updating user profile data."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        issues = serializers.ListField(
            child=inline_serializer(fields={
                'code': serializers.CharField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'estimated_time': serializers.DurationField(),
                'release': serializers.CharField(),
            }),
        )

    def get(self, request: Request) -> Response:  # noqa: D102
        issues = UserService.get_assigned_issues(request.user)

        data = self.OutputSerializer(issues).data
        return Response(data)
