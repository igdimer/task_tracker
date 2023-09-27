import datetime

import pytest

from server.apps.issues.models import Release
from server.apps.issues.services import ReleaseService
from server.apps.issues.tests.factories import ReleaseFactory


@pytest.mark.django_db()
class TestReleaseServiceGetById:
    """Testing method get_by_id of ReleaseService."""

    def test_release_exist(self, release):
        """Release exists."""
        ReleaseFactory()
        result_release = ReleaseService.get_by_id(release.id)

        assert result_release.version == release.version
        assert result_release.description == release.description
        assert result_release.release_date == release.release_date
        assert result_release.status == release.status

    def test_release_not_found(self):
        """Release does not exist."""
        with pytest.raises(ReleaseService.ReleaseNotFoundError):
            ReleaseService.get_by_id(release_id=999)


@pytest.mark.django_db()
class TestReleaseServiceCreate:
    """Testing method create of ReleaseService."""

    @pytest.mark.parametrize('release_date', [datetime.date(2024, 3, 20), None])
    def test_success_creation(self, project, release_date):
        """Success creation."""
        assert Release.objects.all().count() == 0
        ReleaseService.create(
            project=project,
            description='New Release',
            release_date=release_date,
            version='1.0.0',
        )
        release = Release.objects.get(version='1.0.0', project=project)

        assert Release.objects.all().count() == 1
        assert release.description == 'New Release'
        assert release.release_date == release_date
        assert release.status == 'unreleased'

    def test_project_version_unique(self, project, release):
        """Project already has release with the same version."""
        with pytest.raises(ReleaseService.ReleaseAlreadyExist):
            ReleaseService.create(
                project=project,
                version='0.1.0',
                description='New Release',
                release_date=datetime.date(2024, 3, 20),
            )


@pytest.mark.django_db()
class TestReleaseServiceUpdate:
    """Testing method update of ReleaseService."""

    def test_success_updating(self, release):
        """Success updating."""
        ReleaseService.update(
            release=release,
            version='3.0.0',
            description='New Release with new features.',
            release_date=datetime.date(2024, 3, 20),
            status='released',
        )

        release.refresh_from_db()
        assert release.version == '3.0.0'
        assert release.description == 'New Release with new features.'
        assert release.release_date == datetime.date(2024, 3, 20)
        assert release.status == 'released'

    def test_release_already_exist(self, release, project):
        """Project already has release with the same version."""
        ReleaseFactory(project=project, version='2.0.0')
        with pytest.raises(ReleaseService.ReleaseAlreadyExist):
            ReleaseService.update(
                release=release,
                version='2.0.0',
            )
