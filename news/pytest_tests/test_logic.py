from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError

from django.urls import reverse

from news.forms import BAD_WORDS, WARNING
from news.models import Comment

import pytest


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, news, form_data):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_authorized_user_can_create_comment(
    author_client,
    author,
    news,
    form_data
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_user_cant_use_bad_words(author_client, news):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Текст {BAD_WORDS[0]} текст'}
    response = author_client.post(url, data=bad_words_data)
    form = response.context['form']
    assertFormError(form, 'text', WARNING)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(author_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_data = {'text': 'Обновлённый комментарий'}
    response = author_client.post(url, data=new_data)
    expected_url = (
        reverse('news:detail', args=(comment.news.id,))
        + '#comments'
    )
    assertRedirects(response, expected_url)
    comment.refresh_from_db()
    assert comment.text == new_data['text']


def test_other_user_cant_edit_note(reader_client, comment):
    url = reverse('news:edit', args=(comment.id,))
    new_data = {'text': 'Попытка взлома'}
    response = reader_client.post(url, data=new_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    assert comment.text == 'Текст комментария'


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(url)
    expected_url = (
        reverse('news:detail', args=(comment.news.id,))
        + '#comments'
    )
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_other_user_cant_delete_comment(reader_client, comment):
    url = reverse('news:delete', args=(comment.id,))
    response = reader_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1
