import pytest
from pytest_django.asserts import assertQuerySetEqual

from server.apps.issues.models import Project
from server.apps.issues.services import ProjectService
from server.apps.issues.tests.factories import IssueFactory, ProjectFactory


@pytest.mark.django_db()
class TestProjectServiceGetProjectInfo:
    """Testing method get_project_info of ProjectService."""

    def test_project_exist(self, project):
        """Project exists."""
        result = ProjectService.get_project_info(project.id)

        assert result['title'] == project.title
        assert result['code'] == project.code
        assert result['description'] == project.description
        assert result['owner_id'] == project.owner_id
        assertQuerySetEqual(result['issues'], [])

    def test_project_exist_with_issues(self, project):
        """Project has issues."""
        issue = IssueFactory(project=project)

        result = ProjectService.get_project_info(project.id)

        assert result['title'] == project.title
        assert result['code'] == project.code
        assert result['description'] == project.description
        assert result['owner_id'] == project.owner_id
        assertQuerySetEqual(result['issues'], [issue], ordered=False)

    def test_no_project(self):
        """Project does not exist."""
        with pytest.raises(ProjectService.ProjectNotFoundError):
            ProjectService.get_project_info(9999)


@pytest.mark.django_db()
class TestProjectServiceCreate:
    """Testing method create of ProjectService."""

    def test_success(self, user):
        """Success project creation."""
        assert Project.objects.all().count() == 0
        ProjectService.create(
            title='test_title',
            code='TT',
            description='test_project',
            owner=user,
        )
        project = Project.objects.get(title='test_title')

        assert Project.objects.all().count() == 1
        assert project.code == 'TT'
        assert project.description == 'test_project'
        assert project.owner == user

    @pytest.mark.parametrize(('title', 'code'), [
        ('test_project', 'new_code'),
        ('new_title', 'TT'),
    ])
    def test_unique_fields_error(self, project, title, code, user):
        """Project with provided fields already exists."""
        assert Project.objects.all().count() == 1
        with pytest.raises(ProjectService.ProjectAlreadyExist):
            ProjectService.create(
                title=title,
                code=code,
                description='test_description',
                owner=user,
            )

        assert Project.objects.all().count() == 1


@pytest.mark.django_db()
class TestProjectServiceUpdate:
    """Testing method update of ProjectService."""

    def test_success(self, project):
        """Success updating."""
        ProjectService.update(
            project=project,
            title='new_title',
            code='NT',
            description='new_description',
        )
        project.refresh_from_db()

        assert project.title == 'new_title'
        assert project.code == 'NT'
        assert project.description == 'new_description'

    def test_unique_fields_error(self, project):
        """Project with provided fields already exist."""
        ProjectFactory(title='another_title', code='another_code')
        with pytest.raises(ProjectService.ProjectAlreadyExist):
            ProjectService.update(
                project=project,
                title='another_title',
                code='another_code',
            )
