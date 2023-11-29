import datetime

import pytest
from pytest_django.asserts import assertQuerySetEqual

from server.apps.issues.enums import IssueStatusEnum
from server.apps.issues.models import Issue
from server.apps.issues.services import IssueService, ProjectService, ReleaseService
from server.apps.users.services import UserService
from server.apps.users.tests.factories import UserFactory

from ..factories import IssueFactory, ReleaseFactory


@pytest.mark.django_db()
class TestIssueServiceCreate:
    """Testing method create of IssueService."""

    def test_success(self, project, release, user, author, mock_notification_task):
        """Success creation issue."""
        assert Issue.objects.all().count() == 0

        IssueService.create(
            project_id=project.id,
            release_id=release.id,
            title='test_title',
            description='test_text',
            assignee_id=user.id,
            author=author,
            estimated_time=datetime.timedelta(hours=4),
        )

        issue = Issue.objects.get(title='test_title')

        assert Issue.objects.all().count() == 1
        assert issue.description == 'test_text'
        assert issue.project == project
        assert issue.release == release
        assert issue.author == author
        assert issue.assignee == user
        assert issue.estimated_time == datetime.timedelta(hours=4)
        assert issue.code == 'TT-1'

        mock_notification_task.assert_called_with(
            emails=[user.email],
            subject='New issue',
            message=f'Issue {issue.code} {issue.title} created',
        )

    def test_release_none(self, author, user, project, release, mock_notification_task):
        """Creation without release."""
        assert Issue.objects.all().count() == 0
        IssueService.create(
            project_id=project.id,
            title='test_title',
            description='test_text',
            assignee_id=user.id,
            author=author,
            estimated_time=datetime.timedelta(hours=4),
        )
        issue = Issue.objects.get(title='test_title')

        assert Issue.objects.all().count() == 1
        assert issue.description == 'test_text'
        assert issue.project == project
        assert issue.release is None
        assert issue.author == author
        assert issue.assignee == user
        assert issue.estimated_time == datetime.timedelta(hours=4)
        assert issue.code == 'TT-1'

    def test_not_notify_if_author_is_assignee(
        self,
        project,
        release,
        author,
        mock_notification_task,
    ):
        """Author assigned issue to himself."""
        IssueService.create(
            project_id=project.id,
            release_id=release.id,
            title='test_title',
            description='test_text',
            assignee_id=author.id,
            author=author,
            estimated_time=datetime.timedelta(hours=4),
        )

        mock_notification_task.assert_not_called()

    def test_release_not_found(self, user, author, project):
        """Provided release_id does not exist."""
        assert Issue.objects.all().count() == 0
        with pytest.raises(ReleaseService.ReleaseNotFoundError):
            IssueService.create(
                project_id=project.id,
                release_id=999,
                title='test_title',
                description='test_text',
                assignee_id=user.id,
                author=author,
                estimated_time=datetime.timedelta(hours=4),
            )
        assert Issue.objects.all().count() == 0

    def test_project_not_found(self, user, author):
        """Provided project_id does not exist."""
        assert Issue.objects.all().count() == 0
        with pytest.raises(ProjectService.ProjectNotFoundError):
            IssueService.create(
                project_id=999,
                title='test_title',
                description='test_text',
                assignee_id=user.id,
                author=author,
                estimated_time=datetime.timedelta(hours=4),
            )
        assert Issue.objects.all().count() == 0

    def test_assignee_not_found(self, author, project, release):
        """Assignee not found."""
        assert Issue.objects.all().count() == 0
        with pytest.raises(UserService.UserNotFoundError):
            IssueService.create(
                project_id=project.id,
                release_id=release.id,
                title='test_title',
                description='test_text',
                assignee_id=999,
                author=author,
                estimated_time=datetime.timedelta(hours=4),
            )
        assert Issue.objects.all().count() == 0


@pytest.mark.django_db()
class TestIssueServiceGetById:
    """Testing method get_by_id of IssueService."""

    def test_success_no_release(self, issue):
        """Getting issue without release."""
        result = IssueService.get_by_id(issue.id)
        assert result == issue

    def test_no_issue(self):
        """Issue does not exist."""
        with pytest.raises(IssueService.IssueNotFoundError):
            IssueService.get_by_id(999)


