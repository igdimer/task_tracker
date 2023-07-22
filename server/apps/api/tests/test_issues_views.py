import copy
import datetime
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.issues.services import ProjectService, ReleaseService
from server.apps.users.services import UserService


@pytest.mark.django_db()
class TestIssueCreateApi:
    """Testing IssueCreateApi."""

    default_payload = {
        'project_id': 1,
        'title': 'test_title',
        'description': 'test_text',
        'estimated_time': '04:00:00',
        'assignee_id': 2,
        'release_id': 5,
    }

    @pytest.fixture()
    def mock_create(self):
        """Mock fixture method create of IssueService."""
        with mock.patch('server.apps.issues.services.IssueService.create') as mock_method:
            yield mock_method

    def test_success_response(self, authorized_client, mock_create, user):
        """Success response."""
        response = authorized_client.post(
            reverse('issues:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}
        mock_create.assert_called_with(
            project_id=1,
            release_id=5,
            title='test_title',
            description='test_text',
            assignee_id=2,
            author=user,
            estimated_time=datetime.timedelta(hours=4),
        )

    def test_no_estimated_time(self, mock_create, authorized_client, user):
        """Request without provided estimated_time."""
        payload = copy.copy(self.default_payload)
        payload.pop('estimated_time')

        response = authorized_client.post(
            reverse('issues:create'),
            payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}
        mock_create.assert_called_with(
            project_id=1,
            release_id=5,
            title='test_title',
            description='test_text',
            assignee_id=2,
            author=user,
            estimated_time=datetime.timedelta(seconds=0),
        )

    @pytest.mark.parametrize('exc_class', [
        ProjectService.ProjectNotFoundError,
        ReleaseService.ReleaseNotFoundError,
        UserService.UserNotFoundError,
    ])
    def test_not_found(self, mock_create, authorized_client, exc_class):
        """Project, release or user not found."""
        mock_create.side_effect = exc_class()
        response = authorized_client.post(
            reverse('issues:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('issues:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.get(
            reverse('issues:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "GET" not allowed.',
        }

    def test_incorrect_parameters(self, authorized_client):
        """Incorrect response parameters."""
        payload = {
            'wrong_key': 'value',
        }
        response = authorized_client.post(
            reverse('issues:create'),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'project_id': ['This field is required.'],
                'title': ['This field is required.'],
                'description': ['This field is required.'],
                'assignee_id': ['This field is required.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_create):
        """Internal server error."""
        mock_create.side_effect = Exception()
        response = authorized_client.post(
            reverse('issues:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }
