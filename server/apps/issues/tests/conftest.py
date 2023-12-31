from unittest import mock

import pytest

from server.apps.users.tests.factories import UserFactory

from .factories import CommentFactory, IssueFactory, ProjectFactory, ReleaseFactory


@pytest.fixture()
def project():
    """Project fixture."""
    return ProjectFactory()


@pytest.fixture()
def release(project):
    """Release fixture."""
    return ReleaseFactory(project=project, version='0.1.0')


@pytest.fixture()
def user():
    """User fixture."""
    return UserFactory(email='user@mail.com')


@pytest.fixture()
def author():
    """User fixture."""
    return UserFactory(email='author@mail.com')


@pytest.fixture()
def issue(user, author, project):
    """User fixture."""
    return IssueFactory(author=author, assignee=user, project=project, release=None)


@pytest.fixture()
def comment(issue, user):
    """Comment fixture."""
    return CommentFactory(author=user, issue=issue)


@pytest.fixture()
def mock_notification_task():
    """Mock-fixture send_notification_task."""
    with mock.patch('server.apps.issues.tasks.send_notification_task.delay') as mock_task:
        yield mock_task
