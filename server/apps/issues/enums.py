from django.db import models


class ReleaseStatusEnum(models.TextChoices):
    """Enum of release statuses."""

    UNRELEASED = 'unreleased'
    RELEASED = 'released'


class IssueStatusEnum(models.TextChoices):
    """Enum of issue status."""

    OPEN = 'open'
    IN_PROGRESS = 'in_progress'
    CLOSED = 'closed'
    REOPENED = 'reopened'
    RESOLVED = 'resolved'
