import copy
import datetime

from django.db import transaction
from django.db.models.query import QuerySet
from django.db.utils import IntegrityError

from server.apps.core.exceptions import BaseServiceError
from server.apps.users.models import User
from server.apps.users.services import UserService

from .models import Comment, Issue, Project, Release
from .tasks import send_notification_task


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
            setattr(project, key, value)

        try:
            project.save()
        except IntegrityError as exc:
            raise cls.ProjectAlreadyExist() from exc

    @classmethod
    def get_by_id(cls, project_id: int) -> dict[str, str | QuerySet[Issue]]:
        """Get project."""
        project = cls.get_or_error(project_id)

        return {
            'title': project.title,
            'code': project.code,
            'description': project.description,
            'issues': project.issue_set.select_related('release', 'assignee'),
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
    def get_or_error(cls, issue_id: int) -> Issue:
        """Get issue or raise exception."""
        try:
            issue = Issue.objects.get(id=issue_id)
        except Issue.DoesNotExist:
            raise cls.IssueNotFoundError()

        return issue

    @classmethod
    def get_by_id(cls, issue_id: int) -> Issue:
        """Get issue by id."""
        try:
            issue = Issue.objects.select_related('project', 'release').get(id=issue_id)
        except Issue.DoesNotExist:
            raise cls.IssueNotFoundError()

        return issue

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
        assignee = UserService.get_or_error(user_id=assignee_id)
        if release_id is not None:
            ReleaseService.get_or_error(release_id=release_id)

        issue = Issue.objects.create(
            project=project,
            release_id=release_id,
            assignee=assignee,
            author=author,
            title=title,
            description=description,
            estimated_time=estimated_time,
        )

        if author != assignee:
            message = f'Issue {issue.code} {issue.title} created'
            send_notification_task.delay(
                emails=[assignee.email],
                subject='New issue',
                message=message,
            )

    @classmethod
    def get_list(cls) -> QuerySet[Issue]:
        """Get issues list."""
        issues = Issue.objects.all().select_related('project', 'release')

        return issues

    @classmethod
    def update(cls, issue_id: int, user: User, **kwargs) -> None:
        """Edit existing issue."""
        issue = cls.get_or_error(issue_id)
        notified_emails = []
        updated_fields = copy.copy(kwargs)

        if 'release_id' in kwargs:
            release_id = kwargs['release_id']
            if release_id is not None:
                ReleaseService.get_or_error(release_id)

        assignee_id = kwargs.pop('assignee_id', None)
        if assignee_id is not None:
            new_assignee = UserService.get_or_error(assignee_id)
            notified_emails.append(issue.assignee.email)  # to notify previous assignee
            issue.assignee = new_assignee

        logged_time = kwargs.pop('logged_time', None)
        if logged_time is not None:
            issue.logged_time += logged_time

        for key, value in kwargs.items():
            setattr(issue, key, value)

        issue.save()

        notified_emails = [email for email
                           in set(notified_emails + [issue.assignee.email, issue.author.email])
                           if email != user.email]

        if notified_emails:
            message = f'Issue {issue.code} updated:\n'
            for key in updated_fields:
                value = getattr(issue, key)
                message += f'{key}: {value}\n'

            send_notification_task.delay(
                emails=notified_emails,
                subject=f'Issue {issue.code} updated',
                message=message,
            )


class CommentService:
    """Service for working with comments."""

    class CommentNotFoundError(BaseServiceError):
        """Comment was not found."""

    @classmethod
    def create(cls, issue_id: int, author: User, text: str) -> None:
        """Create comment for issue."""
        issue = IssueService.get_or_error(issue_id)

        Comment.objects.create(
            author=author,
            issue=issue,
            text=text,
        )

        notified_emails = [email for email
                           in {issue.assignee.email, issue.author.email}
                           if email != author.email]

        if notified_emails:
            message = f'Issue {issue.code} was commented'
            send_notification_task.delay(
                emails=notified_emails,
                subject=f'Issue {issue.code} was commented',
                message=message,
            )

    @classmethod
    def get_by_id(cls, issue_id: int, comment_id: int):
        """Get comment by id."""
        issue = IssueService.get_or_error(issue_id)

        try:
            comment = Comment.objects.get(issue=issue, id=comment_id)
        except Comment.DoesNotExist:
            raise cls.CommentNotFoundError()

        return comment

    @classmethod
    def update(cls, issue_id: int, comment_id: int, text: str) -> None:
        """Update existing comment."""
        comment = cls.get_by_id(issue_id=issue_id, comment_id=comment_id)
        comment.text = text
        comment.save()

    @classmethod
    def get_list(cls, issue_id: int) -> QuerySet[Comment]:
        """Get comments list of issue."""
        issue = IssueService.get_or_error(issue_id=issue_id)
        return Comment.objects.filter(issue=issue)
