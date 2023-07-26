import datetime

from rest_framework import serializers
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.authentication import TokenAuthentication
from server.apps.issues.services import (CommentService, IssueService, ProjectService,
                                         ReleaseService)
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


class IssueDetailApi(APIView):
    """API for getting issues."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        title = serializers.CharField()
        code = serializers.CharField()
        description = serializers.CharField()
        estimated_time = serializers.DurationField()
        logged_time = serializers.DurationField()
        remaining_time = serializers.DurationField()
        author = serializers.IntegerField()
        assignee = serializers.IntegerField()
        project = serializers.CharField()
        status = serializers.CharField()
        release = serializers.CharField(allow_null=True)

    def get(self, request: Request, issue_id: int) -> Response:  # noqa: D102
        try:
            issue = IssueService.get_by_id(issue_id)
        except IssueService.IssueNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(issue).data
        return Response(data)


class IssueListApi(APIView):
    """API for getting issues list."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        title = serializers.CharField()
        code = serializers.CharField()
        description = serializers.CharField()
        estimated_time = serializers.DurationField()
        logged_time = serializers.DurationField()
        remaining_time = serializers.DurationField()
        author = serializers.IntegerField()
        assignee = serializers.IntegerField()
        project = serializers.CharField()
        status = serializers.CharField()
        release = serializers.CharField(allow_null=True)

    def get(self, request: Request) -> Response:  # noqa: D102
        issues = IssueService.get_list()
        data = self.OutputSerializer(issues, many=True).data

        return Response(data)


class IssueUpdateApi(APIView):
    """
    API for updating issues.

    You should use this API for all editing operations with issues: resolving, logging time,
    reopening, changing assignee, etc. To perform action provide corresponding fields.

    For example: to resolve issue and log working time provide field 'logged_time' with necessary
    duration time value and field 'status' with value 'resolved' (see IssueStatusEnum).

    Logged time will be added to existing value of issue instance.
    """

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False)
        description = serializers.CharField(required=False)
        estimated_time = serializers.DurationField(required=False)
        logged_time = serializers.DurationField(required=False)
        status = serializers.CharField(required=False)
        assignee_id = serializers.IntegerField(required=False)
        release_id = serializers.IntegerField(required=False, allow_null=True)

        def validate(self, attrs):
            """Validate at least one necessary field was provided."""
            if not attrs:
                raise ValidationError('No necessary fields were passed.')

            return attrs

    def patch(self, request: Request, issue_id: int) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            IssueService.update(issue_id=issue_id, **serializer.validated_data)
        except (
            IssueService.IssueNotFoundError,
            UserService.UserNotFoundError,
            ReleaseService.ReleaseNotFoundError,
        ) as exc:
            raise NotFound() from exc

        return Response({})


class CommentCreateApi(APIView):
    """API for creation comments."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField()

    def post(self, request: Request, issue_id: int) -> Response:   # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            CommentService.create(
                author=request.user,
                issue_id=issue_id,
                **serializer.validated_data,
            )
        except IssueService.IssueNotFoundError as exc:
            raise NotFound() from exc

        return Response({})


class CommentDetailApi(APIView):
    """API for getting comments."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        text = serializers.CharField()
        author_id = serializers.IntegerField()
        created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    def get(self, request: Request, issue_id: int, comment_id: int) -> Response:   # noqa: D102
        try:
            comment = CommentService.get_by_id(issue_id=issue_id, comment_id=comment_id)
        except (IssueService.IssueNotFoundError, CommentService.CommentNotFoundError) as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(comment).data
        return Response(data)


class CommentUpdateApi(APIView):
    """API for updating comments."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        text = serializers.CharField()

    def patch(self, request: Request, issue_id: int, comment_id: int) -> Response:   # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            CommentService.update(
                issue_id=issue_id,
                comment_id=comment_id,
                **serializer.validated_data,
            )
        except (CommentService.CommentNotFoundError, IssueService.IssueNotFoundError) as exc:
            raise NotFound() from exc

        return Response({})


class CommentListApi(APIView):
    """API for getting comments list."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        text = serializers.CharField()
        author_id = serializers.IntegerField()
        created_at = serializers.DateTimeField(format='%Y-%m-%d %H:%M')

    def get(self, request: Request, issue_id: int) -> Response:  # noqa: D102
        try:
            comments = CommentService.get_list(issue_id=issue_id)
        except IssueService.IssueNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(comments, many=True).data

        return Response(data)
