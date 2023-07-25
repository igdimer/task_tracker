import pytest

from server.apps.issues.models import Comment
from server.apps.issues.services import CommentService, IssueService
from server.apps.users.tests.factories import UserFactory

from ..factories import CommentFactory, IssueFactory


@pytest.mark.django_db()
class TestCommentServiceCreate:
    """Testing method create of CommentService."""

    def test_success(self, issue, user):
        """Success creation comment."""
        assert Comment.objects.all().count() == 0
        CommentService.create(issue_id=issue.id, author=user, text='test_text')
        comment = Comment.objects.get(issue=issue)

        assert Comment.objects.all().count() == 1
        assert comment.author == user
        assert comment.text == 'test_text'

    def test_issue_not_found(self, user):
        """Issue not found."""
        assert Comment.objects.all().count() == 0
        with pytest.raises(IssueService.IssueNotFoundError):
            CommentService.create(issue_id=999, author=user, text='test_text')

        assert Comment.objects.all().count() == 0


@pytest.mark.django_db()
class TestCommentServiceGetById:
    """Testing method get_by_id of CommentService."""

    def test_success(self, comment):
        """Success getting comment."""
        result_comment = CommentService.get_by_id(
            issue_id=comment.issue_id,
            comment_id=comment.id,
        )
        assert result_comment.text == 'test_text'

    def test_comment_not_found(self, issue):
        """Comment not found."""
        with pytest.raises(CommentService.CommentNotFoundError):
            CommentService.get_by_id(issue_id=issue.id, comment_id=999)

    def test_issue_not_found(self):
        """Issue not found."""
        with pytest.raises(IssueService.IssueNotFoundError):
            CommentService.get_by_id(issue_id=999, comment_id=999)


@pytest.mark.django_db()
class TestCommentServiceUpdate:
    """Testing method get_by_id of CommentService."""

    def test_success(self, comment):
        """Success updating comment."""
        assert comment.text == 'test_text'
        CommentService.update(issue_id=comment.issue_id, comment_id=comment.id, text='new_text')
        comment.refresh_from_db()

        assert comment.text == 'new_text'

    def test_comment_not_found(self, issue):
        """Comment not found."""
        with pytest.raises(CommentService.CommentNotFoundError):
            CommentService.update(issue_id=issue.id, comment_id=999, text='new_text')

    def test_issue_not_found(self):
        """Issue not found."""
        with pytest.raises(IssueService.IssueNotFoundError):
            CommentService.update(issue_id=999, comment_id=999, text='new_text')


@pytest.mark.django_db()
class TestCommentServiceList:
    """Testing method list of CommentService."""

    def test_success(self, issue):
        """Success getting list of comments."""
        comment_1 = CommentFactory(issue=issue, author=issue.assignee)
        comment_2 = CommentFactory(issue=issue, author=issue.assignee)
        another_user = UserFactory(email='another@email.com')
        CommentFactory(issue=IssueFactory(assignee=another_user, author=another_user))

        result = CommentService.get_list(issue_id=issue.id)

        assert result.count() == 2
        assert result[0] == comment_1
        assert result[1] == comment_2

    def test_empty_list(self, issue):
        """Issue has no comments."""
        another_user = UserFactory(email='another@email.com')
        CommentFactory(issue=IssueFactory(assignee=another_user, author=another_user))

        result = CommentService.get_list(issue_id=issue.id)

        assert result.count() == 0

    def test_issue_not_found(self):
        """Issue not found."""
        with pytest.raises(IssueService.IssueNotFoundError):
            CommentService.get_list(999)
