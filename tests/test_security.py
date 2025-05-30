from http import HTTPStatus

from jwt import decode

from project.config import settings
from project.security.auth import (
    create_access_token,
)


def test_jwt():
    data = {'test': 'test'}
    token = create_access_token(data)

    decoded = decode(
        token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
    )

    assert decoded['test'] == 'test'
    assert 'exp' in decoded


def test_jwt_invalid_token(client):
    response = client.delete(
        '/users/', headers={'Authorization': 'Bearer invalid-token'}
    )

    assert response.status_code == HTTPStatus.UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
