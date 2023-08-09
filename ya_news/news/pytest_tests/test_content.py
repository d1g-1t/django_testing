from http import HTTPStatus

import pytest

from django.conf import settings
from django.urls import reverse


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
        sorted_objects = sorted(
            object_list,
            key=lambda x: x.date,
            reverse=True
        )
        assert object_list == sorted_objects


@pytest.mark.usefixtures('news')
@pytest.mark.django_db
class TestComments:
    NEWS_PAGE_DETAIL = 'news:detail'

    def test_comments_are_sorted_by_date(self, client, comments, news_pk):
        """Проверям отображение комментариев от новых к старым"""
        url = reverse(self.NEWS_PAGE_DETAIL, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        all_comments = list(response.context['object'].comment_set.all())
        sorted_comments_by_date = sorted(all_comments, key=lambda x: x.created)
        assert all_comments == sorted_comments_by_date

    def test_form_not_available_for_unauthorized_user(self, client, news_pk):
        """Проверяем, что форма комментариев для неавторизированного"""
        """пользователя не доступна"""
        url = reverse(self.NEWS_PAGE_DETAIL, args=news_pk)
        response = client.get(url)
        assert response.status_code == HTTPStatus.OK
        assert 'form' not in response.context
