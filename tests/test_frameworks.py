from http import HTTPStatus

from project.schemas import FrameworkPublic


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


def test_get_framework_by_id(client, framework, token):
    framework_schema = FrameworkPublic.model_validate(framework).model_dump()

    response = client.get(
        f'/frameworks/{framework.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.OK
    assert response.json() == framework_schema


def test_get_framework_by_id_not_found(client, token):
    response = client.get(
        '/frameworks/666',  # id does not belong to token's user
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == HTTPStatus.NOT_FOUND
    assert response.json() == {'detail': 'Framework not found'}
