import datetime

import pytest

from ..enums import IssueStatusEnum
from .factories import IssueFactory


@pytest.mark.django_db()
class TestIssueModel:
    """Testing methods of model Issue."""

    def test_save(self, project, release):
        """Check save method with setting 'code'."""
        issue = IssueFactory(project=project, release=release)

        assert issue.title == 'test_issue'
        assert issue.description == 'easy_issue'
        assert issue.estimated_time == datetime.timedelta(hours=4)
        assert issue.status == IssueStatusEnum.OPEN
        assert issue.author.email == 'author@email.com'
        assert issue.assignee.email == 'assignee@email.com'
        assert issue.project.title == 'test_project'
        assert issue.release.version == '0.1.0'
        assert issue.logged_time == datetime.timedelta(seconds=0)
        assert issue.code == 'TT-1'

    def test_next_issue(self, project, user, author, release):
        """Create the second issue."""
        issue_1 = IssueFactory(project=project, release=release, author=author, assignee=user)
        assert issue_1.code == 'TT-1'

        issue_2 = IssueFactory(project=project, release=release, author=author, assignee=user)
        assert issue_2.code == 'TT-2'

    def test_updating_not_last_issue(self, project, release, user, author):
        """Update not last issue."""
        issue_1 = IssueFactory(project=project, release=release, author=author, assignee=user)
        assert issue_1.code == 'TT-1'

        issue_2 = IssueFactory(project=project, release=release, author=author, assignee=user)
        assert issue_2.code == 'TT-2'

        issue_1.title = 'new title'
        issue_1.save()

        assert issue_1.code == 'TT-1'
