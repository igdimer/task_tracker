import datetime

import pytest

from server.apps.issues.models import Issue
from server.apps.issues.services import IssueService, ProjectService, ReleaseService
from server.apps.users.services import UserService


@pytest.mark.django_db()
class TestIssueServiceCreate:
    """Testing method create of IssueService."""

    def test_success(self, project, release, user, author):
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

    def test_release_none(self, author, user, project, release):
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
