import pytest

from ...auth.services import AuthService
from .factories import UserFactory


@pytest.mark.django_db()
class TestUserService:
    """Testing methods of UserService."""

    @pytest.fixture()
    def user(self):
        """User instance fixture."""
        return UserFactory()

    def test_get_or_error_success(self, user):
        """Check get_or_error method in case user exists."""
        user = AuthService.get_or_error(email='test@email.com')

        assert user
        assert user.first_name == 'Ozzy'
        assert user.last_name == 'Osbourne'
