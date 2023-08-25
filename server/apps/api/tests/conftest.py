from unittest import mock

import pytest
from rest_framework.test import APIClient

from server.apps.issues.tests.factories import CommentFactory, IssueFactory
from server.apps.users.tests.factories import UserFactory


@pytest.fixture()
def user():
    """User fixture."""
    return UserFactory()


@pytest.fixture()
def issue(user):
    """Issue fixture."""
    return IssueFactory(author=user)


@pytest.fixture()
def comment(user):
    """Comment fixture."""
    return CommentFactory(author=user)


@pytest.fixture()
def authorized_client(user):
    """Test authenticated client."""
    client = APIClient()
    client.force_authenticate(user=user)

    return client


@pytest.fixture()
def admin_client():
    """Test authenticated client by admin-user."""
    user = UserFactory(email='admin@admin.com', is_admin=True)
    client = APIClient()
    client.force_authenticate(user=user)

    return client


@pytest.fixture()
def mock_issue_get_or_error(issue):
    """Mock fixture method get_or_error of IssueService."""
    with mock.patch(
        'server.apps.issues.services.IssueService.get_or_error',
        return_value=issue,
    ) as mock_method:
        yield mock_method


@pytest.fixture()
def mock_comment_get_or_error(comment):
    """Mock fixture method get_or_error of CommentService."""
    with mock.patch(
        'server.apps.issues.services.CommentService.get_or_error',
        return_value=comment,
    ) as mock_method:
        yield mock_method


@pytest.fixture()
def mock_user_get_or_error(user):
    """Mock fixture method get_or_error of UserService."""
    with mock.patch(
        'server.apps.users.services.UserService.get_or_error',
        return_value=user,
    ) as mock_method:
        yield mock_method
