from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.auth.services import AuthService
from server.apps.users.services import UserService


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

    def test_incorrect_password(self, mock_login):
        """Incorrect password."""
        mock_login.side_effect = AuthService.InvalidPasswordError()

        response = self.client.post(
            reverse('auth:login'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 406
        assert response.json() == {
            'detail': 'Invalid password was provided.',
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

    def test_refreshing_error(self, mock_refresh_token):
        """User with provided email not found."""
        mock_refresh_token.side_effect = AuthService.InvalidRefreshTokenError()

        response = self.client.post(
            reverse('auth:token_refresh'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 406
        assert response.json() == {
            'detail': 'Attempt to refresh token failed.',
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
