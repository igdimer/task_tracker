import datetime
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.issues.services import ProjectService, ReleaseService
from server.apps.issues.tests.factories import ProjectFactory, ReleaseFactory
from server.apps.users.tests.factories import UserFactory


@pytest.mark.django_db()
class TestProjectCreateApi:
    """Testing ProjectCreateApi."""

    default_payload = {
        'title': 'test_title',
        'code': 'test_code',
        'description': 'test_description',
    }

    @pytest.fixture()
    def mock_create(self):
        """Mock fixture method create of ProjectService."""
        with mock.patch('server.apps.issues.services.ProjectService.create') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_create, user):
        """Success response."""
        response = authorized_client.post(
            reverse('projects:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 201
        assert response.json() == {}
        mock_create.assert_called_with(
            title='test_title',
            code='test_code',
            description='test_description',
            owner=user,
        )

    def test_unique_fields_error(self, mock_create, authorized_client):
        """Project with provided fields already exists."""
        mock_create.side_effect = ProjectService.ProjectAlreadyExist()
        response = authorized_client.post(
            reverse('projects:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 409
        assert response.json() == {
            'detail': 'Project with some of provided fields already exists.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('projects:create'),
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
            reverse('projects:create'),
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
            reverse('projects:create'),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'code': ['This field is required.'],
                'description': ['This field is required.'],
                'title': ['This field is required.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_create):
        """Internal server error."""
        mock_create.side_effect = Exception()
        response = authorized_client.post(
            reverse('projects:create'),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestProjectUpdateApi:
    """Testing ProjectUpdateApi."""

    default_payload = {
        'title': 'test_title',
        'code': 'test_code',
        'description': 'test_description',
    }

    @pytest.fixture()
    def mock_update(self):
        """Mock fixture method update of ProjectService."""
        with mock.patch('server.apps.issues.services.ProjectService.update') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_update, mock_project_get_or_error, project):
        """Success response."""
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)

        assert response.status_code == 200
        assert response.json() == {}
        mock_update.assert_called_with(
            project=project,
            title='test_title',
            code='test_code',
            description='test_description',
        )

    def test_permission_denied(
        self,
        authorized_client,
        mock_update,
        mock_project_get_or_error,
    ):
        """Request from non-owner user."""
        project = ProjectFactory(
            title='New project',
            code='NP',
            owner=UserFactory(email='owner@mail.com'),
        )
        mock_project_get_or_error.return_value = project
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)

        assert response.status_code == 403
        assert response.json() == {
            'detail': 'You do not have permission to perform this action.',
        }
        mock_update.assert_not_called()

    def test_admin_access(self, admin_client, mock_update, mock_project_get_or_error):
        """Request from admin user."""
        project = ProjectFactory(
            title='New project',
            code='NP',
            owner=UserFactory(email='owner@mail.com'),
        )
        mock_project_get_or_error.return_value = project

        response = admin_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 200
        assert response.json() == {}

    def test_project_not_found(self, mock_update, authorized_client):
        """Project not found."""
        mock_update.side_effect = ProjectService.ProjectNotFoundError()
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_project_already_exist(
        self,
        mock_update,
        authorized_client,
        mock_project_get_or_error,
    ):
        """Project with provided fields already exists."""
        mock_update.side_effect = ProjectService.ProjectAlreadyExist()
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 409
        assert response.json() == {
            'detail': 'Project with some of provided fields already exists.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('projects:update', args=[999]),
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
            reverse('projects:update', args=[999]),
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
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'non_field_errors': ['No necessary fields were passed.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_project_get_or_error):
        """Internal server error."""
        mock_project_get_or_error.side_effect = Exception()
        response = authorized_client.patch(
            reverse('projects:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestProjectDetailApi:
    """Testing ProjectDetailApi."""

    @pytest.fixture()
    def mock_get_project_info(self):
        """Mock fixture method get_by_id of ProjectService."""
        with mock.patch(
            'server.apps.issues.services.ProjectService.get_project_info',
        ) as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_project_info):
        """Success response."""
        mock_get_project_info.return_value = {
            'title': 'project_title',
            'code': 'project_code',
            'description': 'project_description',
            'owner_id': 1,
            'issues': [],
        }
        response = authorized_client.get(reverse('projects:detail', args=[999]))

        assert response.status_code == 200
        assert response.json() == {
            'title': 'project_title',
            'code': 'project_code',
            'description': 'project_description',
            'owner_id': 1,
            'issues': [],
        }

    def test_project_not_found(self, authorized_client, mock_get_project_info):
        """Project does not exist."""
        mock_get_project_info.side_effect = ProjectService.ProjectNotFoundError()
        response = authorized_client.get(reverse('projects:detail', args=[999]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('projects:detail', args=[999]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('projects:detail', args=[999]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_project_info):
        """Internal server error."""
        mock_get_project_info.side_effect = Exception()
        response = authorized_client.get(reverse('projects:detail', args=[999]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestReleaseCreateApi:
    """Testing ReleaseCreateApi."""

    default_payload = {
        'version': '0.1.0',
        'release_date': '2024-01-10',
        'description': 'New_Release',
    }

    @pytest.fixture()
    def mock_create(self):
        """Mock fixture method create of ReleaseService."""
        with mock.patch('server.apps.issues.services.ReleaseService.create') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_create, mock_project_get_or_error, project):
        """Success response."""
        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 201
        assert response.json() == {}
        mock_create.assert_called_with(
            project=project,
            version='0.1.0',
            release_date=datetime.date(2024, 1, 10),
            description='New_Release',
        )

    def test_create_no_release_date(
        self,
        authorized_client,
        mock_create,
        mock_project_get_or_error,
        project,
    ):
        """Create with no provided release date."""
        payload = {
            'version': '0.1.0',
            'description': 'New_Release',
        }

        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 201
        assert response.json() == {}
        mock_create.assert_called_with(
            project=project,
            version='0.1.0',
            description='New_Release',
        )

    def test_project_not_found(self, authorized_client, mock_project_get_or_error):
        """Project was not found."""
        mock_project_get_or_error.side_effect = ProjectService.ProjectNotFoundError()
        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_release_already_exists(
        self,
        authorized_client,
        mock_create,
        mock_project_get_or_error,
    ):
        """Project has release with the same version."""
        mock_create.side_effect = ReleaseService.ReleaseAlreadyExist()
        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 409
        assert response.json() == {
            'detail': 'Project already has release with the same version.',
        }

    def test_permission_denied(
        self,
        authorized_client,
        mock_create,
        mock_project_get_or_error,
    ):
        """Request from non-owner of project user."""
        project = ProjectFactory(
            title='New project',
            code='NP',
            owner=UserFactory(email='owner@mail.com'),
        )
        mock_project_get_or_error.return_value = project
        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 403
        assert response.json() == {
            'detail': 'You do not have permission to perform this action.',
        }
        mock_create.assert_not_called()

    def test_admin_access(
        self,
        admin_client,
        mock_create,
        mock_project_get_or_error,
    ):
        """Request from admin user."""
        project = ProjectFactory(
            title='New project',
            code='NP',
            owner=UserFactory(email='owner@mail.com'),
        )
        mock_project_get_or_error.return_value = project
        response = admin_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        mock_project_get_or_error.assert_called_with(project_id=999)
        assert response.status_code == 201
        assert response.json() == {}
        mock_create.assert_called_with(
            project=project,
            version='0.1.0',
            release_date=datetime.date(2024, 1, 10),
            description='New_Release',
        )

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('projects:release_create', args=[999]),
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
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "GET" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_create, mock_project_get_or_error):
        """Internal server error."""
        mock_create.side_effect = Exception()
        response = authorized_client.post(
            reverse('projects:release_create', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestReleaseDetailApi:
    """Testing ReleaseDetailApi."""

    @pytest.fixture()
    def mock_get_by_id(self):
        """Mock fixture method get_by_id of ReleaseService."""
        with mock.patch('server.apps.issues.services.ReleaseService.get_by_id') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_by_id):
        """Success response."""
        mock_get_by_id.return_value = ReleaseFactory(version='0.1.0')
        response = authorized_client.get(reverse('projects:release_detail', args=[999, 888]))

        assert response.status_code == 200
        assert response.json() == {
            'version': '0.1.0',
            'description': 'New Release',
            'release_date': '2024-01-01',
            'status': 'unreleased',
        }
        mock_get_by_id.assert_called_with(release_id=888, project_id=999)

    def test_release_not_found(self, authorized_client, mock_get_by_id):
        """Release does not exist."""
        mock_get_by_id.side_effect = ReleaseService.ReleaseNotFoundError()
        response = authorized_client.get(reverse('projects:release_detail', args=[999, 888]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('projects:release_detail', args=[999, 888]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('projects:release_detail', args=[999, 888]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_by_id):
        """Internal server error."""
        mock_get_by_id.side_effect = Exception()
        response = authorized_client.get(reverse('projects:release_detail', args=[999, 888]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestReleaseUpdateApi:
    """Testing ReleaseUpdateApi."""

    default_payload = {
        'version': '0.1.0',
        'release_date': '2024-01-10',
        'description': 'New_Release',
        'status': 'released',
    }

    @pytest.fixture()
    def mock_release_get_or_error(self, release):
        """Mock fixture method get_or_error of ReleaseService."""
        with mock.patch(
            'server.apps.issues.services.ReleaseService.get_or_error',
            return_value=release,
        ) as mock_method:
            yield mock_method

    @pytest.fixture()
    def mock_update(self):
        """Mock fixture method update of ReleaseService."""
        with mock.patch('server.apps.issues.services.ReleaseService.update') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_update, mock_release_get_or_error, release):
        """Success response."""
        response = authorized_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        mock_release_get_or_error.assert_called_with(
            release_id=888,
            project_id=999,
            join_project=True,
        )
        assert response.status_code == 200
        assert response.json() == {}
        mock_update.assert_called_with(
            release=release,
            version='0.1.0',
            release_date=datetime.date(2024, 1, 10),
            description='New_Release',
            status='released',
        )

    def test_release_already_exists(
        self,
        mock_update,
        authorized_client,
        mock_release_get_or_error,
    ):
        """Project has release with the same version."""
        mock_update.side_effect = ReleaseService.ReleaseAlreadyExist()
        response = authorized_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        mock_release_get_or_error.assert_called_with(
            release_id=888,
            project_id=999,
            join_project=True,
        )
        assert response.status_code == 409
        assert response.json() == {
            'detail': 'Project already has release with the same version.',
        }

    def test_release_not_found(self, authorized_client, mock_release_get_or_error):
        """Release not found."""
        mock_release_get_or_error.side_effect = ReleaseService.ReleaseNotFoundError()
        response = authorized_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_permission_denied(self, mock_update, mock_release_get_or_error):
        """Request from non-owner of project."""
        non_owner = UserFactory(email='no_owner@email.com')
        client = APIClient()
        client.force_authenticate(non_owner)
        response = client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        mock_release_get_or_error.assert_called_with(
            release_id=888,
            project_id=999,
            join_project=True,
        )
        assert response.status_code == 403
        assert response.json() == {
            'detail': 'You do not have permission to perform this action.',
        }
        mock_update.assert_not_called()

    def test_admin_access(self, admin_client, mock_update, mock_release_get_or_error):
        """Request from non-owner of project."""
        project = ProjectFactory(
            title='New project',
            code='NP',
            owner=UserFactory(email='owner@mail.com'),
        )
        release = ReleaseFactory(project=project)
        mock_release_get_or_error.return_value = release
        response = admin_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        mock_release_get_or_error.assert_called_with(
            release_id=888,
            project_id=999,
            join_project=True,
        )
        assert response.status_code == 200
        assert response.json() == {}
        mock_update.assert_called_with(
            release=release,
            version='0.1.0',
            release_date=datetime.date(2024, 1, 10),
            description='New_Release',
            status='released',
        )

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('projects:release_update', args=[999, 888]),
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
            reverse('projects:release_update', args=[999, 888]),
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
        response = authorized_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'non_field_errors': ['No necessary fields were passed.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_update, mock_release_get_or_error):
        """Internal server error."""
        mock_update.side_effect = Exception()
        response = authorized_client.patch(
            reverse('projects:release_update', args=[999, 888]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }
