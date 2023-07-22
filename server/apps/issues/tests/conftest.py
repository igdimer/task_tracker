import pytest

from .factories import ProjectFactory, ReleaseFactory


@pytest.fixture()
def project():
    """Project fixture."""
    return ProjectFactory(title='test_project', code='TT')


@pytest.fixture()
def release(project):
    """Release fixture."""
    return ReleaseFactory(project=project, version='0.1.0')
