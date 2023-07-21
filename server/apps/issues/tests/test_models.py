import datetime

import pytest

from ..enums import IssueStatusEnum
from .factories import IssueFactory, ReleaseFactory


@pytest.mark.django_db()
class TestIssueModel:
    """Testing methods of model Issue."""

    def test_save(self, project):
        """Check save method with setting 'code'."""
        release = ReleaseFactory(version='0.1.0')
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
