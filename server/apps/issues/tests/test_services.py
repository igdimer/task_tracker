import pytest

from ..models import Project
from ..services import ProjectService
from .factories import IssueFactory, ProjectFactory


@pytest.mark.django_db()
class TestProjectServiceGetById:
    """Testing method get_by_id of ProjectService."""

    def test_project_exist(self, project):
        """Project exists."""
        result = ProjectService.get_by_id(project.id)

        assert result == {
            'title': project.title,
            'code': project.code,
            'description': project.description,
            'issues': [],
        }

    def test_project_exist_with_issues(self, project):
        """Project has issues."""
        issue = IssueFactory(project=project)

        result = ProjectService.get_by_id(project.id)

        assert result == {
            'title': project.title,
            'code': project.code,
            'description': project.description,
            'issues': [
                {
                    'title': issue.title,
                    'code': issue.code,
                    'status': issue.status,
                    'release': issue.release.version,
                    'assignee': issue.assignee.id,
                },
            ],
        }

    def test_no_project(self):
        """Project does not exist."""
        with pytest.raises(ProjectService.ProjectNotFoundError):
            ProjectService.get_by_id(9999)


@pytest.mark.django_db()
class TestProjectServiceCreate:
    """Testing method create of ProjectService."""

    def test_success(self):
        """Success project creation."""
        assert Project.objects.all().count() == 0
        ProjectService.create(title='test_title', code='TT', description='test_project')
        project = Project.objects.get(title='test_title')

        assert Project.objects.all().count() == 1
        assert project.code == 'TT'
        assert project.description == 'test_project'

    @pytest.mark.parametrize(('title', 'code'), [
        ('test_project', 'new_code'),
        ('new_title', 'TT'),
    ])
    def test_unique_fields_error(self, project, title, code):
        """Project with provided fields already exists."""
        assert Project.objects.all().count() == 1
        with pytest.raises(ProjectService.UniqueFieldsError):
            ProjectService.create(title=title, code=code, description='test_description')

        assert Project.objects.all().count() == 1


@pytest.mark.django_db()
class TestProjectServiceUpdate:
    """Testing method update of ProjectService."""

    def test_success(self, project):
        """Success updating."""
        ProjectService.update(
            project_id=project.id,
            title='new_title',
            code='NT',
            description='new_description',
        )
        project.refresh_from_db()

        assert project.title == 'new_title'
        assert project.code == 'NT'
        assert project.description == 'new_description'

    def test_no_project(self):
        """Updating project does not exist."""
        with pytest.raises(ProjectService.ProjectNotFoundError):
            ProjectService.update(
                project_id=999,
                title='new_title',
                code='NT',
                description='new_description',
            )

    def test_unique_fields_error(self, project):
        """Project with provided fields already exist."""
        ProjectFactory(title='another_title', code='another_code')
        with pytest.raises(ProjectService.UniqueFieldsError):
            ProjectService.update(
                project_id=project.id,
                title='another_title',
                code='another_code',
            )