@pytest.mark.django_db()
class TestIssueServiceGetList:
    """Testing method get_list of IssueService."""

    def test_success(self, author):
        """Getting issues."""
        user_1 = UserFactory(email='one@mail.com')
        user_2 = UserFactory(email='two@mail.com')
        release_1, release_2 = ReleaseFactory(), ReleaseFactory()
        issue_1 = IssueFactory(
            title='title_1',
            assignee=user_1,
            author=author,
            project=release_1.project,
            release=release_1,
            description='test_text_1',
            estimated_time=datetime.timedelta(hours=1),
        )
        issue_2 = IssueFactory(
            title='title_2',
            assignee=user_2,
            author=author,
            project=release_2.project,
            release=release_2,
            description='test_text_2',
            estimated_time=datetime.timedelta(hours=2),
        )

        result = IssueService.get_list()
        assertQuerySetEqual(result, [issue_1, issue_2], ordered=False)

    def test_no_issues(self):
        """Empty list of issues."""
        result = IssueService.get_list()
        assertQuerySetEqual(result, [])


@pytest.mark.django_db()
class TestIssueServiceUpdate:
    """Testing method update of IssueService."""

    @pytest.fixture()
    def new_user(self):
        """Fixture of new user."""
        return UserFactory(email='new@mail.com')

    @pytest.fixture()
    def new_release(self, issue):
        """Fixture of new release."""
        return ReleaseFactory(project=issue.project)

    def test_success(self, issue, user, new_user, new_release, mock_notification_task):
        """Success updating."""
        IssueService.update(
            user=issue.author,
            issue=issue,
            title='new_title',
            description='new_description',
            estimated_time=datetime.timedelta(hours=3),
            logged_time=datetime.timedelta(hours=1),
            status=IssueStatusEnum.RESOLVED,
            assignee_id=new_user.id,
            release_id=new_release.id,
        )
        issue.refresh_from_db()

        assert issue.title == 'new_title'
        assert issue.description == 'new_description'
        assert issue.estimated_time == datetime.timedelta(hours=3)
        assert issue.logged_time == datetime.timedelta(hours=1)
        assert issue.status == IssueStatusEnum.RESOLVED
        assert issue.assignee == new_user
        assert issue.release == new_release

        kwargs = mock_notification_task.call_args.kwargs
        emails = kwargs['emails']

        assert kwargs['subject'] == f'Issue {issue.code}'
        assert len(emails) == 2
        assert user.email in emails
        assert new_user.email in emails
        assert kwargs['message'] == (
            f'Issue {issue.code} updated:\ntitle: {issue.title}\n'
            f'description: {issue.description}\nestimated_time: {issue.estimated_time}\n'
            f'logged_time: {issue.logged_time}\nstatus: {issue.status}\n'
            f'assignee_id: {issue.assignee_id}\nrelease_id: {issue.release_id}\n'
        )

    def test_no_release(self, issue, new_user):
        """Updating with non-existing release."""
        with pytest.raises(ReleaseService.ReleaseNotFoundError):
            IssueService.update(
                user=issue.author,
                issue=issue,
                title='new_title',
                description='new_description',
                estimated_time=datetime.timedelta(hours=3),
                logged_time=datetime.timedelta(hours=1),
                status=IssueStatusEnum.RESOLVED,
                assignee_id=new_user.id,
                release_id=999,
            )

    def test_no_new_user(self, issue, new_release):
        """Updating with non-existing user."""
        with pytest.raises(UserService.UserNotFoundError):
            IssueService.update(
                user=issue.author,
                issue=issue,
                title='new_title',
                description='new_description',
                estimated_time=datetime.timedelta(hours=3),
                logged_time=datetime.timedelta(hours=1),
                status=IssueStatusEnum.RESOLVED,
                assignee_id=999,
                release_id=new_release.id,
            )

    def test_remove_release(self):
        """Check removing release from issue."""
        issue = IssueFactory()
        assert issue.release

        IssueService.update(user=issue.author, issue=issue, release_id=None)
        issue.refresh_from_db()

        assert issue.release is None

    def test_adding_logged_time(self, user):
        """Adding logged time to existing value."""
        issue = IssueFactory(logged_time=datetime.timedelta(hours=3))
        IssueService.update(
            user=user,
            issue=issue,
            logged_time=datetime.timedelta(minutes=30),
        )
        issue.refresh_from_db()

        assert issue.logged_time == datetime.timedelta(hours=3, minutes=30)

    def test_notification_updating_user_is_author(
        self,
        issue,
        author,
        user,
        mock_notification_task,
    ):
        """Author updates the issue."""
        IssueService.update(
            issue=issue,
            user=author,
            release_id=None,
        )

        mock_notification_task.assert_called_with(
            emails=[user.email],
            subject=f'Issue {issue.code}',
            message=f'Issue {issue.code} updated:\nrelease_id: None\n',
        )

    def test_notification_updating_user_is_author_and_assignee(
        self,
        author,
        mock_notification_task,
    ):
        """Author is assignee and updates the issue (empty recipients list)."""
        issue = IssueFactory(author=author, assignee=author)
        IssueService.update(
            issue=issue,
            user=author,
            release_id=None,
        )

        mock_notification_task.assert_not_called()
