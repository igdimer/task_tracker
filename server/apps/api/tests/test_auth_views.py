from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.auth.services import AuthService
from server.apps.users.services import UserService


class TestSignUpApi:
    """Testing SignUpApi."""

    client = APIClient()
    email = 'test@mail.com'
    first_name = 'Ozzy'
    last_name = 'Osbourne'

    default_payload = {
        'email': email,
        'first_name': first_name,
        'last_name': last_name,
        'password': 'fake_password',
    }

    @pytest.fixture()
    def mock_signup(self):
        """Mock fixture for method signup of AuthService."""
        with mock.patch('server.apps.auth.services.AuthService.signup') as signup_mock:
            yield signup_mock

    def test_success_response(self, mock_signup):
        """Check success response."""
        mock_signup.return_value = {'email': self.email}

        response = self.client.post(
            reverse('auth:signup'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {'email': self.email}
        mock_signup.assert_called_with(  # noqa: S106
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            password='fake_password',
        )

    def test_success_response_with_admin_secret(self, mock_signup):
        """Check success response with provided secret."""
        mock_signup.return_value = {'email': self.email}
        payload = {
            'email': self.email,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'password': 'fake_password',
            'secret': 'fake_secret',
        }

        response = self.client.post(
            reverse('auth:signup'),
            payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {'email': self.email}
        mock_signup.assert_called_with(  # noqa: S106
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            password='fake_password',
            secret='fake_secret',
        )

    def test_user_already_exist(self, mock_signup):
        """User already exists."""
        mock_signup.side_effect = AuthService.UserAlreadyExistError()
        response = self.client.post(
            reverse('auth:signup'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 409
        assert response.json() == {
            'detail': 'User with specified email already exists in database.',
        }

    def test_invalid_auth_secret(self, mock_signup):
        """Invalid secret was provided."""
        mock_signup.side_effect = AuthService.InvalidAuthSecretError()
        response = self.client.post(
            reverse('auth:signup'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': 'Incorrect data to set user as admin.',
        }

    def test_method_not_allowed(self):
        """Incorrect HTTP method."""
        response = self.client.get(
            reverse('auth:signup'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "GET" not allowed.',
        }

    def test_incorrect_parameters(self, mock_signup):
        """Incorrect response parameters."""
        payload = {
            'wrong_key': 'value',
        }
        response = self.client.post(
            reverse('auth:signup'),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'email': ['This field is required.'],
                'first_name': ['This field is required.'],
                'last_name': ['This field is required.'],
                'password': ['This field is required.'],
            },
        }

    def test_internal_error(self, mock_signup):
        """Internal server error."""
        mock_signup.side_effect = Exception()
        response = self.client.post(
            reverse('auth:signup'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


class TestLoginApi:
    """Testing LoginApi."""

    client = APIClient()

    default_payload = {
        'email': 'test@email.com',
        'password': 'fake_password',  # noqa: S106
    }

    @pytest.fixture()
    def mock_login(self):
        """Mock fixture login method of AuthService."""
        with mock.patch('server.apps.auth.services.AuthService.login') as login_mock:
            yield login_mock

    def test_success(self, mock_login):
        """Success response."""
        mock_login.return_value = {
            'access_token': 'fake_access_token',
            'refresh_token': 'fake_refresh_token',
        }
        response = self.client.post(
            reverse('auth:login'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {
            'access_token': 'fake_access_token',
            'refresh_token': 'fake_refresh_token',
        }

    def test_user_not_found(self, mock_login):
        """User with provided email not found."""
        mock_login.side_effect = UserService.UserNotFoundError()

        response = self.client.post(
            reverse('auth:login'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_method_not_allowed(self):
        """Incorrect HTTP method."""
        response = self.client.get(
            reverse('auth:login'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "GET" not allowed.',
        }

    def test_incorrect_parameters(self):
        """Incorrect response parameters."""
        payload = {
            'wrong_key': 'value',
        }
        response = self.client.post(
            reverse('auth:login'),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'email': ['This field is required.'],
                'password': ['This field is required.'],
            },
        }

    def test_internal_error(self, mock_login):
        """Internal server error."""
        mock_login.side_effect = Exception()
        response = self.client.post(
            reverse('auth:login'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


class TestRefreshTokenApi:
    """Testing RefreshTokenApi."""

    client = APIClient()

    default_payload = {'refresh_token': 'fake_token'}

    @pytest.fixture()
    def mock_refresh_token(self):
        """Mock fixture login method of AuthService."""
        with mock.patch('server.apps.auth.services.AuthService.refresh_token') as refresh_mock:
            yield refresh_mock

    def test_success(self, mock_refresh_token):
        """Success response."""
        mock_refresh_token.return_value = {
            'access_token': 'fake_access_token',
            'refresh_token': 'fake_refresh_token',
        }
        response = self.client.post(
            reverse('auth:token_refresh'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {
            'access_token': 'fake_access_token',
            'refresh_token': 'fake_refresh_token',
        }

    def test_user_not_found(self, mock_refresh_token):
        """User with provided email not found."""
        mock_refresh_token.side_effect = UserService.UserNotFoundError()

        response = self.client.post(
            reverse('auth:token_refresh'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_method_not_allowed(self):
        """Incorrect HTTP method."""
        response = self.client.get(
            reverse('auth:token_refresh'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "GET" not allowed.',
        }

    def test_incorrect_parameters(self):
        """Incorrect response parameters."""
        payload = {
            'wrong_key': 'value',
        }
        response = self.client.post(
            reverse('auth:token_refresh'),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'refresh_token': ['This field is required.'],
            },
        }

    def test_internal_error(self, mock_refresh_token):
        """Internal server error."""
        mock_refresh_token.side_effect = Exception()
        response = self.client.post(
            reverse('auth:token_refresh'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }
