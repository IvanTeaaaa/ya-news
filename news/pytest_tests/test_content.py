from datetime import timedelta

import pytest

from pytest_lazyfixture import lazy_fixture as lf

from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from news.forms import CommentForm
from news.models import Comment


@pytest.mark.django_db
def test_news_count(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.django_db
def test_news_order(client, news_list):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


@pytest.mark.django_db
def test_comments_order(client, author, news):
    now = timezone.now()
    for index in range(10):
        comment = Comment.objects.create(
            news=news,
            author=author,
            text=f'Комментарий {index}'
        )
        comment.created = now + timedelta(days=index)
        comment.save()
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news_obj = response.context['news']
    comments = news_obj.comment_set.all()
    timestamps = [comment.created for comment in comments]
    assert timestamps == sorted(timestamps)


@pytest.mark.parametrize(
    'parametrized_client, form_in_context',
    (
        (lf('client'), False),
        (lf('author_client'), True),
    )
)
@pytest.mark.django_db
def test_comment_form_availability(
    parametrized_client,
    form_in_context,
    news
):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    if form_in_context:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
