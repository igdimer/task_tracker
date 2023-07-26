import copy
import datetime
from unittest import mock

import pytest
from django.urls import reverse
from rest_framework.test import APIClient

from server.apps.issues.models import Comment
from server.apps.issues.services import (CommentService, IssueService, ProjectService,
                                         ReleaseService)
from server.apps.issues.tests.factories import CommentFactory, IssueFactory
from server.apps.users.services import UserService
from server.apps.users.tests.factories import UserFactory


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


@pytest.mark.django_db()
class TestIssueDetailApi:
    """Testing IssueDetailApi."""

    @pytest.fixture()
    def mock_get_by_id(self):
        """Mock fixture method get_by_id of IssueService."""
        with mock.patch('server.apps.issues.services.IssueService.get_by_id') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_by_id):
        """Success response."""
        mock_get_by_id.return_value = {
            'title': 'issue_title',
            'code': 'issue_code',
            'description': 'issue_description',
            'estimated_time': datetime.timedelta(hours=3),
            'logged_time': datetime.timedelta(hours=1),
            'remaining_time': datetime.timedelta(hours=2),
            'author': 1,
            'assignee': 2,
            'project': 'issue_project_code',
            'status': 'open',
            'release': 'version',
        }
        response = authorized_client.get(reverse('issues:detail', args=[999]))

        assert response.status_code == 200
        assert response.json() == {
            'title': 'issue_title',
            'code': 'issue_code',
            'description': 'issue_description',
            'estimated_time': '03:00:00',
            'logged_time': '01:00:00',
            'remaining_time': '02:00:00',
            'author': 1,
            'assignee': 2,
            'project': 'issue_project_code',
            'status': 'open',
            'release': 'version',
        }

    def test_issue_not_found(self, authorized_client, mock_get_by_id):
        """Issue does not exist."""
        mock_get_by_id.side_effect = IssueService.IssueNotFoundError()
        response = authorized_client.get(reverse('issues:detail', args=[999]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('issues:detail', args=[999]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('issues:detail', args=[999]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_by_id):
        """Internal server error."""
        mock_get_by_id.side_effect = Exception()
        response = authorized_client.get(reverse('issues:detail', args=[999]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestIssueListApi:
    """Testing IssueListApi."""

    @pytest.fixture()
    def mock_get_list(self):
        """Mock fixture method get_by_id of IssueListApi."""
        with mock.patch('server.apps.issues.services.IssueService.get_list') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_list):
        """Success response."""
        mock_get_list.return_value = [{
            'title': 'issue_title',
            'code': 'issue_code',
            'description': 'issue_description',
            'estimated_time': datetime.timedelta(hours=3),
            'logged_time': datetime.timedelta(hours=1),
            'remaining_time': datetime.timedelta(hours=2),
            'author': 1,
            'assignee': 2,
            'project': 'issue_project_code',
            'status': 'open',
            'release': 'version',
        }]
        response = authorized_client.get(reverse('issues:list'))

        assert response.status_code == 200
        assert response.json() == [{
            'title': 'issue_title',
            'code': 'issue_code',
            'description': 'issue_description',
            'estimated_time': '03:00:00',
            'logged_time': '01:00:00',
            'remaining_time': '02:00:00',
            'author': 1,
            'assignee': 2,
            'project': 'issue_project_code',
            'status': 'open',
            'release': 'version',
        }]

    def test_empty_issues_list(self, authorized_client, mock_get_list):
        """Issue does not exist."""
        mock_get_list.return_value = []
        response = authorized_client.get(reverse('issues:list'))

        assert response.status_code == 200
        assert response.json() == []

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('issues:list'))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('issues:list'))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_list):
        """Internal server error."""
        mock_get_list.side_effect = Exception()
        response = authorized_client.get(reverse('issues:list'))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestIssueUpdateApi:
    """Testing IssueUpdateApi."""

    default_payload = {
        'title': 'test_title',
        'description': 'test_description',
        'estimated_time': '02:00:00',
        'logged_time': '00:30:00',
        'status': 'resolved',
        'assignee_id': 2,
        'release_id': 5,

    }

    @pytest.fixture()
    def mock_update(self):
        """Mock fixture method update of IssueService."""
        with mock.patch('server.apps.issues.services.IssueService.update') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_update):
        """Success response."""
        response = authorized_client.patch(
            reverse('issues:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}
        mock_update.assert_called_with(
            issue_id=999,
            title='test_title',
            description='test_description',
            release_id=5,
            assignee_id=2,
            estimated_time=datetime.timedelta(hours=2),
            logged_time=datetime.timedelta(minutes=30),
            status='resolved',
        )

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.post(
            reverse('issues:update', args=[999]),
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
            reverse('issues:update', args=[999]),
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
            reverse('issues:update', args=[999]),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'non_field_errors': ['No necessary fields were passed.'],
            },
        }

    @pytest.mark.parametrize('exc_class', [
        IssueService.IssueNotFoundError,
        UserService.UserNotFoundError,
        ReleaseService.ReleaseNotFoundError,
    ])
    def test_not_found(self, authorized_client, mock_update, exc_class):
        """Issue, user or release not found."""
        mock_update.side_effect = exc_class()
        response = authorized_client.patch(
            reverse('issues:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_provided_null_release_id(self, authorized_client, mock_update):
        """Provided release_id is null."""
        payload = {'release_id': None}
        response = authorized_client.patch(
            reverse('issues:update', args=[999]),
            payload,
            format='json',
        )

        assert response.status_code == 200
        mock_update.assert_called_with(issue_id=999, release_id=None)

    def test_internal_error(self, authorized_client, mock_update):
        """Internal server error."""
        mock_update.side_effect = Exception()
        response = authorized_client.patch(
            reverse('issues:update', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestCommentCreateApi:
    """Testing CommentCreateApi."""

    default_payload = {
        'text': 'test_comment_text',
    }

    @pytest.fixture()
    def mock_create(self):
        """Mock fixture of method create of CommentService."""
        with mock.patch('server.apps.issues.services.CommentService.create') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_create, user):
        """Success response."""
        response = authorized_client.post(
            reverse('issues:comments_create', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 200
        assert response.json() == {}
        mock_create.assert_called_with(
            issue_id=999,
            author=user,
            text='test_comment_text',
        )

    def test_issue_not_found(self, authorized_client, mock_create):
        """Issue not found."""
        mock_create.side_effect = IssueService.IssueNotFoundError()
        response = authorized_client.post(
            reverse('issues:comments_create', args=[999]),
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
            reverse('issues:comments_create', args=[999]),
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
            reverse('issues:comments_create', args=[999]),
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
            reverse('issues:comments_create', args=[999]),
            payload,
            format='json',
        )

        assert response.status_code == 400
        assert response.json() == {
            'detail': {
                'text': ['This field is required.'],
            },
        }

    def test_internal_error(self, authorized_client, mock_create):
        """Internal server error."""
        mock_create.side_effect = Exception()
        response = authorized_client.post(
            reverse('issues:comments_create', args=[999]),
            self.default_payload,
            format='json',
        )

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestCommentDetailApi:
    """Testing CommentDetailApi."""

    @pytest.fixture()
    def mock_get_by_id(self):
        """Mock fixture method get_by_id of CommentService."""
        with mock.patch('server.apps.issues.services.CommentService.get_by_id') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_by_id):
        """Success response."""
        comment = CommentFactory(author=UserFactory(email='author@mail.com'))
        mock_get_by_id.return_value = comment

        response = authorized_client.get(reverse('issues:comments_detail', args=[99, comment.id]))

        assert response.status_code == 200
        assert response.json() == {
            'text': comment.text,
            'author_id': comment.author_id,
            'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M'),
        }

    @pytest.mark.parametrize('exc_class', [
        IssueService.IssueNotFoundError,
        CommentService.CommentNotFoundError,
    ])
    def test_not_found(self, authorized_client, exc_class, mock_get_by_id):
        """Issue or comment not found."""
        mock_get_by_id.side_effect = exc_class()
        response = authorized_client.get(reverse('issues:comments_detail', args=[99, 55]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('issues:comments_detail', args=[99, 55]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('issues:comments_detail', args=[99, 55]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_by_id):
        """Internal server error."""
        mock_get_by_id.side_effect = Exception()
        response = authorized_client.get(reverse('issues:comments_detail', args=[99, 55]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }


@pytest.mark.django_db()
class TestCommentListApi:
    """Testing CommentListApi."""

    @pytest.fixture()
    def mock_get_list(self):
        """Mock fixture method get_by_id of CommentService."""
        with mock.patch('server.apps.issues.services.CommentService.get_list') as mock_method:
            yield mock_method

    def test_success(self, authorized_client, mock_get_list):
        """Success response."""
        issue = IssueFactory()
        comment_1 = CommentFactory(issue=issue, author=issue.assignee)
        comment_2 = CommentFactory(issue=issue, author=issue.assignee)
        qs = Comment.objects.all()
        mock_get_list.return_value = qs

        response = authorized_client.get(reverse('issues:comments_list', args=[999]))

        assert response.status_code == 200
        assert response.json() == [
            {
                'text': comment_1.text,
                'author_id': comment_1.author_id,
                'created_at': comment_1.created_at.strftime('%Y-%m-%d %H:%M'),
            },
            {
                'text': comment_2.text,
                'author_id': comment_2.author_id,
                'created_at': comment_2.created_at.strftime('%Y-%m-%d %H:%M'),
            },
        ]

    def test_issue_not_found(self, authorized_client, mock_get_list):
        """Issue not found."""
        mock_get_list.side_effect = IssueService.IssueNotFoundError()
        response = authorized_client.get(reverse('issues:comments_list', args=[999]))

        assert response.status_code == 404
        assert response.json() == {
            'detail': 'Not found.',
        }

    def test_auth_fail(self):
        """Non authenticated response."""
        client = APIClient()
        response = client.get(reverse('issues:comments_list', args=[999]))

        assert response.status_code == 401
        assert response.json() == {
            'detail': 'Incorrect authentication credentials.',
        }

    def test_method_not_allowed(self, authorized_client):
        """Incorrect HTTP method."""
        response = authorized_client.post(reverse('issues:comments_list', args=[999]))

        assert response.status_code == 405
        assert response.json() == {
            'detail': 'Method "POST" not allowed.',
        }

    def test_internal_error(self, authorized_client, mock_get_list):
        """Internal server error."""
        mock_get_list.side_effect = Exception()
        response = authorized_client.get(reverse('issues:comments_list', args=[999]))

        assert response.status_code == 500
        assert response.json() == {
            'detail': 'Internal Server Error',
        }
