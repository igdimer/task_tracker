from unittest import mock

import pytest


@pytest.fixture()
def mock_jwt_encode():
    """Mock fixture jwt.encode."""
    with mock.patch('jwt.encode') as mock_encode:
        mock_encode.side_effect = ['first_token', 'second_token']
        yield mock_encode
