from rest_framework import serializers
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework.views import APIView

from server.apps.issues.services import ProjectService
from server.apps.auth.authentication import TokenAuthentication
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
        except ProjectService.UniqueFieldsError as exc:
            raise exceptions.UniqueProjectConstraintError() from exc

        return Response({})


class ProjectUpdateApi(APIView):
    """API for updating projects."""

    authentication_classes = [TokenAuthentication]

    class InputSerializer(serializers.Serializer):
        title = serializers.CharField(required=False)
        code = serializers.CharField(required=False)
        description = serializers.CharField(required=False)

    def patch(self, request: Request) -> Response:  # noqa: D102
        serializer = self.InputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            ProjectService.update(**serializer.validated_data)
        except ProjectService.ProjectNotFoundError as exc:
            raise NotFound() from exc
        except ProjectService.UniqueFieldsError as exc:
            raise exceptions.UniqueProjectConstraintError() from exc

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
                'code': serializers.CharField(source='__str__'),
                'title': serializers.CharField(),
                'status': serializers.CharField(),
                'release': serializers.CharField(),
                'performer': serializers. CharField(),
            }),
        )

    def get(self, request: Request, project_id: int) -> Response:  # noqa: D102
        try:
            project = ProjectService.get_by_id(project_id)
        except ProjectService.ProjectNotFoundError as exc:
            raise NotFound() from exc

        data = self.OutputSerializer(project)
        return Response(data)
