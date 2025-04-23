from http import HTTPStatus


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
