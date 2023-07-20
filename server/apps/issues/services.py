from django.db import IntegrityError

from server.apps.core.exceptions import BaseServiceError

from .models import Comment, Issue, Project, Release


class ProjectService:
    """Service for working with projects."""

    class ProjectNotFoundError(BaseServiceError):
        """Project does not exist."""

    class UniqueFieldsError(BaseServiceError):
        """Project already exists with some of provided fields."""

    @classmethod
    def get_or_error(cls, project_id: int):
        """Get project or raise exception."""
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            raise cls.ProjectNotFoundError()

        return project

    @classmethod
    def create(cls, title: str, code: str, description: str) -> None:
        """Create project."""
        try:
            Project.objects.create(title=title, code=code, description=description)
        except IntegrityError as exc:
            raise cls.UniqueFieldsError() from exc

    @classmethod
    def update(cls, project_id: int, **kwargs) -> None:
        """Edit existing project."""
        project = cls.get_or_error(project_id)

        for key, value in kwargs.items():
            if value is not None:
                setattr(project, key, value)

        try:
            project.save()
        except IntegrityError as exc:
            raise cls.UniqueFieldsError() from exc

    @classmethod
    def get_by_id(cls, project_id: int) -> dict[str, str]:
        """Get project."""
        project = cls.get_or_error(project_id)
        project_issues = Issue.objects.filter(project=project).values(
            'title',
            '__str__',
            'status',
            'release',
            'performer',
        )

        return {
            'title': project.title,
            'code': project.code,
            'description': project.description,
            'issues': project_issues,
        }
