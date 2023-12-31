import datetime

import factory

from server.apps.users.tests.factories import UserFactory

from ..enums import IssueStatusEnum
from ..models import Comment, Issue, Project, Release


class ProjectFactory(factory.django.DjangoModelFactory):
    """Project factory."""

    class Meta:
        model = Project
        django_get_or_create = ('title',)

    title = 'test_project'
    code = 'TT'
    description = 'Amazing test project'
    owner = factory.SubFactory(UserFactory, email='owner@email.com')


class ReleaseFactory(factory.django.DjangoModelFactory):
    """Release Factory."""

    class Meta:
        model = Release

    version = factory.Sequence(lambda i: f'0.{i + 1}.0')
    description = 'New Release'
    release_date = datetime.date(2024, 1, 1)
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
    project = factory.SubFactory(ProjectFactory)
    release = factory.SubFactory(ReleaseFactory)


class CommentFactory(factory.django.DjangoModelFactory):
    """Comment factory."""

    class Meta:
        model = Comment

    text = 'test_text'
    author = factory.SubFactory(UserFactory)
    issue = factory.SubFactory(IssueFactory)
