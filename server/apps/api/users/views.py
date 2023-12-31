from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.users.services import UserService

from .. import permissions
from ..utils import inline_serializer
from . import exceptions


class UserCreateApi(APIView):
    """API for creation users."""

    permission_classes = [permissions.IsAdmin]

    class InputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        password = serializers.CharField()
        is_admin = serializers.BooleanField(required=False)

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            UserService.create(**serializer.validated_data)
        except UserService.UserAlreadyExistError as exc:
            raise exceptions.UserAlreadyExistError from exc

        return Response({}, status=status.HTTP_201_CREATED)


class UserDetailApi(APIView):
    """API for getting user."""

    class OutputSerializer(serializers.Serializer):
        email = serializers.EmailField()
        first_name = serializers.CharField()
        last_name = serializers.CharField()
        issues = serializers.ListField(
            child=inline_serializer(fields={
                'code': serializers.CharField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'release': serializers.CharField(source='get_release_version'),
            }),
        )

    def get(self, request: Request, user_id: int) -> Response:  # noqa: D102
        try:
            user = UserService.get_user_info(user_id)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(user).data
        return Response(data)


class UserUpdateApi(APIView):
    """API for updating user profile data."""

    permission_classes = [permissions.IsAdmin | permissions.IsUserProfileOwner]

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
            user = UserService.get_or_error(user_id=user_id)
        except UserService.UserNotFoundError as exc:
            raise NotFound() from exc

        self.check_object_permissions(request, user)

        try:
            UserService.update(user=user, **serializer.validated_data)
        except UserService.UserAlreadyExistError as exc:
            raise exceptions.UniqueUserConstraintError() from exc

        return Response({})


class UserGetAssignedIssuesApi(APIView):
    """API for updating user profile data."""

    class OutputSerializer(serializers.Serializer):
        issues = serializers.ListField(
            child=inline_serializer(fields={
                'code': serializers.CharField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'estimated_time': serializers.DurationField(),
                'release': serializers.CharField(source='get_release_version'),
            }),
        )

    def get(self, request: Request) -> Response:  # noqa: D102
        issues = UserService.get_assigned_issues(request.user)

        data = self.OutputSerializer(issues).data
        return Response(data)
