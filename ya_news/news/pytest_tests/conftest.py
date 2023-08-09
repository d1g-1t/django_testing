from django.conf import settings
from django.utils.timezone import now

from news.models import Comment, News

import pytest

from datetime import timedelta


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    news = News.objects.create(
        title='Заголовок',
        text='Текст новости'
    )
    return news


@pytest.fixture
def news_pk(news):
    return news.pk,


@pytest.fixture
def all_news():
    all_news = [
        News(
            title='Заголовок',
            text='Текст новости',
            date=now() - timedelta(days=index)
        ) for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(all_news)


@pytest.fixture
def comment(news, author):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст комментария'
    )


@pytest.fixture
def comment_pk(comment):
    return comment.pk,


@pytest.fixture
def comments(news, author):
    comments = [
        Comment(
            news=news,
            author=author,
            text='Текст комментария',
            created=now() - timedelta(days=index)
        ) for index in range(2)
    ]
    return Comment.objects.bulk_create(comments)


@pytest.fixture
def form_data():
    return {
        'text': 'Комментарий'
    }
