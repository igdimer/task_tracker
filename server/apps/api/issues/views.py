import datetime

from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.authentication import TokenAuthentication
from server.apps.issues.services import IssueService, ProjectService, ReleaseService
from server.apps.users.services import UserService


class IssueCreateApi(APIView):
    """API for creation issues."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        project_id = serializers.IntegerField()
        title = serializers.CharField()
        description = serializers.CharField()
        estimated_time = serializers.DurationField(default=datetime.timedelta(seconds=0))
        assignee_id = serializers.IntegerField()
        release_id = serializers.IntegerField(required=False)

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            IssueService.create(author=request.user, **serializer.validated_data)
        except (
            ProjectService.ProjectNotFoundError,
            ReleaseService.ReleaseNotFoundError,
            UserService.UserNotFoundError,
        ) as exc:
            raise NotFound() from exc

        return Response({})
