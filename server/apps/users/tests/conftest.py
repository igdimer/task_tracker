import pytest

from .factories import UserFactory


@pytest.fixture()
def user():
    """User fixture."""
    return UserFactory()


@pytest.fixture()
def author():
    """User fixture."""
    return UserFactory(email='author@email.com')
