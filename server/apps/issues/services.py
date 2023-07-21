from django.db import transaction
from django.db.utils import IntegrityError

from server.apps.core.exceptions import BaseServiceError

from .models import Comment, Issue, Project, Release  # noqa


class ProjectService:
    """Service for working with projects."""

    class ProjectNotFoundError(BaseServiceError):
        """Project does not exist."""

    class UniqueFieldsError(BaseServiceError):
        """Project with some of provided fields already exists."""

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
            with transaction.atomic():
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
    def get_by_id(cls, project_id: int) -> dict[str, str | list[dict[str, str | int | None]]]:
        """Get project."""
        project = cls.get_or_error(project_id)
        project_issues = Issue.objects.filter(project=project).select_related(
            'release',
            'assignee',
        )

        issues_data = []
        for issue in project_issues:
            issues_data.append({
                'title': issue.title,
                'code': issue.code,
                'status': issue.status,
                'release': issue.release.version if issue.release else None,
                'assignee': issue.assignee.id,
            })

        return {
            'title': project.title,
            'code': project.code,
            'description': project.description,
            'issues': issues_data,
        }
