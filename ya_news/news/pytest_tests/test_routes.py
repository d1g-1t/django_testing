import pytest

from datetime import datetime

from http import HTTPStatus

from django.contrib.auth.models import User

from news.models import News, Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url',
    (
        '/',
        '/auth/signup/',
        '/auth/login/',
        '/auth/logout/',
    )
)
def test_availability_of_pages_for_unauthorized_user(client, url):
    """Проверяем доступность страниц для неавторизированного пользователя"""
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_availability_of_news_page_for_unathorized_user(client):
    """Проверяем доступность страницы отдельной"""
    """"новости для анонимного пользователя"""
    news = News.objects.create(
        title='Test News',
        text='Test News Text',
        date=datetime.today()
    )
    news_url = f'/news/{news.id}/'
    response = client.get(news_url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.django_db
def test_author_can_edir_or_delete_his_comments(client):
    """Проверяем редактирование и удаление комментария автором"""
    user = User.objects.create_user(
        username='testuser',
        password='testpassword'
    )
    news = News.objects.create(
        title='Test News',
        text='Test News Text',
        date=datetime.today()
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Test Comment'
    )
    delete_url = f'/delete_comment/{comment.id}/'
    delete_response = client.get(delete_url)
    assert delete_response.status_code == HTTPStatus.FOUND
    delete_response = client.post(delete_url, follow=True)
    assert delete_response.status_code == HTTPStatus.OK
    assert Comment.objects.filter(id=comment.id).exists() is True


@pytest.mark.django_db
def test_unauthorized_user_cant_edit_or_delete_his_comments(client):
    """Проверяем, что анонимный пользователь перенаправляется на страницу"""
    """авторизации при попытке редактирования или удаления комментария"""
    user = User.objects.create_user(
        username='testuser',
        password='testpassword'
    )
    news = News.objects.create(
        title='Test News',
        text='Test News Text',
        date=datetime.today()
    )
    comment = Comment.objects.create(
        news=news,
        author=user,
        text='Test Comment'
    )
    edit_url = f'/edit_comment/{comment.id}/'
    edit_response = client.get(edit_url, follow=True)
    assert edit_response.status_code == HTTPStatus.OK
    delete_url = f'/delete_comment/{comment.id}/'
    delete_response = client.get(delete_url, follow=True)
    assert delete_response.status_code == HTTPStatus.OK
    assert b"login" in edit_response.content.lower()
    assert b"login" in delete_response.content.lower()


@pytest.mark.django_db
def test_user_cannot_modify_other_comments(client):
    """Проверяем, что пользователь не может редактировать"""
    """или удалять чужие комментарии"""
    other_user = User.objects.create_user(
        username='otheruser',
        password='testpassword'
    )
    news = News.objects.create(
        title='Test News',
        text='Test News Text',
        date=datetime.today()
    )
    test_comment = Comment.objects.create(
        news=news,
        author=other_user,
        text='Test Comment'
    )
    edit_url = f'/edit_comment/{test_comment.id}/'
    edit_response = client.get(edit_url, follow=True)
    assert edit_response.status_code == HTTPStatus.OK
    delete_url = f'/delete_comment/{test_comment.id}/'
    delete_response = client.get(delete_url, follow=True)
    assert delete_response.status_code == HTTPStatus.OK
