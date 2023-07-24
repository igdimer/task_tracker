import pytest

from server.apps.users.tests.factories import UserFactory

from .factories import IssueFactory, ProjectFactory, ReleaseFactory


@pytest.fixture()
def project():
    """Project fixture."""
    return ProjectFactory(title='test_project', code='TT')


@pytest.fixture()
def release(project):
    """Release fixture."""
    return ReleaseFactory(project=project, version='0.1.0')


@pytest.fixture()
def user():
    """User fixtures."""
    return UserFactory(email='user@mail.com')


@pytest.fixture()
def author():
    """User fixtures."""
    return UserFactory(email='author@mail.com')


@pytest.fixture()
def issue(user, author, project):
    """User fixtures."""
    return IssueFactory(author=author, assignee=user, project=project, release=None)
