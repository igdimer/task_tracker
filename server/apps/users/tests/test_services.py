import pytest

from server.apps.issues.tests.factories import IssueFactory

from ..services import UserService
from .factories import UserFactory


@pytest.mark.django_db()
class TestUserServiceGetMethods:
    """Testing methods get_by_email and get_by_id of UserService."""

    def test_get_by_email_success(self, user):
        """Check get_by_email method in case user exists."""
        user = UserService.get_by_email(email='test@email.com')

        assert user
        assert user.email == 'test@email.com'
        assert user.first_name == 'Ozzy'
        assert user.last_name == 'Osbourne'

    def test_get_by_email_no_user(self, user):
        """Check get_by_email method in case no required user."""
        with pytest.raises(UserService.UserNotFoundError):
            UserService.get_by_email(email='nouser@email.com')

    def test_get_by_id(self, user):
        """Check get_by_id method in case user exists."""
        result = UserService.get_by_id(user_id=user.id)

        assert result == {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'issues': [],
        }

    def test_get_by_id_no_user(self, user):
        """Check get_by_id method in case no required user."""
        with pytest.raises(UserService.UserNotFoundError):
            UserService.get_by_id(user_id=9999)

    def test_get_by_id_with_issues(self, user):
        """Check get_by_id method in case user exists and has issues."""
        author = UserFactory(email='author@mail.com')
        issue_1 = IssueFactory(assignee=user, author=author)
        issue_2 = IssueFactory(assignee=user, author=author)
        result = UserService.get_by_id(user_id=user.id)

        assert result == {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_admin': user.is_admin,
            'issues': [
                {
                    'title': issue_1.title,
                    'code': issue_1.code,
                    'status': issue_1.status,
                    'release': issue_1.release.version,
                },
                {
                    'title': issue_2.title,
                    'code': issue_2.code,
                    'status': issue_2.status,
                    'release': issue_2.release.version,
                },
            ],
        }


@pytest.mark.django_db()
class TestUserServiceUpdate:
    """Testing method update of UserService."""

    def test_success(self, user):
        """Success updating."""
        UserService.update(
            user.id,
            email='new@mail.com',
            first_name='NewName',
            last_name='NewLastName',
        )
        user.refresh_from_db()

        assert user.email == 'new@mail.com'
        assert user.first_name == 'NewName'
        assert user.last_name == 'NewLastName'

    def test_existing_email_fail(self, user):
        """User with updated email already exists."""
        UserFactory(email='unique@mail.com')

        with pytest.raises(UserService.UniqueEmailError):
            UserService.update(user.id, email='unique@mail.com')


@pytest.mark.django_db()
class TestUserServiceGetAssignedIssues:
    """Testing method get_assigned_issues of UserService."""

    def test_user_has_issues(self, user, author):
        """User has issues."""
        issue_1 = IssueFactory(assignee=user, author=author)
        issue_2 = IssueFactory(assignee=user, author=author)

        result = UserService.get_assigned_issues(user)

        assert result == {
            'issues': [
                {
                    'title': issue_1.title,
                    'code': issue_1.code,
                    'status': issue_1.status,
                    'estimated_time': issue_1.estimated_time,
                    'release': issue_1.release.version,
                },
                {
                    'title': issue_2.title,
                    'code': issue_2.code,
                    'status': issue_2.status,
                    'estimated_time': issue_2.estimated_time,
                    'release': issue_2.release.version,
                },
            ],
        }

    def test_user_has_no_issues(self, user):
        """User has no assigned issues."""
        assert UserService.get_assigned_issues(user) == {'issues': []}

    def test_another_user_has_issues(self, user, author):
        """Two users have assigned issues."""
        another_user = UserFactory(email='another@mail.com')
        issue_1 = IssueFactory(assignee=user, author=author)
        IssueFactory(assignee=another_user, author=author)

        result = UserService.get_assigned_issues(user)

        assert result == {
            'issues': [
                {
                    'title': issue_1.title,
                    'code': issue_1.code,
                    'status': issue_1.status,
                    'estimated_time': issue_1.estimated_time,
                    'release': issue_1.release.version,
                },
            ],
        }
