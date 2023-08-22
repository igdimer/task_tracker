import datetime

from django.db import models

from server.apps.core.models import BaseModel

from ..users.models import User
from .enums import IssueStatusEnum, ReleaseStatusEnum


class Project(BaseModel):
    """Model of project that is being worked on by issues."""

    title = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=15, unique=True)
    description = models.TextField()

    class Meta:
        db_table = 'projects'
        verbose_name = 'project'
        verbose_name_plural = 'projects'

    def __str__(self) -> str:
        """Text representation."""
        return self.code


class Release(BaseModel):
    """Model of release of projects."""

    version = models.CharField(max_length=20)
    description = models.TextField()
    release_date = models.DateField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=ReleaseStatusEnum.choices,
        default=ReleaseStatusEnum.UNRELEASED,
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    class Meta:
        db_table = 'releases'
        verbose_name = 'release'
        verbose_name_plural = 'releases'
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'version'],
                name='release_project_id_version_key',
            ),
        ]

    def __str__(self) -> str:
        """Text representation."""
        return f'{self.project.code}: {self.version}'


class Issue(BaseModel):
    """Issue model."""

    title = models.CharField(max_length=200)
    description = models.TextField()
    code = models.CharField(max_length=25, unique=True, blank=True)
    estimated_time = models.DurationField()
    logged_time = models.DurationField(default=datetime.timedelta(seconds=0))
    status = models.CharField(
        max_length=20,
        choices=IssueStatusEnum.choices,
        default=IssueStatusEnum.OPEN,
    )
    author = models.ForeignKey(User, on_delete=models.RESTRICT, related_name='issues_reported_by')
    assignee = models.ForeignKey(
        User,
        on_delete=models.RESTRICT,
        related_name='issues_assigned_to',
    )
    project = models.ForeignKey(Project, on_delete=models.RESTRICT)
    release = models.ForeignKey(Release, on_delete=models.RESTRICT, null=True, blank=True)

    class Meta:
        db_table = 'issues'
        verbose_name = 'issue'
        verbose_name_plural = 'issues'

    def __str__(self) -> str:
        """Text representation."""
        return self.code

    def save(self, *args, **kwargs) -> None:
        """Additionally set field 'number'."""
        if not self.code:
            project = self.project
            issue_count = Issue.objects.filter(project=project).count()
            self.code = f'{project.code}-{issue_count + 1}'
        super().save(*args, **kwargs)

    def get_release_version(self):
        """Get release version or None if no release."""
        if self.release is not None:
            return self.release.version
        return None

    @property
    def remaining_time(self) -> datetime.timedelta:
        """Calculate remaining working time."""
        if self.estimated_time < self.logged_time:
            return datetime.timedelta(seconds=0)

        return self.estimated_time - self.logged_time


class Comment(BaseModel):
    """Model of comment on the issue."""

    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.RESTRICT)
    issue = models.ForeignKey(Issue, on_delete=models.CASCADE)

    class Meta:
        db_table = 'comments'
        verbose_name = 'comment'
        verbose_name_plural = 'comments'

    def __str__(self) -> str:
        """Text representation."""
        return f'Comment to issue {self.issue.title}'
