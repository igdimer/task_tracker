import datetime

from django.db import transaction
from django.db.utils import IntegrityError

from server.apps.core.exceptions import BaseServiceError
from server.apps.users.models import User
from server.apps.users.services import UserService

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
        """Release does not exist."""

    class ReleaseAlreadyExist(BaseServiceError):
        """Release already exists."""

    @classmethod
    def get_or_error(cls, release_id: int) -> Release:
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
    def get_by_id(cls, release_id: int) -> Release:
        """Get release by id."""
        return cls.get_or_error(release_id=release_id)

    @classmethod
    def update(cls, release_id: int, **kwargs) -> None:
        """Edit existing release."""
        release = cls.get_or_error(release_id=release_id)

        for key, value in kwargs.items():
            if value is not None:
                setattr(release, key, value)

        try:
            release.save()
        except IntegrityError as exc:
            raise cls.ReleaseAlreadyExist() from exc


class IssueService:
    """Service for working with issues."""

    class IssueNotFoundError(BaseServiceError):
        """Issue does not exist."""

    @classmethod
    def _get_or_error(cls, issue_id: int) -> Issue:
        """Get issue or raise exception."""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            raise cls.IssueNotFoundError()

        return issue

    @classmethod
    def get_by_id(cls, issue_id: int) -> Issue:
        """Get issue by id."""
        return cls._get_or_error(issue_id)

    @classmethod
    def create(
        cls,
        project_id: int,
        title: str,
        description: str,
        estimated_time: datetime.timedelta,
        author: User,
        assignee_id: int,
        release_id: int | None = None,
    ):
        """Create issue."""
        project = ProjectService.get_or_error(project_id=project_id)
        assignee = UserService.get_user_by_id(user_id=assignee_id)
        if release_id is not None:
            ReleaseService.get_or_error(release_id=release_id)

        Issue.objects.create(
            project=project,
            release_id=release_id,
            assignee=assignee,
            author=author,
            title=title,
            description=description,
            estimated_time=estimated_time,
        )
