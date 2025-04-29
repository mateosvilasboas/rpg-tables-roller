from http import HTTPStatus

from project.schemas import FrameworkPublic


def test_create_framework(client, token):
    response = client.post(
        '/frameworks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'framework',
            'entries': {
                'line_0': 'value 1',
                'line_1': 'value 2',
                'line_2': 'value 3',
                'line_3': 'value 4',
            },
        },
    )

    assert response.status_code == HTTPStatus.CREATED
    assert response.json() == {
        'id': 1,
        'name': 'framework',
        'entries': {
            'line_0': 'value 1',
            'line_1': 'value 2',
            'line_2': 'value 3',
            'line_3': 'value 4',
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


def test_create_framework_wrong_line(client, token):
    response = client.post(
        '/frameworks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'framework',
            'entries': {
                'line_0': 'data',
                'line_1': 'data',
                'wrong_line': 'data',
            },
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': "The following keys do not follow 'line X' pattern: "
        'wrong_line'
    }


def test_create_framework_wrong_numbers(client, token):
    response = client.post(
        '/frameworks/',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'name': 'framework',
            'entries': {
                'line_0': 'data',
                'line_1': 'data',
                'line_2': 'data',
                'line_4': 'data',
                'line_6': 'data',
                'line_3': 'data',
            },
        },
    )

    assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
    assert response.json() == {
        'detail': 'Line numbers in dict keys are not sequencial and/or not ordered'  # noqa
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
