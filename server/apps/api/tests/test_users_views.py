from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.issues.tests.factories import IssueFactory
from server.apps.users.services import UserService


@pytest.mark.django_db()
class TestUserDetailApi:
    """Testing UserDetailApi."""

    @pytest.fixture()
    def mock_get_by_id(self):
        """Mock fixture for method get_by_id of UserService."""
        with mock.patch('server.apps.users.services.UserService.get_by_id') as get_mock:
            yield get_mock

    def test_success_response(self, user, authorized_client, mock_get_by_id):
        """Check success response."""
        mock_get_by_id.return_value = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'issues': [],
        }

        response = authorized_client.get(reverse('users:detail', args=[user.id]))

        assert response.status_code == 200
        assert response.json() == {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'issues': [],
        }

    def test_user_not_found(self, authorized_client, mock_get_by_id):
        """User not found."""
        mock_get_by_id.side_effect = UserService.UserNotFoundError()

        response = authorized_client.get(reverse('users:detail', args=[9999]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('users:detail', args=[9999]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('users:detail', args=[9999]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_by_id):
        """Internal server error."""
        mock_get_by_id.side_effect = Exception()
        response = authorized_client.get(reverse('users:detail', args=[9999]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestUserUpdateApi:
    """Testing UserUpdateApi."""

    default_payload = {
        'email': 'test@email.com',
        'first_name': 'Joe',
        'last_name': 'Black',
    }

    @pytest.fixture()
    def mock_update(self):
        """Mock fixture for method update of UserService."""
        with mock.patch('server.apps.users.services.UserService.update') as update_mock:
            yield update_mock

    def test_success(self, authorized_client, mock_update):
        """Success response."""
        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}

    def test_user_not_found(self, authorized_client, mock_update):
        """User is not found."""
        mock_update.side_effect = UserService.UserNotFoundError()

        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_unique_email_error(self, authorized_client, mock_update):
        """User with provided email already exists."""
        mock_update.side_effect = UserService.UserAlreadyExist()

        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 409
        assert response.json() == {
            'detail': 'User with provided email already exists.',
        }

    def test_restricted_attributes_provided(self, authorized_client, mock_update):
        """Check that fields password and is_admin are not passed to service."""
        payload = {
            'email': 'test@email.com',
            'first_name': 'Joe',
            'last_name': 'Black',
            'password': 'hack_password',
            'is_admin': True,
        }

        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}
        mock_update.assert_called_with(
            user_id=1,
            email='test@email.com',
            first_name='Joe',
            last_name='Black',
        )

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.patch(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_incorrect_parameters(self, authorized_client):
        """Incorrect response parameters."""
        payload = {
            'wrong_key': 'value',
        }
        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'non_field_errors': ['No necessary fields were passed.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_update):
        """Internal server error."""
        mock_update.side_effect = Exception()
        response = authorized_client.patch(
            reverse('users:update', args=[1]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestUserGetAssignedIssuesApi:
    """Testing UserGetAssignedIssuesApi."""

    @pytest.fixture()
    def mock_get_assigned_issues(self):
        """Mock fixture of method get_assigned_issues."""
        with mock.patch(
            'server.apps.users.services.UserService.get_assigned_issues',
        ) as issues_mock:
            yield issues_mock

    def test_success(self, user, authorized_client):
        """Success response."""
        issue = IssueFactory(assignee=user)
        response = authorized_client.get(reverse('users:my_issues'))

        assert response.status_code == 200
        assert response.json() == {
            'issues': [
                {
                    'code': issue.code,
                    'title': issue.title,
                    'status': issue.status,
                    'estimated_time': '04:00:00',
                    'release': issue.release.version,
                },
            ],
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('users:my_issues'))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('users:my_issues'))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_assigned_issues):
        """Internal server error."""
        mock_get_assigned_issues.side_effect = Exception()
        response = authorized_client.get(reverse('users:my_issues'))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }
