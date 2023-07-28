from rest_framework import serializers, status
from rest_framework.exceptions import NotFound, ValidationError
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.auth.authentication import TokenAuthentication
from server.apps.issues.enums import ReleaseStatusEnum
from server.apps.issues.services import ProjectService, ReleaseService

from ..utils import inline_serializer
from . import exceptions


class ProjectCreateApi(APIView):
    """API for creating projects."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField()
        code = serializers.CharField()
        description = serializers.CharField()

    def post(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectService.create(**serializer.validated_data)
        except ProjectService.ProjectAlreadyExist as exc:
            raise exceptions.ProjectAlreadyExist() from exc

        return Response({}, status=status.HTTP_201_CREATED)


class ProjectUpdateApi(APIView):
    """API for updating projects."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False)
        code = serializers.CharField(required=False)
        description = serializers.CharField(required=False)

        def validate(self, attrs):
            """Validate at least one necessary field was provided."""
            if not attrs:
                raise ValidationError('No necessary fields were passed.')

            return attrs

    def patch(self, request: Request, project_id: int) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectService.update(project_id=project_id, **serializer.validated_data)
        except ProjectService.ProjectNotFoundError as exc:
            raise NotFound() from exc
        except ProjectService.ProjectAlreadyExist as exc:
            raise exceptions.ProjectAlreadyExist() from exc

        return Response({})


class ProjectDetailApi(APIView):
    """API for getting project."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        title = serializers.CharField()
        code = serializers.CharField()
        description = serializers.CharField()
        issues = serializers.ListField(
            child=inline_serializer(fields={
                'code': serializers.CharField(),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'release': serializers.CharField(),
                'assignee': serializers.CharField(),
            }),
        )

    def get(self, request: Request, project_id: int) -> Response:  # noqa: D102
        try:
            project = ProjectService.get_by_id(project_id)
        except ProjectService.ProjectNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(project).data
        return Response(data)


class ReleaseCreateApi(APIView):
    """API for creating release."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        version = serializers.CharField()
        release_date = serializers.DateField(required=False)
        description = serializers.CharField()

    def post(self, request: Request, project_id: int) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ReleaseService.create(project_id=project_id, **serializer.validated_data)
        except ReleaseService.ReleaseAlreadyExist as exc:
            raise exceptions.ReleaseAlreadyExist() from exc
        except ProjectService.ProjectNotFoundError as exc:
            raise NotFound() from exc

        return Response({}, status=status.HTTP_201_CREATED)


class ReleaseDetailApi(APIView):
    """API for creating release."""

    authentication_classes = [TokenAuthentication]

    class OutputSerializer(serializers.Serializer):
        version = serializers.CharField()
        description = serializers.CharField()
        release_date = serializers.DateField(allow_null=True)
        status = serializers.CharField()

    def get(self, request: Request, release_id: int) -> Response:  # noqa: D102
        try:
            release = ReleaseService.get_by_id(release_id=release_id)
        except ReleaseService.ReleaseNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(release).data
        return Response(data)


class ReleaseUpdateApi(APIView):
    """API for updating projects."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        version = serializers.CharField(required=False)
        description = serializers.CharField(required=False)
        status = serializers.ChoiceField(required=False, choices=ReleaseStatusEnum.choices)
        release_date = serializers.DateField(required=False)

        def validate(self, attrs):
            """Validate at least one necessary field was provided."""
            if not attrs:
                raise ValidationError('No necessary fields were passed.')

            return attrs

    def patch(self, request: Request, release_id: int) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ReleaseService.update(release_id=release_id, **serializer.validated_data)
        except ReleaseService.ReleaseNotFoundError as exc:
            raise NotFound() from exc
        except ReleaseService.ReleaseAlreadyExist as exc:
            raise exceptions.ReleaseAlreadyExist() from exc

        return Response({})
