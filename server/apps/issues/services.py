import datetime

from django.db import transaction
from django.db.utils import IntegrityError

from server.apps.core.exceptions import BaseServiceError

from .models import Comment, Issue, Project, Release  # noqa


class ProjectService:
    """Service for working with projects."""

    class ProjectNotFoundError(BaseServiceError):
        """Project does not exist."""

    class ProjectAlreadyExist(BaseServiceError):
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
            raise cls.ProjectAlreadyExist() from exc

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
            raise cls.ProjectAlreadyExist() from exc

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


class ReleaseService:
    """Service for working with releases."""

    class ReleaseNotFoundError(BaseServiceError):
        """Project does not exist."""

    class ReleaseAlreadyExist(BaseServiceError):
        """Release already exists."""

    @classmethod
    def _get_or_error(cls, release_id: int):
        """Get release or raise exception."""
        try:
            release = Release.objects.get(id=release_id)
        except Release.DoesNotExist:
            raise cls.ReleaseNotFoundError()

        return release

    @classmethod
    def create(
        cls,
        project_id: int,
        version: str,
        description: str,
        release_date: datetime.date | None = None,
    ) -> None:
        """Create release."""
        project = ProjectService.get_or_error(project_id=project_id)

        try:
            Release.objects.create(
                project=project,
                version=version,
                description=description,
                release_date=release_date,
            )
        except IntegrityError as exc:
            raise cls.ReleaseAlreadyExist() from exc

    @classmethod
    def get_by_id(cls, release_id: int) -> dict[str, dict[str, str | datetime.date]]:
        """Get release by id."""
        release = cls._get_or_error(release_id=release_id)
        return {
            'version': release.version,
            'description': release.description,
            'release_date': release.release_date,
            'status': release.status,
        }

    @classmethod
    def update(cls, release_id: int, **kwargs) -> None:
        """Edit existing release."""
        release = cls._get_or_error(release_id=release_id)

        for key, value in kwargs.items():
            if value is not None:
                setattr(release, key, value)

        try:
            release.save()
        except IntegrityError as exc:
            raise cls.ReleaseAlreadyExist() from exc
