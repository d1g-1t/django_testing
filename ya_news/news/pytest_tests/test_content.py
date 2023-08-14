from http import HTTPStatus

import pytest

from django.conf import settings
from django.urls import reverse

from news.models import News, Comment


@pytest.mark.usefixtures('all_news')
@pytest.mark.django_db
class TestNews:
    HOME_PAGE = reverse('news:home')

    def test_news_publication_count(self, client):
        """Проверяем, что количество публикаций новостей"""
        """на странице не превышает десяти"""
        response = client.get(self.HOME_PAGE)
        assert response.status_code == HTTPStatus.OK
        object_list = response.context['object_list']
        assert len(object_list) == settings.NEWS_COUNT_ON_HOME_PAGE

    def test_news_publications_are_sorted_by_date(self, client):
        """Проверям, что новости отображаются от новых к старым"""
        response = client.get(self.HOME_PAGE)
        assert response.status_code == HTTPStatus.OK
        object_list = list(response.context['object_list'])
        sorted_objects_from_db = News.objects.order_by(
            '-date')[:settings.NEWS_COUNT_ON_HOME_PAGE]
        assert object_list == list(sorted_objects_from_db)


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
class TestComments:
    NEWS_PAGE_DETAIL = 'news:detail'

    def test_comments_are_sorted_by_date(self, client, comments, news_pk):
        """Проверям отображение комментариев от новых к старым"""
        sorted_comments_from_db = Comment.objects.filter(news=news_pk
                                                         ).order_by('created')
        url = reverse(self.NEWS_PAGE_DETAIL, args=[news_pk[0]])
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        all_comments = list(response.context['object'].comment_set.all())
        assert all_comments == list(sorted_comments_from_db)

    def test_form_not_available_for_unauthorized_user(self, client, news_pk):
        """Проверяем, что форма комментариев для неавторизированного"""
        """пользователя не доступна"""
        url = reverse(self.NEWS_PAGE_DETAIL, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert 'form' not in response.context
