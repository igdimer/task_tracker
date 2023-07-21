import datetime

import factory

from server.apps.users.tests.factories import UserFactory

from ..enums import IssueStatusEnum
from ..models import Issue, Project, Release


class ProjectFactory(factory.django.DjangoModelFactory):
    """Project factory."""

    class Meta:
        model = Project

    title = factory.Sequence(lambda i: f'test_project {i + 1}')
    code = factory.Sequence(lambda i: f'TP-{i + 1}')
    description = 'Amazing test project'


class ReleaseFactory(factory.django.DjangoModelFactory):
    """Release Factory."""

    class Meta:
        model = Release

    version = factory.Sequence(lambda i: f'0.{i + 1}.0')
    description = 'New Release'
    release_date = datetime.datetime(2024, 1, 1)
    status = 'unreleased'
    project = factory.SubFactory(ProjectFactory)


class IssueFactory(factory.django.DjangoModelFactory):
    """Issue factory."""

    class Meta:
        model = Issue

    title = 'test_issue'
    description = 'easy_issue'
    estimated_time = datetime.timedelta(hours=4)
    status = IssueStatusEnum.OPEN
    author = factory.SubFactory(UserFactory, email='author@email.com')
    assignee = factory.SubFactory(UserFactory, email='assignee@email.com')
    project = factory.SelfAttribute('release.project')
    release = factory.SubFactory(ReleaseFactory)
