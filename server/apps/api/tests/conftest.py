import pytest
from rest_framework.test import APIClient

from server.apps.issues.tests.factories import IssueFactory
from server.apps.users.tests.factories import UserFactory


@pytest.fixture()
def user():
    """User fixture."""
    return UserFactory()


@pytest.fixture()
def issue():
    """Issue fixture."""
    return IssueFactory()


@pytest.fixture()
def authorized_client(user):
    """Тестовый клиент API c аутентификацией."""
    client = APIClient()
    client.force_authenticate(user=user)

    return client
