from unittest import mock

import jwt
import pytest

from server.apps.users.services import UserService
from server.apps.users.tests.factories import UserFactory

from ..services import AuthService


@pytest.mark.django_db()
class TestAuthServiceLogin:
    """Test method login of AuthService."""

    email = 'test@maol.com'
    first_name = 'Ozzy'
    last_name = 'Osbourne'
    password = 'fake_password'  # noqa: S105

    def test_success_login(self, mock_jwt_encode):
        """Success login and getting tokens."""
        UserService.create(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password,
        )
        result = AuthService.login(email=self.email, password=self.password)
        assert result == {
            'access_token': 'first_token',
            'refresh_token': 'second_token',
        }

    def test_incorrect_password(self, mock_jwt_encode):
        """Success login and getting tokens."""
        UserService.create(
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            password=self.password,
        )
        with pytest.raises(AuthService.InvalidPasswordError):
            AuthService.login(email=self.email, password='incorrect_password')  # noqa: S106


@pytest.mark.django_db()
class TestAuthServiceRefreshToken:
    """Test method refresh_token of AuthService."""

    email = 'test@mail.com'
    refresh_token = 'fake_refresh_token'  # noqa: S105

    @pytest.fixture()
    def mock_jwt_decode(self):
        """Mock fixture jwt.decode method."""
        with mock.patch('jwt.decode') as mock_decode:
            yield mock_decode

    def test_success_refresh(self, mock_jwt_encode, mock_jwt_decode):
        """Success refreshing."""
        UserFactory(email=self.email)
        mock_jwt_decode.return_value = {
            'user_email': self.email,
            'type': 'refresh',
        }
        result = AuthService.refresh_token(self.refresh_token)
        assert result == {
            'access_token': 'first_token',
            'refresh_token': 'second_token',
        }

    def test_expired_token(self, mock_jwt_decode):
        """Refresh token is expired."""
        mock_jwt_decode.side_effect = jwt.ExpiredSignatureError()

        with pytest.raises(AuthService.InvalidRefreshTokenError):
            AuthService.refresh_token(self.refresh_token)

    def test_incorrect_token_payload(self, mock_jwt_decode):
        """Incorrect payload of refresh token."""
        mock_jwt_decode.return_value = {'wrong_key': 'value'}

        with pytest.raises(AuthService.InvalidRefreshTokenError):
            AuthService.refresh_token(self.refresh_token)

    def test_incorrect_token_type(self, mock_jwt_decode):
        """Incorrect type of token."""
        UserFactory(email=self.email)
        mock_jwt_decode.return_value = {
            'user_email': self.email,
            'type': 'access',
        }

        with pytest.raises(AuthService.InvalidRefreshTokenError):
            AuthService.refresh_token(self.refresh_token)
