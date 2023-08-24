import pytest
from pytest_django.asserts import assertQuerySetEqual

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
        result = UserService.get_user_info(user_id=user.id)

        assert result['email'] == user.email
        assert result['first_name'] == user.first_name
        assert result['last_name'] == user.last_name
        assertQuerySetEqual(result['issues'], [])

    def test_get_by_id_no_user(self, user):
        """Check get_by_id method in case no required user."""
        with pytest.raises(UserService.UserNotFoundError):
            UserService.get_user_info(user_id=9999)

    def test_get_by_id_with_issues(self, user):
        """Check get_by_id method in case user exists and has issues."""
        author = UserFactory(email='author@mail.com')
        issue_1 = IssueFactory(assignee=user, author=author)
        issue_2 = IssueFactory(assignee=user, author=author, release=None, project=issue_1.project)
        result = UserService.get_user_info(user_id=user.id)

        assert result['email'] == user.email
        assert result['first_name'] == user.first_name
        assert result['last_name'] == user.last_name
        assertQuerySetEqual(result['issues'], [issue_1, issue_2], ordered=False)


@pytest.mark.django_db()
class TestUserServiceUpdate:
    """Testing method update of UserService."""

    def test_success(self, user):
        """Success updating."""
        UserService.update(
            user=user,
            email='new@mail.com',
            first_name='NewName',
            last_name='NewLastName',
        )
        user.refresh_from_db()

        assert user.email == 'new@mail.com'
        assert user.first_name == 'NewName'
        assert user.last_name == 'NewLastName'

    def test_existing_email_error(self, user):
        """User with updated email already exists."""
        UserFactory(email='unique@mail.com')

        with pytest.raises(UserService.UserAlreadyExistError):
            UserService.update(user, email='unique@mail.com')


@pytest.mark.django_db()
class TestUserServiceGetAssignedIssues:
    """Testing method get_assigned_issues of UserService."""

    def test_user_has_issues(self, user, author):
        """User has issues."""
        issue_1 = IssueFactory(assignee=user, author=author)
        issue_2 = IssueFactory(assignee=user, author=author)

        result = UserService.get_assigned_issues(user)

        assertQuerySetEqual(result['issues'], [issue_1, issue_2], ordered=False)

    def test_user_has_no_issues(self, user):
        """User has no assigned issues."""
        result = UserService.get_assigned_issues(user)
        assertQuerySetEqual(result['issues'], [])

    def test_another_user_has_issues(self, user, author):
        """Two users have assigned issues."""
        another_user = UserFactory(email='another@mail.com')
        issue_1 = IssueFactory(assignee=user, author=author)
        IssueFactory(assignee=another_user, author=author)

        result = UserService.get_assigned_issues(user)

        assertQuerySetEqual(result['issues'], [issue_1], ordered=False)
