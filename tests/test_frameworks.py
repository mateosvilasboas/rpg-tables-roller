from http import HTTPStatus


def test_create_framework(client, token):
    response = client.post(
        '/frameworks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'framework',
            'entries': {
                'key_1': 'value 1',
                'key_2': 'value 2',
                'key_3': 'value 3',
                'key_4': 'value 4',
            },
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'user_id': 1,
        'name': 'framework',
        'entries': {
            'key_1': 'value 1',
            'key_2': 'value 2',
            'key_3': 'value 3',
            'key_4': 'value 4',
        },
    }


def test_create_framework_no_entries(client, token):
    response = client.post(
        '/frameworks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'framework',
            'entries': {},
        },
    )

    assert response.status_code == HTTPStatus.BAD_REQUEST
    assert response.json() == {
        'detail': 'Framework must have at least one entry'
    }
