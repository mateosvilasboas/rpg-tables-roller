from http import HTTPStatus

from project.schemas import UserPublic


def test_create_users(client):
    response = client.post(
        '/users/',
        json={
            'name': 'alice',
            'email': 'alice@example.com',
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'name': 'alice',
        'email': 'alice@example.com',
        'id': 1,
    }


def test_get_users(client):
    response = client.get(
        'users',
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == {'users': []}


def test_get_users_with_users(client, user):
    print(user)
    users_schema = UserPublic.model_validate(user).model_dump()

    response = client.get('/users/')

    assert response.json() == {'users': [users_schema]}


def test_update_user(client, user):
    response = client.put(
        f'/users/{user.id}',
        json={'name': 'teste da silva', 'email': 'teste@teste.com'},
    )

    assert response.status_code == HTTPStatus.OK


def test_update_user_integrity_error(client, user, other_user):
    client.post(
        '/users/',
        json={'name': 'outro teste', 'email': 'outroteste@teste.com'},
    )

    response = client.put(
        f'/users/{user.id}',
        json={'name': 'teste da silva', 'email': 'outroteste@teste.com'},
    )

    assert response.status_code == HTTPStatus.CONFLICT


def test_delete_user(client, user):
    response = client.delete(f'/users/{user.id}')

    assert response.status_code == HTTPStatus.OK
