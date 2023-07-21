import pytest

from .factories import ProjectFactory


@pytest.fixture()
def project():
    """Project fixture."""
    return ProjectFactory(title='test_project', code='TT')
