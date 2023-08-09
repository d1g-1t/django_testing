from http import HTTPStatus

import pytest

from django.urls import reverse

from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:home', None),
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
        ('news:detail', pytest.lazy_fixture('news_pk'))
    )
)
def test_availability_of_pages_for_unauthorized_user(client, name, args):
    """Проверяем доступность страниц для неавторизированного пользователя"""
    url = reverse(name, args=args)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


"""Проверяем возможность редактирования и удаления комментариев"""


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_pk')),
        ('news:delete', pytest.lazy_fixture('comment_pk'))
    )
)
class TestComments:
    """Проверяем, что неавторизированный пользователь не может"""
    """редактировать или удалять комментарии"""
    @pytest.mark.django_db
    def test_unauthorized_user_cant_edit_or_delete_his_comments(
            self, client, name, args
    ):
        url = reverse(name, args=args)
        login_url = reverse('users:login')
        expected_redirect_url = f'{login_url}?next={url}'
        response = client.get(url)
        assertRedirects(response, expected_redirect_url)

    """Проверяем доступность страниц дла разных пользователей"""
    @pytest.mark.parametrize(
        'parametrized_client, expected_status',
        (
            (pytest.lazy_fixture('admin_client'), HTTPStatus.NOT_FOUND),
            (pytest.lazy_fixture('author_client'), HTTPStatus.OK)
        ),
    )
    def test_availability_of_pages_for_user_category(
            self, parametrized_client, expected_status, name, args
    ):
        url = reverse(name, args=args)
        response = parametrized_client.get(url)
        assert response.status_code == expected_status
