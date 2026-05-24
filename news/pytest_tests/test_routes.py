from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_lazyfixture import lazy_fixture as lf
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
def test_home_availability_for_anonymous_user(client):
    url = reverse('news:home')
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_detail_availability_for_anonymous_user(client, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'name',
    ('users:login', 'users:signup')
)
def test_auth_pages_availability(client, name):
    url = reverse(name)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


def test_logout_availability(client):
    url = reverse('users:logout')
    response = client.post(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'parametrized_client, expected_status',
    (
        (lf('author_client'), HTTPStatus.OK),
        (lf('reader_client'), HTTPStatus.NOT_FOUND),
    )
)
@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_comment_edit_delete_availability(
        parametrized_client, name, comment, expected_status
):
    url = reverse(name, args=(comment.id,))
    response = parametrized_client.get(url)
    assert response.status_code == expected_status


@pytest.mark.parametrize(
    'name',
    ('news:edit', 'news:delete'),
)
def test_redirect_for_anonymous_client(client, name, comment):
    login_url = reverse('users:login')
    url = reverse(name, args=(comment.id,))
    expected_url = f'{login_url}?next={url}'
    response = client.get(url)
    assertRedirects(response, expected_url)
